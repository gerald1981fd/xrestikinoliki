import socketio
import eventlet
import time
import threading

players = {}
sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)

# ---------- CONNECT ----------
@sio.event
def connect(sid, environ):
    print("Підключився:", sid)

# ---------- DISCONNECT ----------
@sio.event
def disconnect(sid):
    if sid in players:
        print("Вийшов:", players[sid])
        del players[sid]
        sio.emit("players_update", list(players.values()))

# ---------- SET NICK ----------
@sio.on("set_nickname")
def set_nickname(sid, nick):
    players[sid] = nick
    sio.emit("players_update", list(players.values()))

    if len(players) == 2:
        threading.Thread(target=start_countdown).start()

# ---------- COUNTDOWN ----------
def start_countdown():
    for i in range(3, 0, -1):
        sio.emit("countdown", i)
        time.sleep(1)

    sio.emit("start_game")

print("Сервер запущено на 3000")
eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 3000)), app)
