"""
Path: src/main.py
Archivo de entrada para iniciar la aplicación separando la lógica de entrada,
configuración e inicialización de la UI.
"""

import sys
import logging
from utils.logging.logger_configurator import LoggerConfigurator
from utils.error_handling import (
    get_error_handler, ErrorSeverity, error_context,
    handle_exceptions
)
from src.config_manager import ConfigManager
from src.controllers.app_controller import AppController
from src.services.user_input_service import UserInputService
from src.views.console_view import ConsoleView
from src.views.gui_view import GUIView


@handle_exceptions(severity=ErrorSeverity.FATAL)
def setup_dependencies():
    """
    Configura e inicializa las dependencias de la aplicación.
    
    Returns:
        Tupla con todas las dependencias inicializadas
    """
    # Configurar el logger con inyección de parámetros
    logger_configurator = LoggerConfigurator(log_level=logging.INFO)
    logger = logger_configurator.configure()

    # Crear las dependencias necesarias con inyección del logger
    with error_context(
        severity=ErrorSeverity.CRITICAL,
        context={"component": "ConfigManager"},
        reraise=True
    ):
        config_manager = ConfigManager.from_file('src/config.json', logger=logger)

    # Crear componentes del patrón MVC con inyección de dependencias
    user_input_service = UserInputService(logger)
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

    return controller, logger


@handle_exceptions(severity=ErrorSeverity.FATAL)
def main():
    """
    Función principal que utiliza el controlador central para iniciar la aplicación.
    """
    # Inicializar el manejador de errores global
    # Se configurará automáticamente cuando se inicialice el logger
    get_error_handler()

    # Configurar dependencias
    controller, logger = setup_dependencies()

    # Inicializar parámetros y configuración
    with error_context(severity=ErrorSeverity.CRITICAL, context={"phase": "initialization"}):
        if not controller.initialize():
            logger.error("No se pudo inicializar la aplicación correctamente.")
            sys.exit(1)

    # Iniciar la interfaz de usuario
    with error_context(severity=ErrorSeverity.CRITICAL, context={"phase": "ui_execution"}):
        controller.run_ui()


if __name__ == "__main__":
    main()
