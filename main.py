import sys
import random
import copy
import math
import time
import csv
import os
import itertools
from collections import defaultdict

# Course: CS 5314: Decision Making
# Authors: Daniel Marin, Kevin Porras
# Last Revised: Apr 5, 2025
def clone_board(board):
    return [row[:] for row in board]

def read_board(file_name):
    with open(file_name, 'r') as f:
        algorithm = f.readline().strip()
        player = f.readline().strip()
        board = [list(f.readline().strip()) for _ in range(6)]
    return algorithm, player, board

def get_legal_moves(board):
    return [col for col in range(7) if board[0][col] == 'O']

def switch_player(player):
    return 'Y' if player == 'R' else 'R'

def uniform_random_move(board):
    legal_moves = get_legal_moves(board)
    return random.choice(legal_moves) if legal_moves else None

def simulate_random_game(board, current_player):
    while True:
        winner = check_winner(board)
        if winner:
            return winner
        if not get_legal_moves(board):
            return None
        move = uniform_random_move(board)
        for row in range(len(board) - 1, -1, -1):
            if board[row][move] == 'O':
                board[row][move] = current_player
                break
        current_player = switch_player(current_player)

def pmcgs_move(board, player, simulations, verbosity):
    legal_moves = get_legal_moves(board)
    move_stats = {}

    for move in legal_moves:
        win_sum, num_sims = 0, 0

        for _ in range(simulations):
            sim_board = clone_board(board)
            for row in range(len(sim_board) - 1, -1, -1):
                if sim_board[row][move] == 'O':
                    sim_board[row][move] = player
                    break

            if verbosity == "Verbose":
                print("NODE ADDED")

            rollout_moves = []
            current_player = switch_player(player)
            while True:
                winner = check_winner(sim_board)
                if winner or not get_legal_moves(sim_board):
                    break
                rollout_move = uniform_random_move(sim_board)
                rollout_moves.append(str(rollout_move + 1))
                for row in range(len(sim_board) - 1, -1, -1):
                    if sim_board[row][rollout_move] == 'O':
                        sim_board[row][rollout_move] = current_player
                        break
                current_player = switch_player(current_player)

            winner = check_winner(sim_board)
            if winner == player:
                result = 1
            elif winner == switch_player(player):
                result = -1
            else:
                result = 0

            win_sum += result
            num_sims += 1

            if verbosity == "Verbose":
                for m in rollout_moves:
                    print(f"Move selected: {m}")
                print(f"TERMINAL NODE VALUE: {result}")
                print("Updated values:")
                print(f"wi: {win_sum}")
                print(f"ni: {num_sims}\n")

        move_stats[move] = (win_sum, num_sims)

        if verbosity == "Verbose":
            print(f"wi: {win_sum}")
            print(f"ni: {num_sims}")
            print(f"Move simulated: {move + 1}\n")

    best_move = max(move_stats, key=lambda m: move_stats[m][0] / move_stats[m][1])

    if verbosity == "Verbose":
        print("Column values:")
        for m in range(7):
            if m in move_stats:
                avg = move_stats[m][0] / move_stats[m][1]
                print(f"Column {m + 1}: {round(avg, 2)}")
            else:
                print(f"Column {m + 1}: Null")

    return best_move

def uct_move(board, player, simulations, verbosity):
    legal_moves = get_legal_moves(board)
    stats = {move: [0, 0] for move in legal_moves}
    C = math.sqrt(2)

    for _ in range(simulations):
        total_simulations = sum(stats[move][1] for move in legal_moves) + 1
        best_score = float('-inf')
        best_move = None

        for move in legal_moves:
            wins, visits = stats[move]
            if visits == 0:
                score = float('inf')
            else:
                exploitation = wins / visits
                exploration = C * math.sqrt(math.log(total_simulations) / visits)
                score = exploitation + exploration

            if score > best_score:
                best_score = score
                best_move = move

        sim_board = clone_board(board)
        for row in range(len(sim_board) - 1, -1, -1):
            if sim_board[row][best_move] == 'O':
                sim_board[row][best_move] = player
                break

        winner = simulate_random_game(sim_board, switch_player(player))
        if winner == player:
            result = 1
        elif winner == switch_player(player):
            result = -1
        else:
            result = 0

        stats[best_move][0] += result
        stats[best_move][1] += 1

        if verbosity == "Verbose":
            print("NODE ADDED")
            print(f"TERMINAL NODE VALUE: {result}")
            print("Updated values:")
            print(f"wi: {stats[best_move][0]}")
            print(f"ni: {stats[best_move][1]}\n")

    return max(legal_moves, key=lambda m: stats[m][0] / stats[m][1])

