import sys
import random
import time
from rich import print, box
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
console = Console()

START_STONES = 4
RULES = '''
Let's play Mancala!  Mancala is played with a board that has 12 small wells, 6 for each player, that are initially

each filled with 4 stones.  There is also a larger well (called "mancala") for each player on their far right that starts empty.

Players alternate turns.  A turn consists of picking up all the stones in a well on the player's side of the board and

placing 1 stone in each well in sequence going counter-clockwise (to the right) until all stones are placed.  Stones placed in

the player's mancala count toward the players final score.  If a player puts a stone in their mancala and still has more stones

to place, they start placing them in the opponent's wells, going from right to left.  A player cannot place a stone in the

opponent's mancala.  Play continues until one player's side of the board has no stones left, at which point the other player

takes all of the stones on their side for their own mancala.  Whoever has the most stones in their mancala wins!

Special rule #1:  If a player's last stone placed on their turn is in their mancala, they take another turn.

Special rule #2:  If a player's last stone placed on their turn is in an empty well on their side and there are any stones in

the well on the opposite side, they put that stone along with all the stones in the opposite well into their own mancala.'''

def main():
    console.print(Panel('[bold bright white]' + RULES), justify='center')
    board = starting_board()
    ai_player = play_against_ai()
    turn = who_goes_first(ai_player)
    while True:
        display_board(board, turn)
        board, special = player_move(board, turn) # special refers to special rule 1, which when triggered gives another turn
        is_game_over(board, ai_player)
        turn = whose_turn(turn, special, ai_player)

def who_goes_first(ai_player):
    if ai_player:
        turn = int(random.choice('13')) # randomly select who starts, player 1 (1) or ai (3)
        if turn == 1:
            print('PLAYER 1 has been randomly selected to go first.')
            time.sleep(2)
        else:
            print('PLAYER 2 (COMPUTER) has been randomly selected to go first.')
            time.sleep(2)
    else:
        turn = int(random.choice('12')) # randomly select who starts, player 1 or player 2
        if turn == 1:
            print('PLAYER 1 has been randomly selected to go first.')
            time.sleep(2)
        else:
            print('PLAYER 2 has been randomly selected to go first.')
            time.sleep(2)
    return turn

def play_against_ai():
    while True:
        choice = input('Do you want to play against the computer 💻 (Y or N)?')
        if choice == 'Y' or choice == 'y':
            return True
        elif choice == 'N' or choice == 'n':
            return False
        print('Please enter Y or N.')

# Creates the starting board in a list, all wells hold number of stones = START_STONES (except the end wells which are set to 0)
def starting_board():
    board = [0]
    starter = [START_STONES]
    for i in range(13):
        board += starter
    board[13] = 0
    return board

def player_move(board, turn):
    if turn == 3: # first check if it is ai's turn
        board, special = ai_turn(board, turn)
        return board, special
    well_choice = is_valid_choice(turn)
    while board[well_choice] == 0:
        print('There are no stones in that well.')
        well_choice = is_valid_choice(turn)
    board, special = move_stones(well_choice, board, turn)
    print('RESULT:')
    display_board(board, turn)
    input('(Press Enter to continue...)')
    return board, special

def is_valid_choice(turn):
    while True:
        try:
            if turn == 1:
                well_choice = int(input('Enter the number of the well you want to take the stones from (1 - 6): '))
                if well_choice in range(1, 7):
                    return well_choice
            if turn == 2:
                well_choice = int(input('Enter the number of the well you want to take the stones from (7 - 12): '))
                if well_choice in range(7, 13):
                    return well_choice
        except ValueError:
            print('That\'s not a number.')
            continue
        print('Try again please.  For PLAYER 1 valid input is a number 1 through 6, for PLAYER 2 a number 7 through 12.')

def move_stones(well_choice, board, turn):
    if turn == 1:
        board, special = player_one_placement(well_choice, board)
        return board, special
    else:
        board, special = player_two_placement(well_choice, board)
        return board, special

