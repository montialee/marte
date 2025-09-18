import copy
import random

class Move:
    def __init__(self, start_sq, end_sq, board, is_enpassant_move=False, is_castle_move=False):
        self.start_row, self.start_col = start_sq
        self.end_row, self.end_col = end_sq
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.piece_captured = 'p' if self.piece_moved == 'P' else 'P'
        self.is_castle_move = is_castle_move
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

class CastleRights:
    def __init__(self, wks, wqs, bks, bqs):
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs

class GameState:
    def __init__(self):
        self.board = [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        ]
        self.current_turn = 'w'
        self.castle_rights = CastleRights(True, True, True, True)
        self.en_passant_target = ()
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.in_check = False
        self.pins = []
        self.checks = []

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "."
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.current_turn = 'b' if self.current_turn == 'w' else 'w'
        if move.piece_moved == 'K':
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == 'k':
            self.black_king_location = (move.end_row, move.end_col)

        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = '.'

        if move.piece_moved.lower() == 'p' and abs(move.start_row - move.end_row) == 2:
            self.en_passant_target = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.en_passant_target = ()

        if move.is_castle_move:
            if move.end_col - move.start_col == 2: # kingside
                self.board[move.end_row][move.end_col-1] = self.board[move.end_row][move.end_col+1]
                self.board[move.end_row][move.end_col+1] = '.'
            else: # queenside
                self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-2]
                self.board[move.end_row][move.end_col-2] = '.'

        self.update_castle_rights(move)

    def update_castle_rights(self, move):
        if move.piece_moved == 'K':
            self.castle_rights.wks = False
            self.castle_rights.wqs = False
        elif move.piece_moved == 'k':
            self.castle_rights.bks = False
            self.castle_rights.bqs = False
        elif move.piece_moved == 'R':
            if move.start_row == 7:
                if move.start_col == 0: self.castle_rights.wqs = False
                elif move.start_col == 7: self.castle_rights.wks = False
        elif move.piece_moved == 'r':
            if move.start_row == 0:
                if move.start_col == 0: self.castle_rights.bqs = False
                elif move.start_col == 7: self.castle_rights.bks = False

        if move.piece_captured == 'R':
            if move.end_row == 7:
                if move.end_col == 0: self.castle_rights.wqs = False
                elif move.end_col == 7: self.castle_rights.wks = False
        elif move.piece_captured == 'r':
            if move.end_row == 0:
                if move.end_col == 0: self.castle_rights.bqs = False
                elif move.end_col == 7: self.castle_rights.bks = False

    def get_legal_moves(self):
        moves = []
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()
        king_row, king_col = self.white_king_location if self.current_turn == 'w' else self.black_king_location

        if self.in_check:
            if len(self.checks) == 1:
                moves = self.get_all_possible_moves()
                check = self.checks[0]
                check_row, check_col = check[0], check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = []
                if piece_checking.lower() == 'n':
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].piece_moved.lower() != 'k':
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares:
                            moves.remove(moves[i])
            else: # double check
                self.get_king_moves(king_row, king_col, moves)
        else:
            moves = self.get_all_possible_moves()

        return moves

    def is_in_check(self):
        if self.current_turn == 'w':
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])

    def square_under_attack(self, r, c):
        self.current_turn = 'b' if self.current_turn == 'w' else 'w'
        opp_moves = self.get_all_possible_moves()
        self.current_turn = 'b' if self.current_turn == 'w' else 'w'
        for move in opp_moves:
            if move.end_row == r and move.end_col == c:
                return True
        return False

    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0].islower() if self.board[r][c] != '.' else False
                if (turn and self.current_turn == 'b') or (not turn and self.current_turn == 'w'):
                    piece = self.board[r][c]
                    if piece.lower() == 'p': self.get_pawn_moves(r, c, moves)
                    elif piece.lower() == 'r': self.get_rook_moves(r, c, moves)
                    elif piece.lower() == 'n': self.get_knight_moves(r, c, moves)
                    elif piece.lower() == 'b': self.get_bishop_moves(r, c, moves)
                    elif piece.lower() == 'q': self.get_queen_moves(r, c, moves)
                    elif piece.lower() == 'k': self.get_king_moves(r, c, moves)
        return moves

    def get_pawn_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.current_turn == 'w':
            if self.board[r-1][c] == ".":
                if not piece_pinned or pin_direction == (-1, 0):
                    moves.append(Move((r, c), (r-1, c), self.board))
                    if r == 6 and self.board[r-2][c] == ".":
                        moves.append(Move((r, c), (r-2, c), self.board))
            if c-1 >= 0:
                if self.board[r-1][c-1].islower():
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.en_passant_target:
                    moves.append(Move((r, c), (r-1, c-1), self.board, is_enpassant_move=True))
            if c+1 <= 7:
                if self.board[r-1][c+1].islower():
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.en_passant_target:
                    moves.append(Move((r, c), (r-1, c+1), self.board, is_enpassant_move=True))
        else:
            if self.board[r+1][c] == ".":
                if not piece_pinned or pin_direction == (1, 0):
                    moves.append(Move((r, c), (r+1, c), self.board))
                    if r == 1 and self.board[r+2][c] == ".":
                        moves.append(Move((r, c), (r+2, c), self.board))
            if c-1 >= 0:
                if self.board[r+1][c-1].isupper():
                    if not piece_pinned or pin_direction == (1, -1):
                        moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.en_passant_target:
                    moves.append(Move((r, c), (r+1, c-1), self.board, is_enpassant_move=True))
            if c+1 <= 7:
                if self.board[r+1][c+1].isupper():
                    if not piece_pinned or pin_direction == (1, 1):
                        moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.en_passant_target:
                    moves.append(Move((r, c), (r+1, c+1), self.board, is_enpassant_move=True))

    def get_rook_moves(self, r, c, moves):
        self._get_sliding_moves(r, c, moves, [(-1, 0), (1, 0), (0, -1), (0, 1)])

    def get_knight_moves(self, r, c, moves):
        piece_pinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break

        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knight_moves:
            end_row, end_col = r + m[0], c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == '.' or end_piece.islower() != self.board[r][c].islower():
                        moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_bishop_moves(self, r, c, moves):
        self._get_sliding_moves(r, c, moves, [(-1, -1), (-1, 1), (1, -1), (1, 1)])

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_king_moves(self, r, c, moves):
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        for i in range(8):
            end_row, end_col = r + row_moves[i], c + col_moves[i]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece == '.' or end_piece.islower() != self.board[r][c].islower():
                    # place king on end square and check for checks
                    if self.current_turn == 'w': self.white_king_location = (end_row, end_col)
                    else: self.black_king_location = (end_row, end_col)
                    in_check, _, _ = self.check_for_pins_and_checks()
                    if not in_check:
                        moves.append(Move((r,c), (end_row, end_col), self.board))
                    # place king back on original location
                    if self.current_turn == 'w': self.white_king_location = (r, c)
                    else: self.black_king_location = (r, c)
        self.get_castle_moves(r, c, moves)

    def get_castle_moves(self, r, c, moves):
        if self.square_under_attack(r,c): return
        if (self.current_turn == 'w' and self.castle_rights.wks) or (self.current_turn == 'b' and self.castle_rights.bks):
            self.get_kingside_castle_moves(r, c, moves)
        if (self.current_turn == 'w' and self.castle_rights.wqs) or (self.current_turn == 'b' and self.castle_rights.bqs):
            self.get_queenside_castle_moves(r, c, moves)

    def get_kingside_castle_moves(self, r, c, moves):
        if self.board[r][c+1] == '.' and self.board[r][c+2] == '.':
            if not self.square_under_attack(r, c+1) and not self.square_under_attack(r, c+2):
                moves.append(Move((r,c), (r, c+2), self.board, is_castle_move=True))

    def get_queenside_castle_moves(self, r, c, moves):
        if self.board[r][c-1] == '.' and self.board[r][c-2] == '.' and self.board[r][c-3] == '.':
            if not self.square_under_attack(r, c-1) and not self.square_under_attack(r, c-2):
                moves.append(Move((r,c), (r, c-2), self.board, is_castle_move=True))

    def _get_sliding_moves(self, r, c, moves, directions):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c].lower() != 'q': # can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break

        for d in directions:
            for i in range(1, 8):
                end_row, end_col = r + d[0] * i, c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == ".":
                            moves.append(Move((r,c), (end_row, end_col), self.board))
                        elif end_piece.islower() != self.board[r][c].islower():
                            moves.append(Move((r,c), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:
                    break

    def check_for_pins_and_checks(self):
        pins = []
        checks = []
        in_check = False
        if self.current_turn == "w":
            enemy_color, friendly_color = "b", "w"
            start_row, start_col = self.white_king_location
        else:
            enemy_color, friendly_color = "w", "b"
            start_row, start_col = self.black_king_location

        directions = ((-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = ()
            for i in range(1, 8):
                end_row, end_col = start_row + d[0] * i, start_col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece != '.' and (end_piece.islower() if friendly_color == 'b' else end_piece.isupper()):
                        if possible_pin == ():
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else:
                            break
                    elif end_piece != '.':
                        type = end_piece.lower()
                        if (0 <= j <= 3 and type == 'r') or \
                           (4 <= j <= 7 and type == 'b') or \
                           (i == 1 and type == 'p' and ((enemy_color == 'w' and 6 <= j <= 7) or (enemy_color == 'b' and 4 <= j <= 5))) or \
                           (type == 'q') or (i == 1 and type == 'k'):
                            if possible_pin == ():
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:
                                pins.append(possible_pin)
                                break
                        else:
                            break
                else:
                    break

        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knight_moves:
            end_row, end_col = start_row + m[0], start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece != '.' and (end_piece.islower() if enemy_color == 'b' else end_piece.isupper()) and end_piece.lower() == 'n':
                    in_check = True
                    checks.append((end_row, end_col, m[0], m[1]))

        return in_check, pins, checks

# --- The following functions are for the CLI and AI, they need to be refactored to use GameState ---

def get_best_move(gs):
    """Finds the best move for a given color using a simple 1-ply search."""
    best_move = None
    best_score = -float('inf') if gs.current_turn == 'w' else float('inf')

    possible_moves = gs.get_legal_moves()
    random.shuffle(possible_moves)

    for move in possible_moves:
        # To evaluate a move, we need a temporary GameState
        temp_gs = copy.deepcopy(gs)
        temp_gs.make_move(move)
        score = evaluate_board(temp_gs) # This needs to be adapted

        if gs.current_turn == 'w':
            if score > best_score:
                best_score = score
                best_move = move
        else: # Black
            if score < best_score:
                best_score = score
                best_move = move

    return best_move if best_move else (possible_moves[0] if possible_moves else None)

def evaluate_board(gs):
    """Evaluates the board based on material."""
    score = 0
    piece_scores = {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0}
    for r in range(8):
        for c in range(8):
            piece = gs.board[r][c]
            if piece != '.':
                score += piece_scores[piece.lower()] * (1 if piece.isupper() else -1)
    return score

def get_game_state(gs):
    """Determines the game state for the given color."""
    legal_moves = gs.get_legal_moves()
    if not legal_moves:
        if gs.is_in_check():
            return "checkmate"
        else:
            return "stalemate"
    return "ongoing"

def start_cli_game():
    """Starts the command-line interface game."""
    gs = GameState()

    while True:
        # This part needs to be refactored to print the board from gs
        # and parse moves into Move objects.
        # For now, the focus is on the GameState class itself.
        print("CLI needs refactoring to support GameState.")
        break

if __name__ == "__main__":
    start_cli_game()
