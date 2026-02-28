import pygame
import socketio
import sys
import threading

# -------- socketio --------
sio = socketio.Client()
nickname = ""
enemy_nick = "Opponent"

connection_status = False
countdown_value = None

my_symbol = None
enemy_symbol = None
current_turn = "X"

my_score = 0
enemy_score = 0

board = [[None]*3 for _ in range(3)]
game_result = None
result_time = 0

# ---------------- SOCKET EVENTS ----------------

@sio.on("game_start")
def on_game_start(data):
    global state, my_symbol, enemy_nick, current_turn, enemy_symbol

    my_symbol = data["symbol"]
    enemy_nick = data["enemy"]
    current_turn = data["turn"]

    enemy_symbol = "O" if my_symbol == "X" else "X"

    state = "GAME"


@sio.on("board_update")
def on_board_update(data):
    global board, current_turn, my_score, enemy_score, game_result, result_time

    board = data["board"]

    if "winner" in data:
        if data["winner"] == my_symbol:
            my_score += 1
            game_result = "YOU WON"
        elif data["winner"] == "DRAW":
            game_result = "DRAW"
        else:
            enemy_score += 1
            game_result = "YOU LOST"

        result_time = pygame.time.get_ticks()

    if "turn" in data:
        current_turn = data["turn"]


@sio.event
def connect():
    global state
    state = "WAIT"
    sio.emit("set_nickname", nickname)


@sio.event
def disconnect():
    print("Disconnected")


def connect_to_server():
    sio.connect("http://localhost:3000")

# ---------------- PYGAME ----------------

pygame.init()

WIDTH, HEIGHT = 700, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe Online")

FONT_BIG = pygame.font.SysFont(None, 48)
FONT = pygame.font.SysFont(None, 28)

WHITE = (255,255,255)
GRAY = (180,180,180)
GREEN = (50,200,100)
RED = (220,60,60)
BLUE = (70,120,255)
BG = (30,30,30)

SQUARE = 100
FIELD_X = 50
FIELD_Y = 50

input_box = pygame.Rect(200, 120, 250, 40)
play_btn = pygame.Rect(275, 190, 150, 45)

active_input = False
state = "HUB"

clock = pygame.time.Clock()

# ---------------- FUNCTIONS ----------------

def draw_text(text, font, color, x, y, center=False):
    img = font.render(text, True, color)
    rect = img.get_rect(center=(x,y)) if center else img.get_rect(topleft=(x,y))
    screen.blit(img, rect)

# ---------------- LOOP ----------------

while True:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if state == "HUB":
            if event.type == pygame.MOUSEBUTTONDOWN:
                active_input = input_box.collidepoint(event.pos)

                if play_btn.collidepoint(event.pos) and nickname:
                    threading.Thread(target=connect_to_server, daemon=True).start()
                    state = "WAIT"

            if event.type == pygame.KEYDOWN and active_input:
                if event.key == pygame.K_BACKSPACE:
                    nickname = nickname[:-1]
                elif event.unicode.isprintable() and len(nickname) < 10:
                    nickname += event.unicode

        elif state == "GAME":
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos

                if FIELD_X <= x <= FIELD_X+300 and FIELD_Y <= y <= FIELD_Y+300:
                    c = (x - FIELD_X) // SQUARE
                    r = (y - FIELD_Y) // SQUARE

                    if current_turn == my_symbol:
                        sio.emit("make_move", {"row": r, "col": c})

    # ---------------- DRAW ----------------

    screen.fill(BG)

    if state == "HUB":
        draw_text("HUB", FONT_BIG, WHITE, WIDTH//2, 40, center=True)

        pygame.draw.rect(screen, (50,50,50), input_box)
        pygame.draw.rect(screen, WHITE, input_box, 2)

        draw_text(
            nickname if nickname else "Enter nickname",
            FONT,
            WHITE if nickname else GRAY,
            input_box.x + 8,
            input_box.y + 8
        )

        pygame.draw.rect(screen, GREEN, play_btn)
        draw_text("CONNECT", FONT, (0,0,0),
                  play_btn.centerx, play_btn.centery, center=True)

    elif state == "WAIT":
        draw_text("Waiting for another player...",
                  FONT_BIG, WHITE, WIDTH//2, HEIGHT//2, center=True)

    elif state == "GAME":

        # поле
        for i in range(1,3):
            pygame.draw.line(screen, WHITE,
                             (FIELD_X, FIELD_Y + i*SQUARE),
                             (FIELD_X+300, FIELD_Y + i*SQUARE), 4)

            pygame.draw.line(screen, WHITE,
                             (FIELD_X + i*SQUARE, FIELD_Y),
                             (FIELD_X + i*SQUARE, FIELD_Y+300), 4)

        # символи
        for r in range(3):
            for c in range(3):
                x = FIELD_X + c*SQUARE
                y = FIELD_Y + r*SQUARE

                if board[r][c] == "X":
                    pygame.draw.line(screen, RED,
                                     (x+20, y+20),
                                     (x+80, y+80), 6)
                    pygame.draw.line(screen, RED,
                                     (x+80, y+20),
                                     (x+20, y+80), 6)

                elif board[r][c] == "O":
                    pygame.draw.circle(screen, BLUE,
                                       (x+50, y+50), 30, 6)

        # ніки і рахунок
        my_color = RED if my_symbol == "X" else BLUE
        enemy_color = RED if enemy_symbol == "X" else BLUE

        draw_text(f"{nickname} (You)", FONT, my_color, 400, 60)
        draw_text(f"{enemy_nick}", FONT, enemy_color, 400, 100)

        draw_text(f"Score: {my_score} - {enemy_score}", FONT, WHITE, 400, 160)

        # ----- RESULT TEXT -----
        if game_result:
            if pygame.time.get_ticks() - result_time < 2000:
                color = GREEN if game_result == "YOU WON" else RED
                if game_result == "DRAW":
                    color = WHITE

                draw_text(game_result, FONT_BIG, color,
                          WIDTH//2, HEIGHT-40, center=True)
            else:
                game_result = None

    pygame.display.update()