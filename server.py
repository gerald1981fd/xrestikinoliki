import socketio
import eventlet

sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)

players = {}          # sid -> nickname
symbols = {}          # sid -> X/O
board = [[None]*3 for _ in range(3)]
current_turn = None

# ---------------- FUNCTIONS ----------------

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

# ---------------- SOCKET ----------------

@sio.event
def connect(sid, environ):
    print("Connected:", sid)

@sio.event
def disconnect(sid):
    if sid in players:
        print("Disconnected:", players[sid])
        del players[sid]
        if sid in symbols:
            del symbols[sid]

@sio.on("set_nickname")
def set_nickname(sid, nick):
    players[sid] = nick

    if len(players) == 2:
        sids = list(players.keys())
        symbols[sids[0]] = "X"
        symbols[sids[1]] = "O"

        reset_board()

        for s in sids:
            sio.emit("game_start", {
                "symbol": symbols[s],
                "enemy": players[sids[1] if s == sids[0] else sids[0]],
                "turn": current_turn
            }, to=s)

@sio.on("make_move")
def make_move(sid, data):
    global current_turn

    r = data["row"]
    c = data["col"]

    if sid not in symbols:
        return

    if symbols[sid] != current_turn:
        return

    if board[r][c] is not None:
        return

    board[r][c] = current_turn

    if check_win(current_turn):
        sio.emit("board_update", {
            "board": board,
            "winner": current_turn
        })
        reset_board()
        return

    if check_draw():
        sio.emit("board_update", {
            "board": board,
            "winner": "DRAW"
        })
        reset_board()
        return

    current_turn = "O" if current_turn == "X" else "X"

    sio.emit("board_update", {
        "board": board,
        "turn": current_turn
    })

print("Server running on 3000")
eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 3000)), app)