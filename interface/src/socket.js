import openSocket from 'socket.io-client';
const  socket = openSocket('http://127.0.0.1:5000/');

function genPriceUpdate(cb) {
  socket.on('genUpdate', data => cb(null, JSON.parse(data)));
}

function genGenUpdate(cb) {
  socket.on('genResults', data => cb(null, JSON.parse(data)));
}

function requestSample(cb) {
  const sampleSize = 100;
  socket.emit('sampleRequest', sampleSize);
  socket.on('sampleResults', data => cb(null, JSON.parse(data)));
}

export { genPriceUpdate, genGenUpdate, requestSample };
