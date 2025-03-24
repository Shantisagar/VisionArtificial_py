"""
Path: run.py
Archivo de entrada simplificado para iniciar la aplicación.
"""

import os
from flask_socketio import SocketIO
from src.websocket_server import app, socketio
from src.controllers.app_controller import AppController
from src.utils.simple_logger import LoggerService

if __name__ == "__main__":
    os.system("cls")

    # Inicializar el logger
    logger = LoggerService()

    # Inicializar AppController con SocketIO
    app_controller = AppController(logger, socketio)

    # Ejecutar el servidor
    socketio.run(app, host="0.0.0.0", port=5000)
