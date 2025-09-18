# Marte - A simple chess engine in Python

# Initial board setup
# 'r' = black rook, 'n' = black knight, 'b' = black bishop, 'q' = black queen, 'k' = black king, 'p' = black pawn
# 'R' = white rook, 'N' = white knight, 'B' = white bishop, 'Q' = white queen, 'K' = white king, 'P' = white pawn
# '.' = empty square
board = [
    ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
    ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
]

def get_pawn_moves(board, row, col):
    moves = []
    piece = board[row][col]
    color = 'b' if piece.islower() else 'w'

    if color == 'b':
        # Move one step forward
        if row + 1 < 8 and board[row + 1][col] == '.':
            moves.append(((row, col), (row + 1, col)))
        # Move two steps forward
        if row == 1 and board[row + 1][col] == '.' and board[row + 2][col] == '.':
            moves.append(((row, col), (row + 2, col)))
        # Captures
        if col - 1 >= 0 and row + 1 < 8 and board[row + 1][col - 1] != '.' and board[row + 1][col - 1].isupper():
            moves.append(((row, col), (row + 1, col - 1)))
        if col + 1 < 8 and row + 1 < 8 and board[row + 1][col + 1] != '.' and board[row + 1][col + 1].isupper():
            moves.append(((row, col), (row + 1, col + 1)))
    else: # White pawn
        # Move one step forward
        if row - 1 >= 0 and board[row - 1][col] == '.':
            moves.append(((row, col), (row - 1, col)))
        # Move two steps forward
        if row == 6 and board[row - 1][col] == '.' and board[row - 2][col] == '.':
            moves.append(((row, col), (row - 2, col)))
        # Captures
        if col - 1 >= 0 and row - 1 >= 0 and board[row - 1][col - 1] != '.' and board[row - 1][col - 1].islower():
            moves.append(((row, col), (row - 1, col - 1)))
        if col + 1 < 8 and row - 1 >= 0 and board[row - 1][col + 1] != '.' and board[row - 1][col + 1].islower():
            moves.append(((row, col), (row - 1, col + 1)))
    return moves

def get_all_moves(board, color):
    """Gets all possible moves for a given color."""
    moves = []
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece != '.':
                piece_color = 'b' if piece.islower() else 'w'
                if piece_color == color:
                    if piece.lower() == 'p':
                        moves.extend(get_pawn_moves(board, r, c))
                    elif piece.lower() == 'n':
                        moves.extend(get_knight_moves(board, r, c))
                    elif piece.lower() == 'b':
                        moves.extend(get_bishop_moves(board, r, c))
                    elif piece.lower() == 'r':
                        moves.extend(get_rook_moves(board, r, c))
                    elif piece.lower() == 'q':
                        moves.extend(get_queen_moves(board, r, c))
                    elif piece.lower() == 'k':
                        moves.extend(get_king_moves(board, r, c))
    return moves

def get_knight_moves(board, row, col):
    moves = []
    piece = board[row][col]
    color = 'b' if piece.islower() else 'w'
    knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
    for dr, dc in knight_moves:
        r, c = row + dr, col + dc
        if 0 <= r < 8 and 0 <= c < 8:
            target_piece = board[r][c]
            if target_piece == '.':
                moves.append(((row, col), (r,c)))
            else:
                target_color = 'b' if target_piece.islower() else 'w'
                if color != target_color:
                    moves.append(((row, col), (r,c)))
    return moves

def get_sliding_moves(board, row, col, directions):
    moves = []
    piece = board[row][col]
    color = 'b' if piece.islower() else 'w'
    for dr, dc in directions:
        r, c = row + dr, col + dc
        while 0 <= r < 8 and 0 <= c < 8:
            target_piece = board[r][c]
            if target_piece == '.': # Can move to empty square
                moves.append(((row, col), (r, c)))
            else: # Ran into a piece
                target_color = 'b' if target_piece.islower() else 'w'
                if color != target_color: # Can capture opponent's piece
                    moves.append(((row, col), (r, c)))
                break # Stop searching in this direction
            r, c = r + dr, c + dc
    return moves

