from flask import Flask, request, jsonify, send_file
from flask_socketio import SocketIO
from flask_cors import CORS
from threading import Thread
from sklearn.preprocessing import StandardScaler
from utils.data import Data
from tf_evolution import train_model
from finta import TA
import pandas as pd
import numpy as np
import os
import json

import logging
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

app = Flask(__name__, static_folder='interface/build')
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
    # evolution params
    mrw = request.json["mutationRateW"]
    mrb = request.json["mutationRateB"]
    ms = request.json["mutationScale"]
    md = request.json["mutationDecay"]

    # population params
    size = request.json["popSize"]
    rotation = request.json["dataRotation"]

    ta_keys = request.json["taKeys"]
    hidden_layers = [int(x) for x in request.json["hiddenLayers"]]
    def reporter(name, data):
        socketio.emit(name, json.dumps(data), broadcast=True)

    ta, closing = data.get_training_segment()
    args = (hidden_layers, ta, closing, size, rotation, mrw, mrb, ms, md, reporter,)
    Thread(target=train_model, args=args).run()
    
    return jsonify({"message": "training started"})


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def app_page(path):
    # check if react build files exist
    if not os.path.isdir("interface/build"):
        return "App is running (dev/cli)"
    
    if path != "" and os.path.exists(f"interface/build/{path}"):
        return send_file(f"interface/build/{path}")

    return send_file("interface/build/index.html")


if __name__ == "__main__":
    socketio.run(app)