def ai_turn(board, turn):
    well_choice = ai_logic(board)
    stones_in_hand = board[well_choice]
    board[well_choice] = 0
    counter = well_choice
    special = 0
    while stones_in_hand > 0:
            if counter == 12:
                board[13] += 1
                stones_in_hand -= 1
                counter = 0 # This will cause the counter to wrap around back to well number one
                if stones_in_hand == 0:
                    special = 3 # this means computer has triggered special rule 1 and can take another turn
            if stones_in_hand > 0:
                board[counter + 1] += 1  # this adds 1 stone to the well to the right of the chosen well
                counter += 1  # this sets well_choice one well to the right so we can iterate off of that
                stones_in_hand -= 1
    if counter in range(7, 13) and board[counter] == 1:
        board = special_rule_2(board, counter)
    print('RESULT (COMPUTER played ' + str(well_choice) + '):')
    display_board(board, turn)
    with console.status('This is how PLAYER 2 (COMPUTER) played, press ENTER to continue...', spinner='clock'):
        input()
    return board, special

def ai_logic(board):
    placeholder = board[13] # sets a baseline for the number of stones in ai's end well
    for well_choice in range(7, 13):
        sim_board = board[:]
        stones_in_hand = sim_board[well_choice]
        if sim_board[well_choice] == 0: #  this prevents ai from choosing a well that has zero stones
            sim_board[13] = -9999 #  by giving those wells a very negative weight
        sim_board[well_choice] = 0
        counter = well_choice
        special = 0
        while stones_in_hand > 0:
            if counter == 12:
                sim_board[13] += 1
                stones_in_hand -= 1
                counter = 0 # This will cause the counter to wrap around back to well number one
                if stones_in_hand == 0: # TRY TO MAKE THIS TRIGGER ANOTHER SIMULATED TURN? *******************************
                    #special = 3 # this means computer has triggered special rule 1 and can take another turn
                    sim_board[13] += 1 # this causes computer to weigh moves that give another turn more heavily by 1 stone
            if stones_in_hand > 0:
                sim_board[counter + 1] += 1  # this adds 1 stone to the well to the right of the chosen well
                counter += 1  # this sets well_choice one well to the right so we can iterate off of that
                stones_in_hand -= 1
        if counter in range(7, 13) and sim_board[counter] == 1:
            sim_board = ai_special_rule_2(sim_board, counter)
        if sim_board[13] >= placeholder:
            placeholder = sim_board[13]
            best_choice = well_choice
    return best_choice

def player_one_placement(well_choice, board):
    stones_in_hand = board[well_choice]
    board[well_choice] = 0 # empty the well player took stones from
    counter = well_choice
    special = 0 # this is initially 0, will change to 1 if player 1 triggers special rule 1
    while stones_in_hand > 0:
        if counter == 6:
            board[0] += 1
            stones_in_hand -= 1
            if stones_in_hand == 0:
                counter += 1 # this is to avoid accidentally triggering special rule 2 later in this func
                special = 1 # this means player 1 has triggered special rule 1 and can take another turn
        if stones_in_hand > 0:
            board[counter + 1] += 1  # this adds 1 stone to the well to the right of the chosen well
            counter += 1  # this sets well_choice one well to the right so we can iterate off of that
            stones_in_hand -= 1
            if counter == 12:
                counter = 0 # this will cause the counter to wrap around back to well number one
    # Now checks if last stone placed was on own side, and if it is only stone in well (which means well was empty before that)
    if counter in range(1, 7) and board[counter] == 1:
        board = special_rule_2(board, counter)
    return board, special

def player_two_placement(well_choice, board):
    stones_in_hand = board[well_choice]
    board[well_choice] = 0
    counter = well_choice
    special = 0 # this is initially 0, will change to 2 if player 2 triggers special rule 1
    while stones_in_hand > 0:
        if counter == 12:
            board[13] += 1
            stones_in_hand -= 1
            counter = 0 # This will cause the counter to wrap around back to well number one
            if stones_in_hand == 0:
                special = 2 # this means player 2 has triggered special rule 1 and can take another turn
        if stones_in_hand > 0:
            board[counter + 1] += 1  # this adds 1 stone to the well to the right of the chosen well
            counter += 1  # this sets well_choice one well to the right so we can iterate off of that
            stones_in_hand -= 1
    if counter in range(7, 13) and board[counter] == 1:
        board = special_rule_2(board, counter)
    return board, special

def special_rule_2(board, counter):
    if board[13 - counter] > 0:  # this will check if the well on the opposite side of the last stone placed is empty
        captured_stones = board[13 - counter]
        board[13 - counter] = 0
        board[counter] = 0
        if counter in range(1, 7):
            board[0] += (captured_stones + 1) # puts the captured stones in player 1's end well, along with the last stone they played
            return board
        else:
            board[13] += (captured_stones + 1) # puts them in player 2's end well
            return board
    else:
        return board

