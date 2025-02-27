"""
Path: src/main.py
Archivo de entrada para iniciar la aplicación separando la lógica de entrada,
configuración e inicialización de la UI.
"""

import sys
from utils.logging.logger_configurator import LoggerConfigurator, get_logger
from src.config_manager import ConfigManager
from src.controllers.app_controller import AppController
from src.services.user_input_service import UserInputService
from src.views.console_view import ConsoleView
from src.views.gui_view import GUIView

def main():
    """
    Función principal que utiliza el controlador central para iniciar la aplicación.
    """
    try:
        # Configurar el logger
        logger_configurator = LoggerConfigurator()
        logger = logger_configurator.configure()
        
        # Crear las dependencias necesarias
        config_manager = ConfigManager.from_file('src/config.json')  # Ruta correcta
        
        # Crear componentes del patrón MVC
        # Modelo: Servicios y gestores de datos
        user_input_service = UserInputService(logger)
        
        # Vistas: Componentes de UI
        console_view = ConsoleView(logger)
        gui_view = GUIView(logger)
        
        # Controlador: Orquesta la aplicación
        controller = AppController(
            config_manager=config_manager,
            user_input_service=user_input_service,
            console_view=console_view,
            gui_view=gui_view,
            logger=logger
        )
        
        # Inicializar parámetros y configuración
        if not controller.initialize():
            logger.error("No se pudo inicializar la aplicación correctamente.")
            sys.exit(1)
            
        # Iniciar la interfaz de usuario
        controller.run_ui()
        
    except Exception as e:
        # Usando get_logger para obtener el logger sin importar el contexto
        get_logger().error(f"Error fatal en la aplicación: {e}")
        sys.exit(1)
