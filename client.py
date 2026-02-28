import pygame
import socketio
import sys
import threading
import random

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
round_number = 1
MAX_ROUNDS = 3

board = [[None]*3 for _ in range(3)]

# ---------------- SOCKET EVENTS ----------------

@sio.on("countdown")
def on_countdown(data):
    global countdown_value
    countdown_value = data

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
    global board, current_turn, my_score, enemy_score

    board = data["board"]

    if "winner" in data:
        if data["winner"] == my_symbol:
            my_score += 1
        elif data["winner"] != "DRAW":
            enemy_score += 1

    if "turn" in data:
        current_turn = data["turn"]
@sio.event
def connect():
    global connection_status, state
    connection_status = True
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

def check_draw():
    for row in board:
        if None in row:
            return False
    return True

def reset_board():
    global board, current_turn
    board = [[None]*3 for _ in range(3)]
    current_turn = "X"

# ---------------- LOOP ----------------

while True:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # -------- HUB --------
        if state == "HUB":
            if event.type == pygame.MOUSEBUTTONDOWN:
                active_input = input_box.collidepoint(event.pos)

                if play_btn.collidepoint(event.pos) and nickname:
                    threading.Thread(
                        target=connect_to_server,
                        daemon=True
                    ).start()
                    state = "WAIT"

            if event.type == pygame.KEYDOWN and active_input:
                if event.key == pygame.K_BACKSPACE:
                    nickname = nickname[:-1]
                elif event.unicode.isprintable() and len(nickname) < 10:
                    nickname += event.unicode

        # -------- GAME --------
    if state == "GAME":
        if event.type == pygame.MOUSEBUTTONDOWN:
        
            x, y = event.pos
    
            if FIELD_X <= x <= FIELD_X+300 and FIELD_Y <= y <= FIELD_Y+300:
            
                c = (x - FIELD_X) // SQUARE
                r = (y - FIELD_Y) // SQUARE
    
                if current_turn == my_symbol:
                    sio.emit("make_move", {
                        "row": r,
                        "col": c
                    })

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
        draw_text("CONNECTED", FONT_BIG, GREEN, WIDTH//2, 80, center=True)

        if countdown_value:
            draw_text(f"Game starting in {countdown_value}",
                      FONT_BIG, WHITE, WIDTH//2, 150, center=True)
        else:
            draw_text("Waiting for another player...",
                      FONT, GRAY, WIDTH//2, 150, center=True)

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

        # ніки справа
        my_color = RED if my_symbol == "X" else BLUE
        enemy_color = RED if enemy_symbol == "X" else BLUE

        draw_text(f"{nickname} (Ви)", FONT, my_color, 400, 60)
        draw_text(f"{enemy_nick}", FONT, enemy_color, 400, 100)

        draw_text(f"Раунд: {round_number}/3", FONT, WHITE, 400, 150)
        draw_text(f"Рахунок: {my_score} - {enemy_score}", FONT, WHITE, 400, 190)

        if round_number > MAX_ROUNDS:
            draw_text("ГРА ЗАВЕРШЕНА",
                      FONT_BIG, GREEN,
                      WIDTH//2, HEIGHT-40, center=True)

    pygame.display.update()