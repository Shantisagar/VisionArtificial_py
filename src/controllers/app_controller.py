"""
Path: src/controllers/app_controller.py
Controlador central para orquestar la inicialización de la configuración,
la recogida de datos y la activación de la UI.
"""

import sys
import logging
from typing import Dict, Any
from src.config_manager import ConfigManager
from src.services.user_input_service import UserInputService
from src.views.console_view import ConsoleView
from src.views.gui_view import GUIView

class AppController:
    """Controlador central de la aplicación."""
    
    def __init__(self, 
                 config_manager: ConfigManager,
                 user_input_service: UserInputService, 
                 console_view: ConsoleView,
                 gui_view: GUIView,
                 logger: logging.Logger):
        """
        Inicializa el controlador con dependencias inyectadas.
        
        Args:
            config_manager: Gestor de configuración
            user_input_service: Servicio de entrada de usuario
            console_view: Vista para interacciones de consola
            gui_view: Vista para la interfaz gráfica
            logger: Logger configurado
        """
        self.config_manager = config_manager
        self.config = config_manager.get_config()
        self.user_input_service = user_input_service
        self.console_view = console_view
        self.gui_view = gui_view
        self.logger = logger
        self.video_url = None
        self.grados_rotacion = None
        self.pixels_por_mm = None
        self.altura = None
        self.horizontal = None
    
    def initialize(self) -> bool:
        """
        Inicializa los parámetros de la aplicación.
        
        Returns:
            True si la inicialización fue exitosa, False en caso contrario
        """
        try:
            # Recoger parámetros de entrada mediante la vista de consola
            parametros = self.console_view.solicitar_parametros_usuario(self.config)
            
            # Validar los parámetros recogidos
            if not self.user_input_service.validar_parametros(parametros):
                self.console_view.mostrar_error("Parámetros inválidos.")
                return False
                
            # Extraer los valores validados en variables de clase
            self.grados_rotacion, self.pixels_por_mm, self.altura, self.horizontal = (
                self.user_input_service.convertir_a_tupla_parametros(parametros)
            )
            
            # Actualizar la configuración con los nuevos valores
            nueva_config = {
                "grados_rotacion_default": self.grados_rotacion,
                "altura_default": self.altura,
                "horizontal_default": self.horizontal,
                "pixels_por_mm_default": self.pixels_por_mm
            }
            self.config_manager.update_config(nueva_config)
            
            # Seleccionar el modo de video según opción elegida
            opcion_video = self.console_view.mostrar_menu_fuente_video()
            self.video_url = self.user_input_service.procesar_opcion_video(opcion_video, self.config)
            
            if self.video_url is None:
                self.console_view.mostrar_error("Opción de video no válida.")
                return False
            
            return True
        except Exception as e:
            self.console_view.mostrar_error(f"Error al inicializar la aplicación: {e}")
            return False
    
    def run_ui(self) -> None:
        """Inicia la interfaz de usuario de la aplicación."""
        try:
            # Inicializar la UI gráfica con los parámetros recogidos
            self.gui_view.inicializar_ui(
                self.video_url, 
                self.grados_rotacion, 
                self.altura, 
                self.horizontal, 
                self.pixels_por_mm
            )
            
            # Ejecutar la UI
            self.gui_view.ejecutar()
        except Exception as e:
            self.console_view.mostrar_error(f"Error al iniciar la interfaz gráfica: {e}")
            sys.exit(1)
