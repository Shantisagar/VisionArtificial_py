"""
Path: src/controllers/gui_parameter_panel_controller.py
Controlador para el panel de parámetros en la interfaz gráfica.
"""

import logging
from typing import Dict, Callable, Optional, Any, Tuple

class GUIParameterPanelController:
    """Controlador para el panel de parámetros."""

    def __init__(self, logger: logging.Logger):
        """
        Inicializa el controlador del panel de parámetros.
        
        Args:
            logger: Logger para registrar eventos
        """
        self.logger = logger
        self.view = None
        self.notifier = None
        
        # Parámetros actuales
        self.current_parameters = {
            'grados_rotacion': 0.0,
            'pixels_por_mm': 1.0,
            'altura': 0.0,
            'horizontal': 0.0
        }
        
        # Rangos para los parámetros (deben coincidir con ParameterPanelLayout.slider_ranges)
        self.parameter_ranges = {
            'grados_rotacion': (-180, 180),
            'pixels_por_mm': (0.1, 50),
            'altura': (-500, 500),
            'horizontal': (-500, 500)
        }
        
        # Callbacks externos
        self.parameters_update_callback = None
        self.external_callbacks = {
            'on_update_parameters': None,
            'on_reset_parameters': None,
            'on_save_as_default': None
        }
        
    def set_view(self, view):
        """
        Establece la vista asociada al controlador.
        
        Args:
            view: Vista del panel de parámetros
        """
        self.view = view
        
        # Configurar callbacks en la vista
        self.view.set_callbacks(
            on_slider_change=self.on_slider_change,
            on_update_parameters=self.on_update_parameters,
            on_reset_parameters=self.on_reset_parameters,
            on_save_as_default=self.on_save_as_default,
            on_entry_validate=self.validate_entry
        )
        
        # Si la vista tiene un layout, actualizar los rangos de los sliders
        if hasattr(self.view, 'layout'):
            self.view.layout.set_slider_ranges(self.parameter_ranges)
        
    def set_notifier(self, notifier):
        """
        Establece el notificador para mostrar mensajes al usuario.
        
        Args:
            notifier: Objeto notificador
        """
        self.notifier = notifier
        
    def set_parameters_update_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Establece un callback para cuando se actualizan los parámetros.
        
        Args:
            callback: Función a llamar cuando se actualicen los parámetros
        """
        self.parameters_update_callback = callback
        
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
    
    def initialize(self, grados_rotacion: float, pixels_por_mm: float, altura: float, horizontal: float) -> None:
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
    
    def on_slider_change(self, param_name: str, value: float) -> None:
        """
        Maneja los cambios en los sliders.
        
        Args:
            param_name: Nombre del parámetro asociado al slider
            value: Nuevo valor del slider
        """
        try:
            # Actualizar el campo de texto correspondiente en la vista
            if self.view:
                self.view.update_parameter_text(param_name, str(value))
            self.logger.debug(f"Slider cambiado: {param_name} = {value}")
            
            # Aplicar el cambio inmediatamente
            self._apply_single_parameter_change(param_name, value)
            
        except Exception as e:
            self.logger.error(f"Error al manejar cambio de slider para {param_name}: {e}")
            if self.notifier:
                self.notifier.notify_error(f"Error al ajustar {param_name}: {e}")
    
    def _apply_single_parameter_change(self, param_name: str, value: float) -> None:
        """
        Aplica el cambio de un único parámetro.
        
        Args:
            param_name: Nombre del parámetro a actualizar
            value: Nuevo valor como float
        """
        # Crear un diccionario con solo este parámetro
        params = {param_name: value}
        
        # Notificar el cambio a través del callback si existe
        if self.parameters_update_callback:
            self.parameters_update_callback(params)
            self.logger.debug(f"Parámetro {param_name} actualizado a {value}")
    
    def validate_entry(self, param_name: str, value: str) -> Tuple[bool, Optional[str]]:
        """
        Valida el valor ingresado en un campo de entrada.
        
        Args:
            param_name: Nombre del parámetro a validar
            value: Valor a validar
            
        Returns:
            Tuple con un booleano (válido/inválido) y un mensaje opcional de error
        """
        try:
            # Convertir a float para validar
            float_value = float(value)
            
            # Verificar si está dentro del rango permitido
            min_value, max_value = self.parameter_ranges[param_name]
            
            if float_value < min_value or float_value > max_value:
                error_msg = f"El valor debe estar entre {min_value} y {max_value}"
                self.logger.warning(f"Validación fallida para {param_name}: {error_msg}")
                if self.notifier:
                    self.notifier.notify_warning(f"Valor inválido: {error_msg}")
                return False, error_msg
            
            # Si el valor es válido, actualizar el slider correspondiente
            if self.view:
                self.view.update_slider_value(param_name, float_value)
                
            # Aplicar el cambio inmediatamente
            self._apply_single_parameter_change(param_name, float_value)
            
            return True, None
            
        except ValueError:
            error_msg = "El valor debe ser un número"
            self.logger.warning(f"Validación fallida para {param_name}: {error_msg}")
            if self.notifier:
                self.notifier.notify_warning(f"Valor inválido: {error_msg}")
            return False, error_msg
    
    def on_update_parameters(self) -> None:
        """Maneja el evento del botón de aplicar cambios."""
        try:
            if not self.view:
                self.logger.error("No hay vista configurada")
                return
                
            # Obtener valores actuales desde la vista
            string_values = self.view.get_current_values()
            
            # Convertir a valores float para procesamiento
            float_values = {}
            
            # Validar todos los valores antes de actualizar
            all_valid = True
            for param_name, value_str in string_values.items():
                valid, _ = self.validate_entry(param_name, value_str)
                if not valid:
                    all_valid = False
                else:
                    # Si es válido, convertir a float para el procesamiento
                    float_values[param_name] = float(value_str)
            
            if all_valid:
                # Llamar al callback externo de actualización si existe
                if self.external_callbacks['on_update_parameters']:
                    self.external_callbacks['on_update_parameters']()
                
                # Notificar a través del callback de parámetros si existe
                if self.parameters_update_callback:
                    self.parameters_update_callback(float_values)
                
                self.logger.info("Parámetros actualizados correctamente")
                if self.notifier:
                    self.notifier.notify_info("Parámetros actualizados correctamente")
            else:
                self.logger.warning("No se pudieron actualizar los parámetros debido a valores inválidos")
                if self.notifier:
                    self.notifier.notify_warning("No se pudieron actualizar los parámetros debido a valores inválidos")
        except Exception as e:
            self.logger.error(f"Error al actualizar parámetros: {e}")
            if self.notifier:
                self.notifier.notify_error(f"Error al actualizar parámetros: {e}")
    
    def on_reset_parameters(self) -> None:
        """Maneja el evento del botón de restaurar valores predeterminados."""
        if self.external_callbacks['on_reset_parameters']:
            self.external_callbacks['on_reset_parameters']()
            self.logger.info("Parámetros restablecidos a valores predeterminados")
            if self.notifier:
                self.notifier.notify_info("Parámetros restablecidos a valores predeterminados")
    
    def on_save_as_default(self) -> None:
        """Maneja el evento del botón de guardar como valores predeterminados."""
        try:
            if not self.view:
                self.logger.error("No hay vista configurada")
                return
                
            # Obtener valores actuales desde la vista
            string_values = self.view.get_current_values()
            
            # Convertir a valores float para procesamiento
            float_values = {}
            
            # Validar todos los valores antes de guardar
            all_valid = True
            for param_name, value_str in string_values.items():
                valid, _ = self.validate_entry(param_name, value_str)
                if not valid:
                    all_valid = False
                else:
                    # Si es válido, convertir a float para el procesamiento
                    float_values[param_name] = float(value_str)
            
            if all_valid:
                if self.external_callbacks['on_save_as_default']:
                    self.external_callbacks['on_save_as_default']()
                
                # Notificar también mediante el callback de parámetros si existe
                if self.parameters_update_callback:
                    # Añadir flag especial para indicar que se guarda como default
                    float_values['save_as_default'] = True
                    self.parameters_update_callback(float_values)
                
                self.logger.info("Parámetros guardados como valores predeterminados")
                if self.notifier:
                    self.notifier.notify_info("Parámetros guardados como valores predeterminados")
            else:
                self.logger.warning("No se pudieron guardar los parámetros debido a valores inválidos")
                if self.notifier:
                    self.notifier.notify_warning("No se pudieron guardar los parámetros debido a valores inválidos")
        except Exception as e:
            self.logger.error(f"Error al guardar parámetros como predeterminados: {e}")
            if self.notifier:
                self.notifier.notify_error(f"Error al guardar parámetros como predeterminados: {e}")
    
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
