import socketio

sio = socketio.Client()

@sio.event
def connect():
    print("Підключено до сервера")
    sio.emit("message", "Привіт з клієнта!")

@sio.event
def message(data):
    print("Від сервера:", data)
    sio.disconnect()

@sio.event
def disconnect():
    print("Відключено")

sio.connect("http://localhost:3000")
sio.wait()
