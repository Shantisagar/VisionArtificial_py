"""
Path: src/main.py
Punto de entrada principal de la aplicación
Configura la aplicación e inicia la interfaz gráfica
"""

import logging
import sys
import os
from src.views.gui_view import GUIView
from src.controllers.app_controller import AppController

def configure_logging():
    """Configura el sistema de logging"""
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "vision_artificial.log")
    
    logger = logging.getLogger("vision_artificial")
    logger.setLevel(logging.INFO)
    
    # Handler para archivo
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Formato
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Agregar handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def main():
    """Función principal que inicia la aplicación"""
    try:
        # Configurar logging
        logger = configure_logging()
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
        
    except Exception as e:
        if 'logger' in locals():
            logger.exception(f"Error al iniciar la aplicación: {e}")
        else:
            print(f"Error crítico: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
