from aiohttp import web
from threading import Thread
import socketio
import json

sio = socketio.AsyncServer()

app = web.Application()
sio.attach(app)

@sio.on('connect')
def connect(sid, environ):
    print("connected:", sid)
    send_gen_update({'generation': 69})

async def send_gen_update(data):
    await sio.emit('update', json.dumps(data))

@sio.on('disconnect')
def disconnect(sid):
    print('disconnected:', sid)


web.run_app(app)
# Thread(target=web.run_app, args=(self.app))
