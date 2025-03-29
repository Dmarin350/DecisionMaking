import sys
import random

def read_board(file_name):
    # Reads the txt file we are given
    with open(file_name, 'r') as f:
        print(f.readline().strip())
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

def check_winner(board):
    rows = len(board)
    cols = len(board[0])
    
    # Checks to see if a straight line has a winner
    def check_line(line):
        for i in range(len(line) - 3):
            if line[i] != 0 and line[i] == line[i+1] == line[i+2] == line[i+3]:
                return line[i]  # Return 'Y' or 'R'
        return None
    
    # Check horizontal
    for row in board:
        result = check_line(row)
        if result:
            return result
    
    # Check vertical
    for c in range(cols):
        column = [board[r][c] for r in range(rows)]
        result = check_line(column)
        if result:
            return result
    
    # Check diagonal (bottom-left to top-right)
    for r in range(rows - 3):
        for c in range(cols - 3):
            if board[r][c] != 0 and board[r][c] == board[r+1][c+1] == board[r+2][c+2] == board[r+3][c+3]:
                return board[r][c]

    # Check diagonal (top-left to bottom-right)
    for r in range(3, rows):
        for c in range(cols - 3):
            if board[r][c] != 0 and board[r][c] == board[r-1][c+1] == board[r-2][c+2] == board[r-3][c+3]:
                return board[r][c]
    
    # No winner
    return None  


def simulate_game():
    red_to_move = False
    input_file, verbosity, simulations = sys.argv[1], sys.argv[2], int(sys.argv[3])
    algorithm, player, board = read_board(input_file)

    if player == 'R':
        red_to_move = True
    
    for i in range(simulations):
        # Pick random move
        next_move = uniform_random_move

        # If theres no more moves, return the board
        if(next_move == None):
            return board
        else:
            # Go through the column of the move you chose, bottom to the top
            for i in range(len(board) - 1, -1, -1):
                if board[i][next_move] == '0':
                    if red_to_move:
                        board[i][next_move] = 'R'
                        red_to_move = False
                    else:
                       board[i][next_move] = 'Y' 
                       red_to_move = True
            
            
            # Check to see if theres a winner
            winner = check_winner(board)

            if winner:
                print(winner+" is the winner!")

    print("No winner :(")
            

def main():
    simulate_game()
   
    
