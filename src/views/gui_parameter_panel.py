"""
Path: src/views/gui_parameter_panel.py
Panel para manejar los parámetros de configuración en la interfaz gráfica.
Extrae la responsabilidad de gestión de parámetros de GUIView.
"""

import tkinter as tk
import logging
from typing import Dict, Callable, Optional

from src.views.gui_parameter_panel_view import GUIParameterPanelView
from src.controllers.gui_parameter_panel_controller import GUIParameterPanelController

class GUIParameterPanel:
    """
    Clase responsable de la gestión de los parámetros en la interfaz gráfica.
    Mantiene compatibilidad mientras se completa la refactorización.
    Esta clase gradualmente transferirá responsabilidades al controlador.
    """

    def __init__(self, parent_frame: tk.Frame, logger: logging.Logger):
        """
        Inicializa el panel de parámetros.
        
        Args:
            parent_frame: Frame padre donde se crearán los controles
            logger: Logger configurado para registrar eventos
        """
        self.logger = logger
        
        # Crear la vista que manejará la interfaz gráfica
        self.view = GUIParameterPanelView(parent_frame, logger)
        
        # Crear el controlador que manejará la lógica de eventos y validación
        self.controller = GUIParameterPanelController(logger)
        
        # Configurar la relación entre vista y controlador
        self.controller.set_view(self.view)
        
        # Configurar los callbacks de la vista para que apunten al controlador
        self.view.set_callbacks(
            on_slider_change=self.controller.on_slider_change,
            on_update_parameters=self.controller.on_update_parameters,
            on_reset_parameters=self.controller.on_reset_parameters,
            on_save_as_default=self.controller.on_save_as_default,
            on_entry_validate=self.controller.validate_parameter_value
        )

    def set_notifier(self, notifier) -> None:
        """
        Establece el notificador para mensajes de error/información.
        
        Args:
            notifier: Objeto notificador que implementa métodos notify_error y notify_info
        """
        self.controller.set_notifier(notifier)

    def set_parameters_update_callback(self, callback: Callable[[Dict[str, float]], None]) -> None:
        """
        Establece el callback que se llamará cuando los parámetros se actualicen.
        
        Args:
            callback: Función a llamar con los nuevos parámetros
        """
        self.controller.set_parameters_update_callback(callback)

    def initialize(self, grados_rotacion: float, pixels_por_mm: float, altura: float, horizontal: float) -> None:
        """
        Inicializa los controles de parámetros con los valores proporcionados.
        
        Args:
            grados_rotacion: Grados de rotación para la imagen
            pixels_por_mm: Relación de píxeles por milímetro
            altura: Ajuste vertical para la imagen
            horizontal: Ajuste horizontal para la imagen
        """
        # Delegar la inicialización a la vista
        self.view.initialize(grados_rotacion, pixels_por_mm, altura, horizontal)

    def get_current_parameters(self) -> Dict[str, float]:
        """
        Obtiene los valores actuales de los parámetros desde la interfaz.
        
        Returns:
            Diccionario con los valores de los parámetros
            
        Raises:
            ValueError: Si algún valor no es válido
        """
        return self.controller.get_current_parameters()
            
    def update_parameters(self, parameters: Dict[str, float]) -> None:
        """
        Actualiza los valores de los parámetros en la interfaz.
        
        Args:
            parameters: Diccionario con los nuevos valores
        """
        self.controller.update_parameters(parameters)
