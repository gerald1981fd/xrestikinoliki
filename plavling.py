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
BLUE = (50,150,255)
GREEN = (50,200,100)

SQUARE = 100

# ---------- СТАНИ ----------
HUB = "hub"
GAME = "game"
WIN = "win"

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
    for i in range(3):
        if all(board[i][c] == p for c in range(3)):
            return True
        if all(board[r][i] == p for r in range(3)):
            return True
    if all(board[i][i] == p for i in range(3)):
        return True
    if all(board[i][2-i] == p for i in range(3)):
        return True
    return False

# ---------- ХАБ ----------
def draw_hub():
    screen.fill((30,30,30))

    draw_text("HUB", FONT_BIG, WHITE, WIDTH//2, 50, center=True)

    # input
    pygame.draw.rect(screen, WHITE, (30, 150, 200, 40), 2)
    draw_text(nickname or "Enter nickname", FONT, WHITE, 40, 160)

    # play button
    pygame.draw.rect(screen, GREEN, (WIDTH//2-75, HEIGHT//2-25, 150, 50))
    draw_text("PLAY", FONT, BLACK, WIDTH//2, HEIGHT//2, center=True)

# ---------- ГРА ----------
def draw_game():
    screen.fill((20,160,140))

    # grid
    for i in range(1,3):
        pygame.draw.line(screen, BLACK, (0, i*SQUARE), (300, i*SQUARE), 5)
        pygame.draw.line(screen, BLACK, (i*SQUARE, 0), (i*SQUARE, 300), 5)

    # figures
    for r in range(3):
        for c in range(3):
            if board[r][c] == "X":
                pygame.draw.line(screen, BLACK, (c*SQUARE+20, r*SQUARE+20),
                                 (c*SQUARE+80, r*SQUARE+80), 6)
                pygame.draw.line(screen, BLACK, (c*SQUARE+80, r*SQUARE+20),
                                 (c*SQUARE+20, r*SQUARE+80), 6)
            elif board[r][c] == "O":
                pygame.draw.circle(screen, BLACK,
                                   (c*SQUARE+50, r*SQUARE+50), 30, 6)

    draw_text(f"Player: {player}", FONT, WHITE, 350, 50)
    draw_text("Q - HUB", FONT, WHITE, 350, 90)

# ---------- ЕКРАН ПЕРЕМОГИ ----------
def draw_win():
    screen.fill((10,10,10))

    draw_text("WINNER!", FONT_BIG, GREEN, WIDTH//2, 120, center=True)
    draw_text(f"{nickname or 'Player'} won", FONT, WHITE, WIDTH//2, 200, center=True)
    draw_text(f"Symbol: {winner}", FONT, WHITE, WIDTH//2, 240, center=True)
    draw_text("Press Q to HUB", FONT, GRAY, WIDTH//2, 320, center=True)

# ---------- ГОЛОВНИЙ ЦИКЛ ----------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # ---------- HUB ----------
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
                elif len(nickname) < 10:
                    nickname += event.unicode

        # ---------- GAME ----------
        if state == GAME:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    state = HUB

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if x < 300 and y < 300:
                    r = y // SQUARE
                    c = x // SQUARE
                    if board[r][c] is None:
                        board[r][c] = player
                        if check_win(player):
                            winner = player
                            state = WIN
                        else:
                            player = "O" if player == "X" else "X"

        # ---------- WIN ----------
        if state == WIN:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    state = HUB

    if state == HUB:
        draw_hub()
    elif state == GAME:
        draw_game()
    elif state == WIN:
        draw_win()

    pygame.display.update()