def ai_special_rule_2(sim_board, counter):
    if sim_board[13 - counter] > 0:  # this will check if the well on the opposite side of the last stone placed is empty
        captured_stones = sim_board[13 - counter]
        sim_board[13 - counter] = 0
        sim_board[counter] = 0
        if counter in range(1, 7):
            sim_board[0] += (captured_stones + 1) # puts the captured stones in player 1's end well, along with the last stone they played
            return sim_board
        else:
            sim_board[13] += (captured_stones + 1) # puts them in player 2's end well
            return sim_board
    else:
        return sim_board

# If special rule 1 has been triggered by a player, they will get another turn.  Otherwise turns will alternate.        
def whose_turn(turn, special, ai_player):
    if special == 1:
        special = 0
        print('PLAYER 1 gets another turn!')
        return 1
    if special == 2:
        special = 0
        print('PLAYER 2 gets another turn!')
        return 2
    if special == 3:
        special = 0
        print('PLAYER 2 (COMPUTER) gets another turn!')
        return 3
    if ai_player:
        if turn == 1:
            return 3
        else:
            return 1
    else:
        if turn == 1:
            return 2
        else:
            return 1

def display_board(board, turn):
    if turn == 1:
        player_one_display(board, turn)
    else:
        if turn == 2:
            console.rule('[bold red]PLAYER 2\'s turn', align='left')
            player_two_display(board, turn)
        else:
            console.rule('[bold red]PLAYER 2 (COMPUTER)\'s turn', align='left')
            player_two_display(board, turn)
        
def player_one_display(board, turn):
    console.rule('[bold red]PLAYER 1\'s turn', align='left')
    table = Table(title='[italics]Mancala Board', show_lines='True', box=box.ROUNDED, style='black on rgb(95,55,0)')
    table.add_column('[cyan]PLAYER 2 End Well', justify='right', style='cyan', no_wrap=True)
    for i in range(12, 6, -1):
        table.add_column('[bold white]Well ' + str(i), style='white')
    table.add_column('[green]Player 1 End Well', justify='right', style='bold green')
    table.add_row(str(board[13]), str(board[12]), str(board[11]), str(board[10]), str(board[9]), str(board[8]), str(board[7]))
    table.add_row('', str(board[1]), str(board[2]), str(board[3]), str(board[4]), str(board[5]), str(board[6]), str(board[0]))
    table.add_row('Player 2 End Well', 'Well 1', 'Well 2', 'Well 3', 'Well 4', 'Well 5', 'Well 6', 'Player 1 End Well', style='bold white')
    console.print(Panel(table, expand=False))
    print('')

def player_two_display(board, turn):
    table = Table(title='Mancala Board', show_lines='True', box=box.ROUNDED, style='black on rgb(95,55,0)')
    table.add_column('[green]Player 1 End Well', justify='right', style='green', no_wrap=True)
    for i in range(6, 0, -1):
        table.add_column('[bold white]Well ' + str(i), style='white')
    table.add_column('[cyan]Player 2 End Well', justify='right', style='bold cyan')
    table.add_row(str(board[0]), str(board[6]), str(board[5]), str(board[4]), str(board[3]), str(board[2]), str(board[1]))
    table.add_row('', str(board[7]), str(board[8]), str(board[9]), str(board[10]), str(board[11]), str(board[12]), str(board[13]))
    table.add_row('Player 1 End Well', 'Well 7', 'Well 8', 'Well 9', 'Well 10', 'Well 11', 'Well 12', 'Player 2 End Well', style='bold white')
    console.print(Panel(table, expand=False), justify='center')
    print ('')

def is_game_over(board, ai_player):
    if sum(board[1:7]) == 0 or sum(board[7:13]) == 0:
        if sum(board[1:7]) == 0:
            board[13] += sum(board[7:13])
        if sum(board[7:13]) == 0:
            board[0] += sum(board[1:7])
        if board[0] > board[13]:
            print('PLAYER 1 wins,', board[0], '-', board[13], '!')
            sys.exit()
        elif board[0] == board[13]:
            print('It\'s a tie,', board[0], '-', board[13], '!')
            sys.exit()
        else:
            if ai_player:
                print('COMPUTER wins,', board[13], '-', board[0], '!')
                sys.exit()
            else:
                print('PLAYER 2 wins,', board[13], '-', board[0], '!')
                sys.exit()


if __name__ == '__main__':
    main()
