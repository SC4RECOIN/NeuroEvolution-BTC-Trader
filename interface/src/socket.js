import openSocket from 'socket.io-client';
const  socket = openSocket('http://127.0.0.1:5000/');

function onConnectionError(cb) {
  socket.on('connect_error', err => cb());
}

function genPriceUpdate(cb) {
  socket.on('genUpdate', data => cb(null, JSON.parse(data)));
}

function genGenUpdate(cb) {
  socket.on('genResults', data => cb(null, JSON.parse(data)));
}

function genGenProgress(cb) {
  socket.on('genProgress', data => cb(null, JSON.parse(data)));
}

export { 
  onConnectionError,
  genPriceUpdate, 
  genGenUpdate,
  genGenProgress
};
