import pygame
import sys
import os
from marte import get_legal_moves, make_move, get_best_move, get_game_state, is_in_check

# --- Constants ---
WIDTH, HEIGHT = 480, 480  # Window size
DIMENSION = 8  # 8x8 board
SQ_SIZE = WIDTH // DIMENSION

# --- Pygame Setup ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Marte Chess")
clock = pygame.time.Clock()

# --- Load Assets ---
def load_images():
    """Loads piece images into a dictionary."""
    images = {}
    pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
    # Mapping from board characters to asset names
    piece_map = {
        'P': 'wP', 'R': 'wR', 'N': 'wN', 'B': 'wB', 'Q': 'wQ', 'K': 'wK',
        'p': 'bP', 'r': 'bR', 'n': 'bN', 'b': 'bB', 'q': 'bQ', 'k': 'bK'
    }

    for piece_char, asset_name in piece_map.items():
        path = os.path.join("assets", f"{asset_name}.png")
        # The images are 45x45, we scale them to fit the square size
        images[piece_char] = pygame.transform.scale(pygame.image.load(path), (SQ_SIZE, SQ_SIZE))

    return images

IMAGES = load_images()

# --- Drawing Functions ---
def draw_board(screen):
    """Draws the squares of the board."""
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            pygame.draw.rect(screen, color, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces(screen, board):
    """Draws the pieces on the board."""
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '.':
                screen.blit(IMAGES[piece], pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_game_state(screen, board):
    """Draws the board and pieces."""
    draw_board(screen)
    draw_pieces(screen, board)

# --- Main Game Loop ---
def highlight_squares(screen, board, selected_piece, legal_moves):
    """Highlights the selected square and legal moves."""
    if selected_piece:
        r, c = selected_piece
        s = pygame.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100) # transparency
        s.fill(pygame.Color('blue'))
        screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

        # Highlight legal moves
        s.fill(pygame.Color('yellow'))
        for move in legal_moves:
            if move[0] == selected_piece:
                screen.blit(s, (move[1][1] * SQ_SIZE, move[1][0] * SQ_SIZE))

def draw_game_over_text(screen, text):
    font = pygame.font.SysFont(None, 48, True, False)
    text_object = font.render(text, 0, pygame.Color('Gray'))
    text_location = pygame.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - text_object.get_width() / 2, HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, 0, pygame.Color('Black'))
    screen.blit(text_object, text_location.move(2, 2))

# --- Main Game Loop ---
def main():
    # Initial board state from marte.py, but we need a mutable copy
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

    current_turn = 'w'
    selected_square = () # (row, col) of the piece the user clicked
    player_clicks = [] # two clicks make a move: [(row, col), (row, col)]
    game_over = False

    running = True
    while running:
        human_turn = (current_turn == 'w')

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Mouse handler
            elif event.type == pygame.MOUSEBUTTONDOWN and human_turn and not game_over:
                location = pygame.mouse.get_pos() # (x, y) location of the mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if selected_square == (row, col): # User clicked the same square twice
                    selected_square = () # Deselect
                    player_clicks = []
                else:
                    selected_square = (row, col)
                    player_clicks.append(selected_square)

                if len(player_clicks) == 2: # After 2nd click
                    move = (player_clicks[0], player_clicks[1])
                    legal_moves = get_legal_moves(board, 'w')
                    if move in legal_moves:
                        make_move(board, move)
                        current_turn = 'b'
                        selected_square = () # reset user clicks
                        player_clicks = []
                    else:
                        player_clicks = [selected_square]

        # AI Move Logic
        if not human_turn and not game_over:
            computer_move = get_best_move(board, 'b')
            if computer_move:
                make_move(board, computer_move)
                current_turn = 'w'

        # Drawing logic
        draw_game_state(screen, board)

        legal_moves = get_legal_moves(board, current_turn)
        highlight_squares(screen, board, selected_square, legal_moves)

        if not game_over:
            game_state = get_game_state(board, current_turn)
            if game_state != "ongoing":
                game_over = True
                if game_state == "checkmate":
                    winner = "Black" if current_turn == 'w' else "White"
                    draw_game_over_text(screen, f"Checkmate! {winner} wins.")
                else:
                    draw_game_over_text(screen, "Stalemate!")

        pygame.display.flip()
        clock.tick(15)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
