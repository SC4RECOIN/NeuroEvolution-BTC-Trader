import openSocket from 'socket.io-client';
const  socket = openSocket('http://127.0.0.1:5000/');

function subscribeToTimer(cb) {
  socket.on('update', data => cb(null, JSON.parse(data)));
  socket.emit('welcome', 'hello')
}

export { subscribeToTimer };
