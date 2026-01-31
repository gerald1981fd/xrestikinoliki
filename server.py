import socketio
import eventlet

players = []
sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    print("Клієнт підключився:", sid)

@sio.event
def message(sid, data):
    print("Отримано:", data)
    sio.emit("message", "Привіт з сервера!", to=sid)

@sio.event
def disconnect(sid):
    print("Клієнт відключився:", sid)


@sio.on("set_nickname")
def set_nickname(nick):
    players.append(nick)
    socketio.emit("players_update", players)

print("Сервер запущено на порту 3000")
eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 3000)), app)