def uct_improved_move(board, player, simulations, verbosity):
    legal_moves = get_legal_moves(board)
    stats = {move: [0, 0] for move in legal_moves}

    def center_bias(move):
        return -abs(3 - move)

    for _ in range(simulations):
        total_simulations = sum(stats[move][1] for move in legal_moves) + 1
        best_score = float('-inf')
        best_move = None

        for move in legal_moves:
            wins, visits = stats[move]
            if visits == 0:
                score = float('inf')
            else:
                exploitation = wins / visits
                exploration = math.sqrt(math.log(total_simulations) / visits)
                score = exploitation + 1.4 * exploration + 0.01 * center_bias(move)

            if score > best_score:
                best_score = score
                best_move = move
                
        if best_move is None:
            continue  # Skip this simulation if no move was selected
            
        sim_board = clone_board(board)
        for row in range(len(sim_board) - 1, -1, -1):
            if sim_board[row][best_move] == 'O':
                sim_board[row][best_move] = player
                break

        winner = simulate_random_game(sim_board, switch_player(player))
        if winner == player:
            result = 1
        elif winner == switch_player(player):
            result = -1
        else:
            result = 0

        stats[best_move][0] += result
        stats[best_move][1] += 1

        if verbosity == "Verbose":
            print("NODE ADDED")
            print(f"TERMINAL NODE VALUE: {result}")
            print("Updated values:")
            print(f"wi: {stats[best_move][0]}")
            print(f"ni: {stats[best_move][1]}")
            
            
    valid_moves = {m: stats[m] for m in legal_moves if stats[m][1] > 0}
    if not valid_moves:
        return None  # No valid move found after simulations
    
    return max(valid_moves, key=lambda m: valid_moves[m][0] / valid_moves[m][1])


    return max(legal_moves, key=lambda m: stats[m][0] / stats[m][1])

def check_winner(board):
    def check_line(line):
        for i in range(len(line) - 3):
            if line[i] != 'O' and line[i] == line[i+1] == line[i+2] == line[i+3]:
                return line[i]
        return None

    for row in board:
        result = check_line(row)
        if result: return result

    for c in range(7):
        column = [board[r][c] for r in range(6)]
        result = check_line(column)
        if result: return result

    for r in range(3):
        for c in range(4):
            if board[r][c] != 'O' and board[r][c] == board[r+1][c+1] == board[r+2][c+2] == board[r+3][c+3]:
                return board[r][c]
    for r in range(3, 6):
        for c in range(4):
            if board[r][c] != 'O' and board[r][c] == board[r-1][c+1] == board[r-2][c+2] == board[r-3][c+3]:
                return board[r][c]

    return None

