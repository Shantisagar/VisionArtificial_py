"""
Controlador especializado en la recolección y validación de parámetros de entrada.
Implementa el patrón Mediator para coordinar la recolección de múltiples parámetros.
"""

import logging
from typing import Dict, Any, Tuple, Optional
from src.views.console_view import ConsoleView
from src.services.user_input_service import UserInputService
from src.config_manager import ConfigManager

class InputController:
    """
    Controlador que coordina la recolección y validación de parámetros de entrada del usuario.
    Separa la lógica de recolección (UI) de la validación (negocio) siguiendo el patrón Mediator.
    """

    def __init__(self,
                 console_view: ConsoleView,
                 user_input_service: UserInputService,
                 config_manager: ConfigManager,
                 logger: logging.Logger):
        """
        Inicializa el controlador con las dependencias necesarias.

        Args:
            console_view: Vista de consola para interacción con el usuario
            user_input_service: Servicio para validación de entradas
            config_manager: Gestor de configuración para obtener valores por defecto
            logger: Logger para registro de eventos
        """
        self.console_view = console_view
        self.user_input_service = user_input_service
        self.config_manager = config_manager
        self.logger = logger
        self.config = config_manager.get_config()

    def collect_all_parameters(self) -> Dict[str, float]:
        """
        Coordina la recolección y validación de todos los parámetros del usuario.

        Returns:
            Diccionario con todos los parámetros validados o None si hay errores
        """
        try:
            # Recoger cada parámetro individualmente
            parameters = {}

            # Recoger y validar grados de rotación
            grados_rotacion = self.console_view.solicitar_grados_rotacion(
                self.config["grados_rotacion_default"]
            )
            if not self.user_input_service.validar_grados_rotacion(grados_rotacion):
                self.console_view.mostrar_error("Grados de rotación inválidos.")
                return None
            parameters['grados_rotacion'] = grados_rotacion

            # Recoger y validar pixels por mm
            pixels_por_mm = self.console_view.solicitar_pixels_por_mm(
                self.config["pixels_por_mm_default"]
            )
            if not self.user_input_service.validar_pixels_por_mm(pixels_por_mm):
                self.console_view.mostrar_error("Valor de píxeles por mm inválido.")
                return None
            parameters['pixels_por_mm'] = pixels_por_mm

            # Recoger y validar altura
            altura = self.console_view.solicitar_altura(
                self.config["altura_default"]
            )
            if not self.user_input_service.validar_altura(altura):
                self.console_view.mostrar_error("Valor de altura inválido.")
                return None
            parameters['altura'] = altura

            # Recoger y validar desplazamiento horizontal
            horizontal = self.console_view.solicitar_horizontal(
                self.config["horizontal_default"]
            )
            if not self.user_input_service.validar_horizontal(horizontal):
                self.console_view.mostrar_error("Valor de desplazamiento horizontal inválido.")
                return None
            parameters['horizontal'] = horizontal

            # Validación global de todos los parámetros
            if not self.user_input_service.validar_parametros(parameters):
                self.console_view.mostrar_error("Combinación de parámetros inválida.")
                return None

            return parameters

        except ValueError as e:
            self.console_view.mostrar_error(f"Error al procesar valor: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Error inesperado recolectando parámetros: {e}")
            return None

    def update_config_with_parameters(self, parameters: Dict[str, float]) -> None:
        """
        Actualiza la configuración con los nuevos valores de parámetros.

        Args:
            parameters: Diccionario con los parámetros a actualizar
        """
        if parameters:
            nueva_config = {
                "grados_rotacion_default": parameters['grados_rotacion'],
                "pixels_por_mm_default": parameters['pixels_por_mm'],
                "altura_default": parameters['altura'],
                "horizontal_default": parameters['horizontal']
            }
            self.config_manager.update_config(nueva_config)
            self.logger.info("Configuración actualizada con nuevos parámetros.")
