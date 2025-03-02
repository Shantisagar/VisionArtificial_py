"""
Path: src/controllers/gui_parameter_panel_controller.py
Controlador para el panel de parámetros en la interfaz gráfica.
"""

import logging
from typing import Dict, Callable, Optional, Any, Tuple
from src.controllers.parameter_model import ParameterModel
from src.controllers.parameter_event_controller import ParameterEventController

class GUIParameterPanelController:
    """Controlador para el panel de parámetros en la GUI."""
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.view = None
        # Inicializar la lógica de negocio en ParameterModel
        self.parameter_model = ParameterModel(logger)
        # Inicializar la gestión de eventos con el modelo
        self.event_controller = ParameterEventController(logger, self.parameter_model)

        self.external_callbacks = {
            'on_update_parameters': lambda: None,  # Changed default to a no-op lambda
            'on_reset_parameters': lambda: None,
            'on_save_as_default': lambda: None
        }
        self.parameter_ranges = {}  # Added missing attribute
        self.zoom = 1.0             # Predefine zoom attribute
        self.paper_color = ""       # Predefine paper_color attribute

    def set_view(self, view):
        "Establece la vista para el controlador."
        self.view = view
        self.view.set_callbacks(
            on_slider_change=self._on_slider_change,
            on_update_parameters=self._on_update_parameters_wrapper,
            on_reset_parameters=self._on_reset_parameters_wrapper,
            on_save_as_default=self._on_save_as_default_wrapper,
            on_entry_validate=self.validate_entry
        )
        # Si la vista tiene un layout, actualizar los rangos de los sliders
        if hasattr(self.view, 'layout'):
            self.view.layout.set_slider_ranges(self.parameter_ranges)

    def _on_update_parameters_wrapper(self) -> None:
        self.event_controller.on_update_parameters(self.view, None)
        if callable(self.external_callbacks.get('on_update_parameters')):
            self.external_callbacks['on_update_parameters']()

    def _on_reset_parameters_wrapper(self) -> None:
        if callable(self.external_callbacks.get('on_reset_parameters')):
            self.external_callbacks['on_reset_parameters']()

    def _on_save_as_default_wrapper(self) -> None:
        if callable(self.external_callbacks.get('on_save_as_default')):
            self.external_callbacks['on_save_as_default']()

    def _on_slider_change(self, param_name: str, value: float) -> None:
        self.event_controller.on_slider_change(param_name, value, self.view)

    def set_notifier(self, notifier):
        "Establece el notificador para el controlador."
        self.event_controller.notifier = notifier

    def set_parameters_update_callback(self, callback: Callable[[Dict[str, Any]], None]):
        "Establece el callback para la actualización de parámetros."
        self.event_controller.set_parameters_update_callback(callback)
        self.logger.debug("Callback de actualización de parámetros configurado")

    def set_external_callbacks(self,
                              on_update_parameters: Optional[Callable[[], None]] = None,
                              on_reset_parameters: Optional[Callable[[], None]] = None,
                              on_save_as_default: Optional[Callable[[], None]] = None):
        """
        Establece callbacks externos para eventos del panel.
        
        Args:
            on_update_parameters: Callback para actualizar parámetros
            on_reset_parameters: Callback para restaurar valores predeterminados
            on_save_as_default: Callback para guardar como valores predeterminados
        """
        if on_update_parameters:
            self.external_callbacks['on_update_parameters'] = on_update_parameters
        if on_reset_parameters:
            self.external_callbacks['on_reset_parameters'] = on_reset_parameters
        if on_save_as_default:
            self.external_callbacks['on_save_as_default'] = on_save_as_default

    def initialize(
        self,
        grados_rotacion: float,
        pixels_por_mm: float,
        altura: float,
        horizontal: float
    ) -> None:
        """
        Inicializa los valores en la vista.
        
        Args:
            grados_rotacion: Grados de rotación para la imagen
            pixels_por_mm: Relación de píxeles por milímetro
            altura: Ajuste vertical para la imagen
            horizontal: Ajuste horizontal para la imagen
        """
        if self.view:
            self.view.initialize(grados_rotacion, pixels_por_mm, altura, horizontal)

    def validate_entry(self, param_name: str, value: str) -> Tuple[bool, Optional[str]]:
        " Valida un valor de entrada para un parámetro. "
        valid, _error_msg = self.parameter_model.validate_value(param_name, value)
        if not valid:
            self.logger.warning(f"Validación fallida para {param_name}: {_error_msg}")
        else:
            # Actualizar el slider si fuera necesario vía la vista
            if self.view:
                self.view.update_slider_value(param_name, float(value))
        return valid, _error_msg

    def on_update_parameters(self, parameters: Optional[Dict[str, float]] = None) -> None:
        "Actualiza los parámetros con los valores actuales en la vista."
        self.event_controller.on_update_parameters(self.view, parameters)
        if callable(self.external_callbacks['on_update_parameters']):
            self.external_callbacks['on_update_parameters']()

    def on_reset_parameters(self) -> None:
        "Restablece los parámetros a valores predeterminados."
        if callable(self.external_callbacks['on_reset_parameters']):
            self.external_callbacks['on_reset_parameters']()
        self.logger.info("Parámetros restablecidos a valores predeterminados")
        if self.event_controller.notifier:
            self.event_controller.notifier.notify_info(
                "Parámetros restablecidos a valores predeterminados"
            )

    def on_save_as_default(self) -> None:
        " Guarda los parámetros actuales como valores predeterminados. "
        try:
            string_values = self.view.get_current_values()
            parameters = {}
            for param_name, value_str in string_values.items():
                valid, _error_msg = self.validate_entry(param_name, value_str)
                if not valid:
                    return
                parameters[param_name] = float(value_str)
            if callable(self.external_callbacks['on_save_as_default']):
                self.external_callbacks['on_save_as_default']()
            # Añadir flag especial para guardar como default
            parameters['save_as_default'] = True
            if self.event_controller.parameters_update_callback:
                self.event_controller.parameters_update_callback(parameters)
            self.logger.info("Parámetros guardados como valores predeterminados")
            if self.event_controller.notifier:
                self.event_controller.notifier.notify_info(
                    "Parámetros guardados como valores predeterminados"
                )
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.logger.error(f"Error al guardar parámetros como predeterminados: {e}")
            if self.event_controller.notifier:
                self.event_controller.notifier.notify_error(
                    f"Error al guardar parámetros como predeterminados: {e}"
                )

    def update_parameters_display(self, parameters: Dict[str, float]) -> None:
        """
        Actualiza la visualización de los parámetros en la interfaz.
        
        Args:
            parameters: Diccionario con los valores a mostrar
        """
        if self.view:
            self.view.update_parameters_display(parameters)

    def set_parameter_ranges(self, ranges: Dict[str, Tuple[float, float]]) -> None:
        """
        Establece los rangos permitidos para los parámetros.
        
        Args:
            ranges: Diccionario con los rangos para cada parámetro
        """
        self.parameter_ranges.update(ranges)

        # Actualizar también los rangos en el layout si ya está configurado
        if self.view and hasattr(self.view, 'layout'):
            self.view.layout.set_slider_ranges(self.parameter_ranges)
            self.logger.debug(f"Rangos de parámetros actualizados: {ranges}")

    def update_parameters(self, parameters):
        """
        Actualiza los parámetros del controlador.
        
        Args:
            parameters: Diccionario con los parámetros a actualizar
        """
        if 'zoom' in parameters:
            self.zoom = parameters['zoom']
        if 'paper_color' in parameters:
            self.paper_color = parameters['paper_color']

        self.view.update_parameters(parameters)
