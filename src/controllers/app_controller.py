"""
Path: src/controllers/app_controller.py
Controlador central para orquestar la inicialización de la configuración,
la recogida de datos y la activación de la UI.
"""

import sys
import tkinter as tk
import logging
from typing import Optional, Dict, Any
from src.video_stream import VideoStreamApp
from src.config_manager import ConfigManager
from src.services.user_input_service import UserInputService
from utils.logging.logger_configurator import LoggerConfigurator

logger = LoggerConfigurator().configure()

class AppController:
    """Controlador central de la aplicación."""
    
    def __init__(self, 
                 config_manager: ConfigManager,
                 user_input_service: UserInputService, 
                 logger: logging.Logger):
        """
        Inicializa el controlador con dependencias inyectadas.
        
        Args:
            config_manager: Gestor de configuración
            user_input_service: Servicio de entrada de usuario
            logger: Logger configurado
        """
        self.config_manager = config_manager
        self.config = config_manager.get_config()
        self.user_input_service = user_input_service
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
            # Recoger parámetros de entrada
            self.grados_rotacion, self.pixels_por_mm, self.altura, self.horizontal = (
                self.user_input_service.recoger_parametros_usuario(self.config)
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
            self.video_url = self.user_input_service.obtener_opcion_video(self.config)
            
            return True
        except Exception as e:
            self.logger.error(f"Error al inicializar la aplicación: {e}")
            return False
    
    def run_ui(self) -> None:
        """Inicia la interfaz de usuario de la aplicación."""
        try:
            root = tk.Tk()
            app = VideoStreamApp(
                root, 
                self.video_url, 
                self.grados_rotacion, 
                self.altura, 
                self.horizontal, 
                self.pixels_por_mm
            )
            app.run()
        except Exception as e:
            self.logger.error(f"Error al iniciar la interfaz gráfica: {e}")
            sys.exit(1)
