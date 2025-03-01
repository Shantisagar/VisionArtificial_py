"""
Path: src/views/gui_parameter_panel.py
Clase adaptadora que integra la vista y el controlador del panel de parámetros.
"""

import tkinter as tk
import logging
from typing import Dict, Callable, Optional, Any

from src.views.gui_parameter_panel_view import GUIParameterPanelView
from src.controllers.gui_parameter_panel_controller import GUIParameterPanelController


class GUIParameterPanel:
    """
    Clase adaptadora que integra la vista y el controlador del panel de parámetros.
    Proporciona una interfaz compatible con el código existente.
    """

    def __init__(self, parent_frame: tk.Frame, logger: logging.Logger):
        """
        Inicializa el panel de parámetros integrando vista y controlador.
        
        Args:
            parent_frame: Frame padre para la vista
            logger: Logger para registrar eventos
        """
        # Guardar referencia al logger
        self.logger = logger
        
        # Crear la vista y el controlador
        self.view = GUIParameterPanelView(parent_frame, logger)
        self.controller = GUIParameterPanelController(logger)
        
        # Conectar vista y controlador
        self.controller.set_view(self.view)
        
        # Guardar referencia al notificador (se configurará después)
        self.notifier = None
        
    def set_notifier(self, notifier):
        """
        Establece el notificador para mostrar mensajes al usuario.
        
        Args:
            notifier: Objeto notificador con métodos notify_info, notify_warning, etc.
        """
        self.notifier = notifier
        # Pasar el notificador al controlador si lo soporta
        if hasattr(self.controller, 'set_notifier'):
            self.controller.set_notifier(notifier)
        
    def initialize(self, grados_rotacion: float, pixels_por_mm: float, altura: float, horizontal: float) -> None:
        """
        Inicializa el panel con los valores proporcionados.
        
        Args:
            grados_rotacion: Grados de rotación para la imagen
            pixels_por_mm: Relación de píxeles por milímetro
            altura: Ajuste vertical para la imagen
            horizontal: Ajuste horizontal para la imagen
        """
        self.controller.initialize(grados_rotacion, pixels_por_mm, altura, horizontal)
    
    def set_callbacks(self, 
                     on_update_parameters: Optional[Callable[[], None]] = None,
                     on_reset_parameters: Optional[Callable[[], None]] = None,
                     on_save_as_default: Optional[Callable[[], None]] = None) -> None:
        """
        Establece callbacks externos para eventos del panel.
        
        Args:
            on_update_parameters: Callback para actualizar parámetros
            on_reset_parameters: Callback para restaurar valores predeterminados
            on_save_as_default: Callback para guardar como valores predeterminados
        """
        self.controller.set_external_callbacks(
            on_update_parameters=on_update_parameters,
            on_reset_parameters=on_reset_parameters,
            on_save_as_default=on_save_as_default
        )
    
    def set_parameters_update_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Establece un callback para cuando se actualizan los parámetros.
        
        Args:
            callback: Función a llamar cuando se actualicen los parámetros
        """
        if hasattr(self.controller, 'set_parameters_update_callback'):
            self.controller.set_parameters_update_callback(callback)
            self.logger.debug("Callback de actualización de parámetros configurado")
        else:
            # Alternativa: almacenar el callback y usarlo en el método update_parameters
            self._parameters_update_callback = callback
            self.logger.warning("Controller no soporta set_parameters_update_callback, usando alternativa")
            
    def update_parameters(self, parameters: Dict[str, float]) -> None:
        """
        Actualiza los valores de los parámetros en la vista.
        
        Args:
            parameters: Diccionario con los valores a actualizar
        """
        self.update_parameters_display(parameters)
        
    def update_parameters_display(self, parameters: Dict[str, float]) -> None:
        """
        Actualiza la visualización de los parámetros en la interfaz.
        
        Args:
            parameters: Diccionario con los valores a mostrar
        """
        self.controller.update_parameters_display(parameters)
    
    def get_current_values(self) -> Dict[str, str]:
        """
        Obtiene los valores actuales desde la interfaz.
        
        Returns:
            Diccionario con los valores como strings
        """
        return self.view.get_current_values()