def get_bishop_moves(board, row, col):
    return get_sliding_moves(board, row, col, [(-1, -1), (-1, 1), (1, -1), (1, 1)])

def get_rook_moves(board, row, col):
    return get_sliding_moves(board, row, col, [(-1, 0), (1, 0), (0, -1), (0, 1)])

def get_queen_moves(board, row, col):
    return get_rook_moves(board, row, col) + get_bishop_moves(board, row, col)

def get_king_moves(board, row, col):
    moves = []
    piece = board[row][col]
    color = 'b' if piece.islower() else 'w'
    king_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dr, dc in king_moves:
        r, c = row + dr, col + dc
        if 0 <= r < 8 and 0 <= c < 8:
            target_piece = board[r][c]
            if target_piece == '.':
                moves.append(((row, col), (r,c)))
            else:
                target_color = 'b' if target_piece.islower() else 'w'
                if color != target_color:
                    moves.append(((row, col), (r,c)))
    return moves

def print_board(board):
    """Prints the chess board to the console."""
    print("  a b c d e f g h")
    print(" +-----------------+")
    for i, row in enumerate(board):
        print(f"{8 - i}| {' '.join(row)} |{8 - i}")
    print(" +-----------------+")
    print("  a b c d e f g h")

def parse_move(move_str):
    """Parses a move from algebraic notation (e.g., 'e2e4') to board coordinates."""
    if len(move_str) != 4:
        return None
    try:
        from_col = ord(move_str[0]) - ord('a')
        from_row = 8 - int(move_str[1])
        to_col = ord(move_str[2]) - ord('a')
        to_row = 8 - int(move_str[3])
        if 0 <= from_row < 8 and 0 <= from_col < 8 and 0 <= to_row < 8 and 0 <= to_col < 8:
            return ((from_row, from_col), (to_row, to_col))
    except (ValueError, IndexError):
        return None
    return None

def make_move(board, move):
    """Makes a move on the board."""
    from_pos, to_pos = move
    from_row, from_col = from_pos
    to_row, to_col = to_pos
    board[to_row][to_col] = board[from_row][from_col]
    board[from_row][from_col] = '.'

import random
import copy

piece_scores = {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0}

def evaluate_board(board):
    """Evaluates the board based on material."""
    score = 0
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece != '.':
                score += piece_scores[piece.lower()] * (1 if piece.isupper() else -1)
    return score

def get_best_move(board, color):
    """Finds the best move for a given color using a simple 1-ply search."""
    best_move = None
    best_score = -float('inf') if color == 'w' else float('inf')

    possible_moves = get_all_moves(board, color)
    random.shuffle(possible_moves) # Add some variety

    for move in possible_moves:
        temp_board = copy.deepcopy(board)
        make_move(temp_board, move)
        score = evaluate_board(temp_board)

        if color == 'w':
            if score > best_score:
                best_score = score
                best_move = move
        else: # Black
            if score < best_score:
                best_score = score
                best_move = move

    return best_move if best_move else (possible_moves[0] if possible_moves else None)

def main():
    """Main game loop."""
    current_turn = 'w'
    while True:
        print_board(board)

        possible_moves = get_all_moves(board, current_turn)
        if not possible_moves:
            print(f"{'White' if current_turn == 'b' else 'Black'} wins by checkmate/stalemate!")
            break

        if current_turn == 'w':
            print("White's turn (you).")
            move_str = input("Enter your move (e.g., e2e4): ")
            user_move = parse_move(move_str)

            if user_move and user_move in possible_moves:
                make_move(board, user_move)
                current_turn = 'b'
            else:
                print("Invalid move. Please try again.")
        else:
            print("Black's turn (computer).")
            computer_move = get_best_move(board, 'b')
            if computer_move:
                make_move(board, computer_move)
                current_turn = 'w'
            else:
                # Should not happen if possible_moves check passed
                print("Computer has no moves! This shouldn't happen.")
                break


if __name__ == "__main__":
    main()
