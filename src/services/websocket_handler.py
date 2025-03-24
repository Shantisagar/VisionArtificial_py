"""
Path: src/services/websocket_handler.py
Módulo para manejar eventos WebSocket.
"""

from flask_socketio import SocketIO

class WebSocketHandler:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.register_events()

    def register_events(self):
        @self.socketio.on('connect')
        def handle_connect():
            try:
                print("Cliente conectado")
            except Exception as e:
                print(f"Error en 'connect': {e}")

        @self.socketio.on('disconnect')
        def handle_disconnect():
            try:
                print("Cliente desconectado")
            except Exception as e:
                print(f"Error en 'disconnect': {e}")

        @self.socketio.on('message')
        def handle_message(data):
            try:
                print(f"Mensaje recibido: {data}")
                self.socketio.send("Mensaje recibido en el servidor")
            except Exception as e:
                print(f"Error en 'message': {e}")
