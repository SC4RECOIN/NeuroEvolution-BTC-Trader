from flask import Flask, render_template
from flask_socketio import SocketIO
from threading import Thread
from utils.data import Data
from finta import TA
import pandas as pd
import numpy as np
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
    d = data.get_rand_segment(sample_size)
    socketio.emit('sampleResults', d.to_json(), broadcast=True)

@socketio.on('taRequest')
def handle_message(ohlc_data):
    ta = TA.RSI(pd.DataFrame(ohlc_data))
    ta[np.isnan(ta)] = 0
    ta[np.isinf(ta)] = 0
    socketio.emit('taResults', ta.to_json(), broadcast=True)

def send_data(name, data):
    socketio.emit(name, json.dumps(data), broadcast=True)

thread = Thread(target=socketio.run, args=(app,)).start()