def simulate_game():
    input_file, verbosity, simulations = sys.argv[1], sys.argv[2], int(sys.argv[3])
    algorithm, player, board = read_board(input_file)
    current_player = player
    winner_symbol = None

    log_file = open("game_output.log", "w")
    def log(msg):
        print(msg)
        print(msg, file=log_file)

    start_time = time.time()

    # Create CSV file if it doesn't exist
    if not os.path.exists("game_metrics.csv"):
        with open("game_metrics.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Algorithm", "Simulations", "Winner", "Duration (ms)"])

    if algorithm == "UR" and simulations != 0:
        print("UR must have 0 simulations.")
        sys.exit(1)
    if algorithm in ("PMCGS", "UCT", "UCT-IMPROVED") and simulations <= 0:
        print(f"{algorithm} requires > 0 simulations.")
        sys.exit(1)

    while True:
        if algorithm == "UR":
            move = uniform_random_move(board)
        elif algorithm == "PMCGS":
            move = pmcgs_move(board, current_player, simulations, verbosity)
        elif algorithm == "UCT":
            move = uct_move(board, current_player, simulations, verbosity)
        elif algorithm == "UCT-IMPROVED":
            move = uct_improved_move(board, current_player, simulations, verbosity)
        else:
            log("Unknown algorithm.")
            break

        if move is None:
            log("No valid moves left.")
            winner_symbol = 'None'
            break

        for row in range(5, -1, -1):
            if board[row][move] == 'O':
                board[row][move] = current_player
                break

        log(f"Turn: {'Red' if current_player == 'R' else 'Yellow'}")
        for row in board:
            log(" ".join(row))
        log(f"FINAL Move selected: {move + 1}")

        winner = check_winner(board)
        if winner:
            winner_symbol = winner
            log(f"{'Red' if winner == 'R' else 'Yellow'} is the winner")
            break

        current_player = switch_player(current_player)

    duration_ms = int((time.time() - start_time) * 1000)
    with open("game_metrics.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([algorithm, simulations, winner_symbol or "None", duration_ms])
    log(f"Game duration: {duration_ms} ms")
    log(f"Winner: {winner_symbol or 'None'}")
    log_file.close()



# Define the 5 strategies
algorithms = [
    ("UR", 0),
    ("PMCGS", 500),
    ("PMCGS", 1000),
    ("UCT", 500),
    ("UCT", 1000)
]

def run_match(algo1, algo2, num_games=100):
    wins = {0: 0, 1: 0}  # algo1 wins, algo2 wins

    for i in range(num_games):
        # Alternate who goes first
        if i % 2 == 0:
            winner = play_full_game(algo1, algo2)
            if winner == 'R':
                wins[0] += 1
            elif winner == 'Y':
                wins[1] += 1
        else:
            winner = play_full_game(algo2, algo1)
            if winner == 'R':
                wins[1] += 1
            elif winner == 'Y':
                wins[0] += 1
    return wins

def play_full_game(algo1_tuple, algo2_tuple):
    alg1, sim1 = algo1_tuple
    alg2, sim2 = algo2_tuple
    board = [['O'] * 7 for _ in range(6)]
    current_player = 'R'
    winner = None

    while True:
        if current_player == 'R':
            move = select_move(alg1, board, current_player, sim1)
        else:
            move = select_move(alg2, board, current_player, sim2)

        if move is None:
            break  # draw

        for row in range(5, -1, -1):
            if board[row][move] == 'O':
                board[row][move] = current_player
                break

        winner = check_winner(board)
        if winner:
            return winner

        if not get_legal_moves(board):
            break

        current_player = switch_player(current_player)
    return None  # draw

def select_move(algorithm, board, player, simulations):
    if algorithm == "UR":
        return uniform_random_move(board)
    elif algorithm == "PMCGS":
        return pmcgs_move(board, player, simulations, "None")
    elif algorithm == "UCT":
        return uct_move(board, player, simulations, "None")
    elif algorithm == "UCT-IMPROVED":
        return uct_improved_move(board, player, simulations, "None")
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

def run_tournament():
    results = defaultdict(lambda: defaultdict(int))

    for i, algo1 in enumerate(algorithms):
        for j, algo2 in enumerate(algorithms):
            if i <= j:
                print(f"Running: {algo1} vs {algo2}")
                wins = run_match(algo1, algo2)
                results[algo1][algo2] = wins[0]
                results[algo2][algo1] = wins[1]

    print("\n--- TOURNAMENT RESULTS (Winning % for row vs column) ---")
    headers = [f"{name}({sims})" for name, sims in algorithms]
    print(f"{'':20}", end="")
    for h in headers:
        print(f"{h:>20}", end="")
    print()
    for a1 in algorithms:
        row_name = f"{a1[0]}({a1[1]})"
        print(f"{row_name:20}", end="")
        for a2 in algorithms:
            total = results[a1][a2] + results[a2][a1]
            pct = (results[a1][a2] / total * 100) if total > 0 else 0
            print(f"{pct:20.2f}", end="")
        print()


def uct_test():
    win_50 = run_match(("UCT",50),("UCT-IMPROVED",50))
    win_100 =run_match(("UCT",100),("UCT-IMPROVED",100))
    win_500 = run_match(("UCT",500),("UCT-IMPROVED",500))

    print(win_50)
    print(win_100)
    print(win_500)


def main():
    if len(sys.argv) != 4:
        print("Usage: python3 main.py <input_file> <verbosity> <simulations>")
        sys.exit(1)
    simulate_game()

if __name__ == "__main__":
    main()
    #run_tournament()
    # uct_test()
