"""
Path: src/controllers/parameter_model.py
Esta clase se encarga de almacenar y validar los parámetros,
separando la lógica de negocio de la gestión de eventos.
"""

from typing import Tuple  # Added to fix undefined Tuple

class ParameterModel:
    """
    Clase encargada de almacenar y validar los parámetros,
    separando la lógica de negocio de la gestión de eventos.
    """
    def __init__(self, logger):
        self.logger = logger
        self.current_parameters = {
            'grados_rotacion': 0.0,
            'pixels_por_mm': 1.0,
            'altura': 0.0,
            'horizontal': 0.0
        }
        self.parameter_ranges = {
            'grados_rotacion': (-180, 180),
            'pixels_por_mm': (0.1, 50),
            'altura': (-500, 500),
            'horizontal': (-500, 500)
        }

    def validate_value(self, param_name: str, value: str) -> Tuple[bool, str]:
        "Valida un valor para un parámetro"
        try:
            float_value = float(value)
            min_value, max_value = self.parameter_ranges[param_name]
            if not min_value <= float_value <= max_value:
                error_msg = f"El valor debe estar entre {min_value} y {max_value}"
                self.logger.warning(f"Validación fallida para {param_name}: {error_msg}")
                return False, error_msg
            return True, ""
        except ValueError:
            error_msg = "El valor debe ser un número"
            self.logger.warning(f"Validación fallida para {param_name}: {error_msg}")
            return False, error_msg

    def update_parameter(self, param_name: str, value: float):
        " Actualiza un parámetro con un valor"
        self.current_parameters[param_name] = value
        self.logger.debug(f"Parámetro {param_name} actualizado a {value}")
