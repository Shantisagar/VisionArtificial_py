"""
Path: src/controllers/app_controller.py
Controlador central para orquestar la inicialización de la configuración,
la recogida de datos y la activación de la UI.
"""

import sys
from src.config_manager import ConfigManager
from src.services.user_input_service import UserInputService
from src.views.console_view import ConsoleView
from src.views.gui_view import GUIView
from src.controllers.input_controller import InputController

class AppController:
    """Controlador central de la aplicación."""
    
    def __init__(self, 
                 config_manager: ConfigManager,
                 user_input_service: UserInputService, 
                 console_view: ConsoleView,
                 gui_view: GUIView,
                 logger=None):
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
        
        # Crear el controlador de entrada
        self.input_controller = InputController(
            console_view=console_view,
            user_input_service=user_input_service,
            config_manager=config_manager,
            logger=logger
        )
    
    def initialize(self) -> bool:
        """
        Inicializa los parámetros de la aplicación.
        
        Returns:
            True si la inicialización fue exitosa, False en caso contrario
        """
        try:
            # Usar el controlador de entrada para recoger todos los parámetros
            parametros = self.input_controller.collect_all_parameters()
            
            if parametros is None:
                return False
                
            # Extraer los valores validados en variables de clase
            self.grados_rotacion = parametros['grados_rotacion']
            self.pixels_por_mm = parametros['pixels_por_mm']
            self.altura = parametros['altura']
            self.horizontal = parametros['horizontal']
            
            # Actualizar la configuración con los nuevos valores
            self.input_controller.update_config_with_parameters(parametros)
            
            # Obtener las opciones de menú del controlador de video
            opciones_video = self.user_input_service.get_video_menu_options()
            
            # Seleccionar el modo de video según opción elegida
            opcion_video = self.console_view.mostrar_menu_fuente_video(opciones_video)
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
