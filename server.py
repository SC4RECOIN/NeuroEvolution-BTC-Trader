from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
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
CORS(app)
socketio = SocketIO(app)
data = Data('data/coinbase-1min.csv')


@app.route('/ta-request', methods=['POST'])
def get_sample_data():
    ohlc_data = request.json['ohlcData']
    ta = TA.RSI(pd.DataFrame(ohlc_data))
    ta[np.isnan(ta)] = 0
    ta[np.isinf(ta)] = 0
    return ta.to_json()


@app.route('/sample-request', methods=['POST'])
def sample_request():
    sample_size = request.json['sampleSize']
    d = data.get_rand_segment(sample_size)
    return d.to_json()


def send_data(name, data):
    socketio.emit(name, json.dumps(data), broadcast=True)


socketio.run(app)
