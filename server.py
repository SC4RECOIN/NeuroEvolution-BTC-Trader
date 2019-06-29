from flask import Flask, render_template
from flask_socketio import SocketIO
from threading import Thread
from utils.data import Data
import json

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
socketio = SocketIO(app)
data = Data('data/coinbase-1min.csv')

@socketio.on('welcome')
def handle_message(message):
    print('received message: ' + message)

@socketio.on('sampleRequest')
def handle_message(sample_size):
    d = data.get_rand_segment(sample_size)[:10]
    socketio.emit('sampleResults', d.to_json(), broadcast=True)

def send_data(name, data):
    socketio.emit(name, json.dumps(data), broadcast=True)

thread = Thread(target=socketio.run, args=(app,)).start()
