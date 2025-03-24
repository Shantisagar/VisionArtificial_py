"""
Path: src/websocket_server.py
"""

from flask import Flask
from flask_socketio import SocketIO
from threading import Thread
import time
from src.utils.simple_logger import LoggerService

logger = LoggerService()
# Crear la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

# Configurar SocketIO
socketio = SocketIO(app)

def periodic_event():
    """Envía un evento al cliente cada 5 segundos."""
    while True:
        socketio.emit('server_event', {'data': 'Evento periódico desde el servidor'})
        time.sleep(5)
