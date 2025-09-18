import pygame
import sys
import os
import marte

# --- Constants ---
WIDTH, HEIGHT = 480, 480
DIMENSION = 8
SQ_SIZE = WIDTH // DIMENSION
MAX_FPS = 15

# --- Pygame Setup ---
def setup_pygame():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Marte Chess")
    clock = pygame.time.Clock()
    return screen, clock

# --- Load Assets ---
def load_images():
    images = {}
    piece_map = {
        'P': 'wP', 'R': 'wR', 'N': 'wN', 'B': 'wB', 'Q': 'wQ', 'K': 'wK',
        'p': 'bP', 'r': 'bR', 'n': 'bN', 'b': 'bB', 'q': 'bQ', 'k': 'bK'
    }
    for piece_char, asset_name in piece_map.items():
        path = os.path.join("assets", f"{asset_name}.png")
        images[piece_char] = pygame.transform.scale(pygame.image.load(path), (SQ_SIZE, SQ_SIZE))
    return images

IMAGES = load_images()

# --- Drawing Functions ---
def draw_game_state(screen, gs, valid_moves, selected_square):
    draw_board(screen)
    highlight_squares(screen, gs, valid_moves, selected_square)
    draw_pieces(screen, gs.board)

def draw_board(screen):
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            pygame.draw.rect(screen, color, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '.':
                screen.blit(IMAGES[piece], pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def highlight_squares(screen, gs, valid_moves, selected_square):
    if selected_square:
        r, c = selected_square
        if gs.board[r][c][0] == ('w' if gs.current_turn == 'w' else 'b'):
            s = pygame.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(pygame.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            s.fill(pygame.Color('yellow'))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col * SQ_SIZE, move.end_row * SQ_SIZE))

def draw_text(screen, text):
    font = pygame.font.SysFont(None, 48, True, False)
    text_object = font.render(text, 0, pygame.Color('Gray'))
    text_location = pygame.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - text_object.get_width() / 2, HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, 0, pygame.Color('Black'))
    screen.blit(text_object, text_location.move(2, 2))

def draw_menu(screen):
    screen.fill(pygame.Color("black"))
    font = pygame.font.SysFont(None, 32, True, False)
    title_text = font.render("Choose your color", 0, pygame.Color('white'))
    title_location = pygame.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - title_text.get_width() / 2, 100)
    screen.blit(title_text, title_location)
    white_button = pygame.Rect(WIDTH / 4, 200, WIDTH / 2, 50)
    pygame.draw.rect(screen, pygame.Color('white'), white_button)
    white_text = font.render("Play as White", 0, pygame.Color('black'))
    white_text_location = white_button.move(white_button.width / 2 - white_text.get_width() / 2, white_button.height/2 - white_text.get_height()/2)
    screen.blit(white_text, white_text_location)
    black_button = pygame.Rect(WIDTH / 4, 300, WIDTH / 2, 50)
    pygame.draw.rect(screen, pygame.Color('darkgray'), black_button)
    black_text = font.render("Play as Black", 0, pygame.Color('white'))
    black_text_location = black_button.move(black_button.width / 2 - black_text.get_width() / 2, black_button.height/2 - black_text.get_height()/2)
    screen.blit(black_text, black_text_location)
    pygame.display.flip()
    return white_button, black_button

# --- Main Game Loop ---
def main():
    screen, clock = setup_pygame()

    player_color = None
    white_button, black_button = draw_menu(screen)
    while player_color is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                location = pygame.mouse.get_pos()
                if white_button.collidepoint(location): player_color = 'w'
                elif black_button.collidepoint(location): player_color = 'b'
        clock.tick(MAX_FPS)

    gs = marte.GameState()
    valid_moves = gs.get_legal_moves()
    move_made = False

    selected_square = ()
    player_clicks = []
    game_over = False

    while True:
        human_turn = (gs.current_turn == player_color)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not game_over and human_turn:
                    location = pygame.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if selected_square == (row, col):
                        selected_square = ()
                        player_clicks = []
                    else:
                        selected_square = (row, col)
                        player_clicks.append(selected_square)
                    if len(player_clicks) == 2:
                        move = marte.Move(player_clicks[0], player_clicks[1], gs.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                move_made = True
                                selected_square = ()
                                player_clicks = []
                                break
                        if not move_made:
                            player_clicks = [selected_square]

        if not game_over and not human_turn:
            # AI move
            # For now, we'll just pick a random move to test the logic
            # computer_move = marte.get_best_move(gs)
            # if computer_move:
            #     gs.make_move(computer_move)
            #     move_made = True
            pass # AI is disabled for now to simplify testing

        if move_made:
            valid_moves = gs.get_legal_moves()
            move_made = False

        draw_game_state(screen, gs, valid_moves, selected_square)

        if len(valid_moves) == 0:
             game_over = True
             if gs.is_in_check():
                 winner = "Black" if gs.current_turn == 'w' else "White"
                 draw_text(screen, f"Checkmate! {winner} wins.")
             else:
                 draw_text(screen, "Stalemate!")

        clock.tick(MAX_FPS)
        pygame.display.flip()

if __name__ == "__main__":
    main()
