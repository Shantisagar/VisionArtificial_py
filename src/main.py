"""
Path: src/main.py
Punto de entrada principal de la aplicación
Configura la aplicación e inicia la interfaz gráfica
"""

from src.views.gui_view import GUIView
from src.controllers.app_controller import AppController
from src.utils.simple_logger import LoggerService

logger = LoggerService()


def main():
    """Función principal que inicia la aplicación"""
    try:
        # Obtener logger centralizado
        logger.info("Iniciando aplicación de Visión Artificial...")

        # Crear controlador
        controller = AppController(logger)

        # Crear vista y configurarla
        view = GUIView(logger)

        # Este es el paso clave: el controlador configura la vista y establece los callbacks
        controller.setup_view(view)

        # Ejecutar la aplicación
        controller.run()

        logger.info("Aplicación finalizada correctamente")
    except Exception as e:
        logger.error(f"Error en la aplicación: {e}")
