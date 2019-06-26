from flask import Flask, render_template
from flask_socketio import SocketIO
from threading import Thread
import json


app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('welcome')
def handle_message(message):
    print('received message: ' + message)

def send_data(data):
    socketio.emit('update', json.dumps(data), broadcast=True)


thread = Thread(target=socketio.run, args=(app,)).start()
