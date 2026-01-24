import pygame
import sys

pygame.init()

# ---------- НАЛАШТУВАННЯ ----------
WIDTH, HEIGHT = 700, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe")

FONT_BIG = pygame.font.SysFont(None, 64)
FONT = pygame.font.SysFont(None, 32)

WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY = (180,180,180)
GREEN = (50,200,100)
RED = (220, 60, 60)
BLUE = (70, 120, 255)
FIELD_COLOR = (40, 180, 160)
INPUT_BG = (50, 50, 50)
INPUT_ACTIVE = (100, 200, 255)

SQUARE = 100
SURRENDER_BTN = pygame.Rect(350, 140, 200, 45)

# ---------- СТАНИ ----------
HUB = "hub"
GAME = "game"
WIN = "win"
DRAW = "draw"

state = HUB

# ---------- ДАНІ ----------
nickname = ""
active_input = False

board = [[None]*3 for _ in range(3)]
player = "X"
winner = None

# ---------- ФУНКЦІЇ ----------
def draw_text(text, font, color, x, y, center=False):
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(img, rect)

def reset_game():
    global board, player, winner, state
    board = [[None]*3 for _ in range(3)]
    player = "X"
    winner = None
    state = GAME

def check_win(p):
    print('параметер Б', p)
    for i in range(3):
        print("Параметер І ", i)
        if all(board[i][c] == p for c in range(3)):
            print("Параметр спрацював c:", c, i)
            return True
        if all(board[r][i] == p for r in range(3)):
            print("Параметр спрацював", r, i)
            return True
    # З ліва верху до низу діагоналлю
    if all(board[i][i] == p for i in range(3)):
        return True
    # З правого верху до низу діагоналлю
    if all(board[i][2-i] == p for i in range(3)):
        return True
    return False

def check_draw():
    for row in board:
        if None in row:
            return False
    return True

# ---------- ХАБ ----------
def draw_hub():
    screen.fill((30,30,30))
    draw_text("HUB", FONT_BIG, WHITE, WIDTH//2, 50, center=True)

    # input box
    input_box = pygame.Rect(30, 150, 200, 40)

    pygame.draw.rect(screen, INPUT_BG, input_box)
    pygame.draw.rect(
        screen,
        INPUT_ACTIVE if active_input else WHITE,
        input_box,
        2
    )

    if nickname:
        text_surf = FONT.render(nickname, True, WHITE)
    else:
        text_surf = FONT.render("Enter nickname", True, GRAY)

    screen.blit(text_surf, (input_box.x + 8, input_box.y + 8))

    # PLAY button
    pygame.draw.rect(screen, GREEN, (WIDTH//2-75, HEIGHT//2-25, 150, 50))
    draw_text("PLAY", FONT, BLACK, WIDTH//2, HEIGHT//2, center=True)
# ---------- ГРА ----------
def draw_game():
    screen.fill(FIELD_COLOR)

    for i in range(1,3):
        pygame.draw.line(screen, BLACK, (0, i*SQUARE), (300, i*SQUARE), 5)
        pygame.draw.line(screen, BLACK, (i*SQUARE, 0), (i*SQUARE, 300), 5)

    for r in range(3):
        for c in range(3):
            if board[r][c] == "X":
                pygame.draw.line(screen, RED, (c*SQUARE+20, r*SQUARE+20),
                                 (c*SQUARE+80, r*SQUARE+80), 6)
                pygame.draw.line(screen, RED, (c*SQUARE+80, r*SQUARE+20),
                                 (c*SQUARE+20, r*SQUARE+80), 6)
            elif board[r][c] == "O":
                pygame.draw.circle(screen, BLUE,
                                   (c*SQUARE+50, r*SQUARE+50), 30, 6)

    player_color = RED if player == "X" else BLUE
    draw_text(f"Player: {player}", FONT, player_color, 350, 50)
    draw_text("Q - HUB", FONT, WHITE, 350, 90)
        # SURRENDER button
    pygame.draw.rect(screen, RED, SURRENDER_BTN, border_radius=8)
    draw_text("SURRENDER", FONT, WHITE,
              SURRENDER_BTN.centerx, SURRENDER_BTN.centery, center=True)


# ---------- ПЕРЕМОГА ----------
def draw_win():
    screen.fill((10,10,10))
    draw_text("WINNER!", FONT_BIG, GREEN, WIDTH//2, 120, center=True)
    draw_text(f"{nickname or 'Player'} won", FONT, WHITE, WIDTH//2, 200, center=True)
    draw_text(f"Symbol: {winner}", FONT, WHITE, WIDTH//2, 240, center=True)
    draw_text("Press Q to HUB", FONT, GRAY, WIDTH//2, 320, center=True)

# ---------- НІЧИЯ ----------
def draw_draw():
    screen.fill((10,10,10))
    draw_text("DRAW!", FONT_BIG, WHITE, WIDTH//2, 160, center=True)
    draw_text("No winner", FONT, GRAY, WIDTH//2, 220, center=True)
    draw_text("Press Q to HUB", FONT, GRAY, WIDTH//2, 300, center=True)

# ---------- ГОЛОВНИЙ ЦИКЛ ----------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # HUB
        if state == HUB:
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 30 <= x <= 230 and 150 <= y <= 190:
                    active_input = True
                else:
                    active_input = False

                if WIDTH//2-75 <= x <= WIDTH//2+75 and HEIGHT//2-25 <= y <= HEIGHT//2+25:
                    reset_game()

            if event.type == pygame.KEYDOWN and active_input:
                if event.key == pygame.K_BACKSPACE:
                    nickname = nickname[:-1]
                elif event.unicode.isprintable() and not event.unicode.isspace():
                    if len(nickname) < 10:
                        nickname += event.unicode
                    

        # GAME
        if state == GAME:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                state = HUB

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if x < 300 and y < 300:
                    r = y // SQUARE
                    c = x // SQUARE
                    if board[r][c] is None:
                        board[r][c] = player
                                    # surrender button
                        if SURRENDER_BTN.collidepoint(event.pos):
                            winner = "O" if player == "X" else "X"
                            state = WIN

                        if check_win(player):
                            winner = player
                            state = WIN
                        elif check_draw():
                            state = DRAW
                        else:
                            player = "O" if player == "X" else "X"

        # WIN / DRAW
        if state in (WIN, DRAW):
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                state = HUB

    if state == HUB:
        draw_hub()
    elif state == GAME:
        draw_game()
    elif state == WIN:
        draw_win()
    elif state == DRAW:
        draw_draw()

    pygame.display.update()
