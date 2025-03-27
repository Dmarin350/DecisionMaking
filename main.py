import sys
import random

def read_board(file_name):
    # Reads the txt file we are given
    with open(file_name, 'r') as f:
        algorithm = f.readline().strip()
        player = f.readline().strip()
        board = [list(f.readline().strip()) for _ in range(6)]
    return algorithm, player, board

def get_legal_moves(board):
    # Checks to see if the top space at the top of a column has an empty space, making it a valid column
    valid_columns = []
    for col in range(7):
        if board[0][col] == '0':
            valid_columns.append(col)
    return valid_columns

def uniform_random_move(board):
    # Returns a random column to make a move, if no valid moves, returns None
    legal_moves = get_legal_moves(board)
    if legal_moves:
        return random.choice(legal_moves)
    else:
        return None

# TODO: Simulate a gmae
def simulate_game():
    input_file, verbosity, simulations = sys.argv[1], sys.argv[2], int(sys.argv[3])
    algorithm, player, board = read_board(input_file)

    for i in range(simulations):
        continue



def main():
    '''
    call simulate game
    '''
   
    
