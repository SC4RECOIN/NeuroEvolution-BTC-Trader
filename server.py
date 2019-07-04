from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from threading import Thread
from sklearn.preprocessing import StandardScaler
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
    ohlc = pd.DataFrame(request.json['ohlcData'])
    ta = [
        TA.ER(ohlc),
        TA.PPO(ohlc)["HISTO"],
        TA.STOCHRSI(ohlc),
        TA.ADX(ohlc),
        TA.RSI(ohlc),
        TA.COPP(ohlc),
        TA.CCI(ohlc),
        TA.CHAIKIN(ohlc),
        TA.FISH(ohlc)
    ]

    ta = np.array(ta).transpose()
    ta[np.isnan(ta)] = 0
    ta[np.isinf(ta)] = 0

    # scale them to the same range
    scaler = StandardScaler()
    scaler.fit(ta)
    ta = scaler.transform(ta)
    
    # reformat for rechart.js
    return jsonify({
        "results": [{
            "ER": row[0],
            "PPO": row[1],
            "STOCHRSI": row[2],
            "ADX": row[3],
            "RSI": row[4],
            "COPP": row[5],
            "CCI": row[6],
            "CHAIKIN": row[7],
            "FISH": row[8],
        } for row in ta
    ]})


@app.route('/sample-request', methods=['POST'])
def sample_request():
    sample_size = request.json['sampleSize']
    d = data.get_rand_segment(sample_size)
    return d.to_json()


@app.route('/start-training', methods=['GET'])
def sample_request():
    return jsonify({"message": "training started"})


def send_data(name, data):
    socketio.emit(name, json.dumps(data), broadcast=True)


socketio.run(app)
