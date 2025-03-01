"""
Path: src/controllers/gui_parameter_panel_controller.py
Controlador para el panel de parámetros de configuración.
Maneja la lógica de eventos, validación y actualizaciones de parámetros.
"""

import logging
from typing import Dict, Callable, Optional, Tuple

class GUIParameterPanelController:
    """
    Controlador responsable de la lógica de eventos del panel de parámetros.
    Separa la lógica de la presentación y gestiona la validación y actualización de parámetros.
    """

    def __init__(self, logger: logging.Logger):
        """
        Inicializa el controlador del panel de parámetros.
        
        Args:
            logger: Logger configurado para registrar eventos
        """
        self.logger = logger
        
        # Callback para cuando se actualicen los parámetros
        self.on_parameters_update: Optional[Callable[[Dict[str, float]], None]] = None

        # Variables para controlar si el cambio viene del slider o del campo de texto
        self.updating_from_slider = False
        self.updating_from_entry = False

        # Notificador para mensajes de error/información
        self.notifier = None
        
        # Vista asociada (se establecerá después de la inicialización)
        self.view = None
        
    def set_view(self, view):
        """
        Establece la vista asociada a este controlador.
        
        Args:
            view: La vista del panel de parámetros
        """
        self.view = view
        
    def set_notifier(self, notifier) -> None:
        """
        Establece el notificador para mensajes de error/información.
        
        Args:
            notifier: Objeto notificador que implementa métodos notify_error y notify_info
        """
        self.notifier = notifier

    def set_parameters_update_callback(self, callback: Callable[[Dict[str, float]], None]) -> None:
        """
        Establece el callback que se llamará cuando los parámetros se actualicen.
        
        Args:
            callback: Función a llamar con los nuevos parámetros
        """
        self.on_parameters_update = callback

    def on_slider_change(self, param_name: str, value: float) -> None:
        """
        Método para manejar cambios en cualquier slider.
        
        Args:
            param_name: Nombre del parámetro asociado al slider
            value: Nuevo valor del slider
        """
        if self.updating_from_entry:
            return

        try:
            self.updating_from_slider = True

            # Actualizar el parámetro en el modelo y procesamiento
            self._update_parameter(param_name, value)

            self.updating_from_slider = False

        except (ValueError, TypeError) as e:
            self.logger.error(f"Error de valor al actualizar desde slider {param_name}: {e}")
            self.updating_from_slider = False
    
    def validate_parameter_value(self, param_name: str, value: str) -> Tuple[bool, Optional[str]]:
        """
        Valida un valor de parámetro según sus rangos permitidos.
        
        Args:
            param_name: Nombre del parámetro a validar
            value: Valor a validar
            
        Returns:
            tuple: (es_válido, mensaje_error)
        """
        try:
            # Convertir a float para validación numérica
            float_value = float(value)
            
            # Validar según el tipo de parámetro y su rango
            if self.view and param_name in self.view.slider_ranges:
                min_val, max_val = self.view.slider_ranges[param_name]
                
                if min_val <= float_value <= max_val:
                    # Si es válido, actualizar el slider y el modelo
                    if not self.updating_from_slider:
                        self.updating_from_entry = True
                        self._update_parameter(param_name, float_value)
                        self.updating_from_entry = False
                    return True, None
                else:
                    return False, f"Valor fuera de rango ({min_val} a {max_val})"
            else:
                return False, f"Parámetro '{param_name}' no reconocido"
                
        except ValueError:
            return False, "Valor no válido. Debe ser un número."
            
    def _update_parameter(self, param_name: str, value: float) -> None:
        """
        Actualiza un parámetro individual y envía la actualización si hay un callback configurado.
        
        Args:
            param_name: Nombre del parámetro
            value: Nuevo valor
        """
        # Si hay un callback configurado, actualizamos
        if self.on_parameters_update:
            current_params = self.get_current_parameters()
            if current_params:
                current_params[param_name] = value  # Actualizar solo el parámetro cambiado
                self.on_parameters_update(current_params)
                
    def on_update_parameters(self) -> None:
        """Maneja el evento del botón de actualización de todos los parámetros"""
        try:
            # Obtener y validar los valores
            params = self.get_current_parameters()
            
            # Si hay un callback configurado, llamarlo con los nuevos parámetros
            if self.on_parameters_update and params:
                self.logger.info(f"Enviando actualización de parámetros desde panel: {params}")
                self.on_parameters_update(params)
                if self.notifier:
                    self.notifier.notify_info("Todos los parámetros actualizados correctamente")
            else:
                if not self.on_parameters_update:
                    self.logger.error("No hay callback configurado para actualización de parámetros")
                self.logger.warning("No se pudieron actualizar los parámetros - callback no configurado o parámetros inválidos")
                if self.notifier:
                    self.notifier.notify_error("No se pudieron aplicar los cambios")
            
        except ValueError as e:
            self.logger.error(f"Error en los parámetros: {str(e)}")
            if self.notifier:
                self.notifier.notify_error(f"Error en los parámetros: {str(e)}")
                
    def on_reset_parameters(self) -> None:
        """Restaura los valores predeterminados de los parámetros"""
        try:
            # Solicitar valores predeterminados al controlador
            if self.notifier:
                self.notifier.notify_info("Restaurando valores predeterminados...")
                
            # Solicitar valores predeterminados al controlador
            if self.on_parameters_update:
                self.on_parameters_update({'reset': True})
                
        except (ValueError, TypeError) as e:
            if self.notifier:
                self.notifier.notify_error(f"Error al restaurar valores predeterminados: {str(e)}")
                
    def on_save_as_default(self) -> None:
        """Guarda los valores actuales como nuevos valores predeterminados"""
        try:
            # Obtener y validar los valores
            params = self.get_current_parameters()
            
            if params:
                # Si hay un callback configurado, llamarlo con los nuevos parámetros y una flag especial
                if self.on_parameters_update:
                    params['save_as_default'] = True  # Flag especial para indicar guardar como predeterminados
                    self.on_parameters_update(params)
                    if self.notifier:
                        self.notifier.notify_info("Valores guardados como nuevos valores predeterminados")
                
        except ValueError as e:
            if self.notifier:
                self.notifier.notify_error(f"Error al guardar valores predeterminados: {str(e)}")
    
    def get_current_parameters(self) -> Dict[str, float]:
        """
        Obtiene los valores actuales de los parámetros desde la interfaz.
        
        Returns:
            Diccionario con los valores de los parámetros
            
        Raises:
            ValueError: Si algún valor no es válido
        """
        try:
            if self.view:
                values = self.view.get_current_values()
                
                return {
                    'grados_rotacion': float(values['grados_rotacion']),
                    'pixels_por_mm': float(values['pixels_por_mm']),
                    'altura': float(values['altura']),
                    'horizontal': float(values['horizontal'])
                }
            else:
                self.logger.error("No se ha establecido la vista para obtener los valores actuales")
                return {}
        except ValueError:
            raise ValueError("Todos los valores deben ser números válidos")
            
    def update_parameters(self, parameters: Dict[str, float]) -> None:
        """
        Actualiza los valores de los parámetros en la interfaz.
        
        Args:
            parameters: Diccionario con los nuevos valores
        """
        # Actualizar los controles de la UI a través de la vista
        if self.view:
            self.view.update_parameters_display(parameters)
            
            if self.notifier:
                self.notifier.notify_info("Parámetros actualizados correctamente")
