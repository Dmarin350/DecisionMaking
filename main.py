import sys
import random

#Course: CS 5314: Decision Making
#Authors: Daniel Marin, Kevin Porras
#Last Revised: Mar 30, 2025

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
        if board[0][col] == 'O':
            valid_columns.append(col)
    return valid_columns

def uniform_random_move(board):
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
            if line[i] != 'O' and line[i] == line[i+1] == line[i+2] == line[i+3]:
                return line[i]
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
            if board[r][c] != 'O' and board[r][c] == board[r+1][c+1] == board[r+2][c+2] == board[r+3][c+3]:
                return board[r][c]
            
    # Check diagonal (top-left to bottom-right)
    for r in range(3, rows):
        for c in range(cols - 3):
            if board[r][c] != 'O' and board[r][c] == board[r-1][c+1] == board[r-2][c+2] == board[r-3][c+3]:
                return board[r][c]

    return None


def simulate_game():
    input_file, verbosity, simulations = sys.argv[1], sys.argv[2], int(sys.argv[3])
    algorithm, player, board = read_board(input_file)
    continue_game = True
    red_to_move = (player == 'R')

    while(continue_game):
        
        if algorithm == "UR":
            
            if simulations != 0:
                print("Error: UR algorithm requires simulation count to be 0.")
                sys.exit(1)
            
            move = uniform_random_move(board)
            if move is None:
                print("No valid moves left.")
                print("No winner")
                continue_game = False


            # Apply the move
            for row in range(len(board) - 1, -1, -1):
                if board[row][move] == 'O':
                    board[row][move] = 'R' if red_to_move else 'Y'
                    if red_to_move:
                        red_to_move = False
                    else:
                        red_to_move = True
                    break
    
            
            for row in board:
                print(" ".join(map(str, row)))

            if check_winner(board) == 'Y':
                print("Yellow is the winner")
                continue_game = False
            if check_winner(board) =='R':
                print("Red is the winner")
                continue_game = False

            # Print selected move
            print(f"FINAL Move selected: {move + 1}")

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 PA2.py <input_file> <verbosity> <simulations>")
        sys.exit(1)
    
    simulate_game()
if __name__ == "__main__":
    main()