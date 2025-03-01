"""
Path: src/main.py
Punto de entrada principal de la aplicación
Configura la aplicación e inicia la interfaz gráfica
"""

import sys
import os
from src.views.gui_view import GUIView
from src.controllers.app_controller import AppController
from utils.logging.dependency_injection import get_logger

def main():
    """Función principal que inicia la aplicación"""
    try:
        # Obtener logger centralizado
        logger = get_logger()
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
        return 0

    except (OSError, RuntimeError) as e:
        # Intentar usar el logger si está disponible
        try:
            logger = get_logger()
            logger.exception(f"Error al iniciar la aplicación: {e}")
        except:
            # Fallback a print si no se pudo obtener el logger
            print(f"Error crítico: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
