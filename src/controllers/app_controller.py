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
        Ahora simplemente carga los valores predeterminados de la configuración.
        
        Returns:
            True si la inicialización fue exitosa, False en caso contrario
        """
        try:
            # Cargar valores predeterminados de la configuración
            self.grados_rotacion = self.config.get("grados_rotacion_default", 0)
            self.pixels_por_mm = self.config.get("pixels_por_mm_default", 10)
            self.altura = self.config.get("altura_default", 0)
            self.horizontal = self.config.get("horizontal_default", 0)

            # Configurar la fuente de video (siempre webcam)
            self.video_url = self.user_input_service.get_webcam_url(self.config)

            if self.video_url is None:
                self.console_view.mostrar_error("No se pudo inicializar la cámara web.")
                return False
                
            self.logger.info("Parámetros inicializados con valores predeterminados")
            self.logger.info(f"Grados de rotación: {self.grados_rotacion}")
            self.logger.info(f"Píxeles por mm: {self.pixels_por_mm}")
            self.logger.info(f"Altura: {self.altura}")
            self.logger.info(f"Horizontal: {self.horizontal}")
            
            return True
        except (KeyError, ValueError, TypeError) as e:
            self.console_view.mostrar_error(f"Error al inicializar la aplicación: {e}")
            return False

    def run_ui(self) -> None:
        """Inicia la interfaz de usuario de la aplicación."""
        try:
            # Inicializar la UI gráfica con los parámetros predeterminados
            self.gui_view.inicializar_ui(
                self.video_url,
                self.grados_rotacion,
                self.altura,
                self.horizontal,
                self.pixels_por_mm
            )
            
            # Configurar el callback para recibir actualizaciones de parámetros desde la GUI
            self.gui_view.set_parameters_update_callback(self._on_parameters_update)

            # Ejecutar la UI
            self.gui_view.ejecutar()
        except (RuntimeError, ValueError, TypeError) as e:
            self.console_view.mostrar_error(f"Error al iniciar la interfaz gráfica: {e}")
            sys.exit(1)
            
    def _on_parameters_update(self, parameters: dict) -> None:
        """
        Callback para procesar las actualizaciones de parámetros desde la GUI.
        
        Args:
            parameters: Diccionario con los nuevos valores de parámetros
        """
        try:
            # Verificar si es una solicitud de reset (restaurar valores predeterminados)
            if 'reset' in parameters and parameters['reset']:
                # Cargar valores predeterminados de la configuración
                default_params = {
                    'grados_rotacion': self.config["grados_rotacion_default"],
                    'pixels_por_mm': self.config["pixels_por_mm_default"],
                    'altura': self.config["altura_default"],
                    'horizontal': self.config["horizontal_default"]
                }
                
                # Actualizar la interfaz con valores predeterminados
                self.gui_view.update_parameters(default_params)
                
                # Actualizar variables internas
                self.grados_rotacion = default_params['grados_rotacion']
                self.pixels_por_mm = default_params['pixels_por_mm']
                self.altura = default_params['altura']
                self.horizontal = default_params['horizontal']
                
                self.logger.info("Valores de parámetros restaurados a valores predeterminados")
                return
            
            # Verificar si es una solicitud para guardar como valores predeterminados
            if 'save_as_default' in parameters and parameters['save_as_default']:
                # Crear una copia limpia de los parámetros (sin la flag especial)
                clean_params = {k: v for k, v in parameters.items() if k != 'save_as_default'}
                
                # Validar los parámetros
                if not self.user_input_service.validar_parametros(clean_params):
                    self.gui_view.notifier.notify_error("Combinación de parámetros inválida para guardar como predeterminados")
                    return
                
                # Actualizar la configuración con los nuevos valores predeterminados
                default_config = {
                    "grados_rotacion_default": clean_params['grados_rotacion'],
                    "pixels_por_mm_default": clean_params['pixels_por_mm'],
                    "altura_default": clean_params['altura'],
                    "horizontal_default": clean_params['horizontal']
                }
                
                # Guardar en la configuración
                self.config_manager.update_config(default_config)
                
                # Actualizar la referencia local a la configuración
                self.config = self.config_manager.get_config()
                
                self.logger.info("Valores actuales guardados como nuevos valores predeterminados")
                return
                
            # Validar los parámetros usando el servicio de entrada
            if not self.user_input_service.validar_parametros(parameters):
                self.gui_view.notifier.notify_error("Combinación de parámetros inválida")
                return
                
            # Actualizar las variables internas
            self.grados_rotacion = parameters['grados_rotacion']
            self.pixels_por_mm = parameters['pixels_por_mm']
            self.altura = parameters['altura']
            self.horizontal = parameters['horizontal']
            
            # Actualizar la configuración con los nuevos valores
            self.input_controller.update_config_with_parameters(parameters)
            
            self.logger.info(f"Parámetros actualizados desde GUI: {parameters}")
            
        except (KeyError, ValueError) as e:
            self.gui_view.notifier.notify_error(f"Error al procesar parámetros: {str(e)}")
