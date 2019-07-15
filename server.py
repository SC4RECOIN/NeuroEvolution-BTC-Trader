from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from threading import Thread
from sklearn.preprocessing import StandardScaler
from utils.data import Data
from tf_evolution import train_model
from finta import TA
import pandas as pd
import numpy as np
import json

import logging
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)


print('Loading data and calculating TA...')
data = Data("data/coinbase-1min.csv", interval=5)


@app.route("/data-sample-request", methods=["POST"])
def sample_request():
    print('sample data request received')

    # update ohlc and TA to reflect interval
    inv = int(request.json["interval"])
    if inv != data.interval:
        data.interval = inv

    sample_size = request.json["sampleSize"]
    ohlc, ta = data.get_rand_segment(sample_size)
    close_col = ohlc.columns.get_loc('close')

    return jsonify({
        "closing": [{"price": p} for p in ohlc.values[:, close_col]],
        "ta": data.to_dict(ta)
    })


@app.route("/start-training", methods=["POST"])
def start_training():
    ta_keys = request.json["taKeys"]
    hidden_layers = [int(x) for x in request.json["hiddenLayers"]]
    def reporter(name, data):
        socketio.emit(name, json.dumps(data), broadcast=True)

    args = (hidden_layers, data.ta, data.ohlc, reporter,)
    Thread(target=train_model, args=args).run()
    return jsonify({"message": "training started"})


if __name__ == "__main__":
    socketio.run(app)
