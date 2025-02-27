"""
Path: src/main.py
Archivo de entrada para iniciar la aplicación separando la lógica de entrada,
configuración e inicialización de la UI.
"""

import sys
from utils.logging.logger_configurator import LoggerConfigurator, get_logger
from src.config_manager import ConfigManager  # Usar la ruta correcta del módulo
from src.controllers.app_controller import AppController
from src.services.user_input_service import UserInputService

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
        user_input_service = UserInputService(logger)
        
        # Crear e inicializar el controlador con inyección de dependencias
        controller = AppController(
            config_manager=config_manager,
            user_input_service=user_input_service,
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
if __name__ == '__main__':    main()