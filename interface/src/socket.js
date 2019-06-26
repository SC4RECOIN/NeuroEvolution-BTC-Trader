import openSocket from 'socket.io-client';
const  socket = openSocket('http://localhost:8080');

function subscribeToTimer(cb) {
  socket.on('update', data => cb(null, JSON.parse(data)));
}

export { subscribeToTimer };
