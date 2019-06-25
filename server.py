from aiohttp import web
import socketio

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

@sio.on('connect')
def connect(sid, environ):
    print("connect", sid)

@sio.on('subscribeToTimer')
async def message(sid, data):
    print("react app connected to socket")
    await sio.emit('timer', 'Message sent from server')

@sio.on('disconnect')
def disconnect(sid):
    print('disconnect', sid)

def run():
    web.run_app(app)
