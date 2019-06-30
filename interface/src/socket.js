import openSocket from 'socket.io-client';
const  socket = openSocket('http://127.0.0.1:5000/');

function genPriceUpdate(cb) {
  socket.on('genUpdate', data => cb(null, JSON.parse(data)));
}

function genGenUpdate(cb) {
  socket.on('genResults', data => cb(null, JSON.parse(data)));
}

export { 
  genPriceUpdate, 
  genGenUpdate
};
