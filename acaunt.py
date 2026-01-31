import pygame
import socketio
import sys

# -------- socketio --------
sio = socketio.Client()
nickname = ""
connection_status = False

@sio.event
def connect():
    global connection_status
    connection_status = True
    print("✅ Connected to server")

    sio.emit("set_nickname", nickname)

@sio.event
def disconnect():
    print("❌ Disconnected")

# -------- pygame --------
pygame.init()

WIDTH, HEIGHT = 500, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("HUB")

FONT_BIG = pygame.font.SysFont(None, 48)
FONT = pygame.font.SysFont(None, 28)

WHITE = (255,255,255)
GRAY = (180,180,180)
GREEN = (50,200,100)
BG = (30,30,30)
INPUT_BG = (50,50,50)
INPUT_ACTIVE = (100,200,255)

input_box = pygame.Rect(150, 120, 200, 40)
play_btn = pygame.Rect(175, 190, 150, 45)

active_input = False
connected = False

def draw_text(text, font, color, x, y, center=False):
    img = font.render(text, True, color)
    rect = img.get_rect(center=(x,y)) if center else img.get_rect(topleft=(x,y))
    screen.blit(img, rect)

# -------- LOOP --------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            active_input = input_box.collidepoint(event.pos)

            if play_btn.collidepoint(event.pos):
                if nickname and not connected:
                    sio.connect("http://localhost:3000")
                    connected = True

        if event.type == pygame.KEYDOWN and active_input:
            if event.key == pygame.K_BACKSPACE:
                nickname = nickname[:-1]
            elif event.unicode.isprintable() and not event.unicode.isspace():
                if len(nickname) < 10:
                    nickname += event.unicode

    if connection_status:
        # гра
        while connection_status:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            screen.fill(BG)
            draw_text("Connected!", FONT, GREEN, WIDTH//2, HEIGHT - 40, center=True)

            pygame.display.update()
    # ---- DRAW ----
    screen.fill(BG)

    draw_text("HUB", FONT_BIG, WHITE, WIDTH//2, 40, center=True)

    # input
    pygame.draw.rect(screen, INPUT_BG, input_box)
    pygame.draw.rect(
        screen,
        INPUT_ACTIVE if active_input else WHITE,
        input_box,
        2
    )

    draw_text(
        nickname if nickname else "Enter nickname",
        FONT,
        WHITE if nickname else GRAY,
        input_box.x + 8,
        input_box.y + 8
    )

    # button
    pygame.draw.rect(screen, GREEN, play_btn, border_radius=8)
    draw_text("CONNECT", FONT, (0,0,0),
              play_btn.centerx, play_btn.centery, center=True)
    

    pygame.display.update()
