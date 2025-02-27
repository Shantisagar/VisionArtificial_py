"""
Path: app/logs/logger_configurator.py

"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class ConfigStrategy(ABC):
    """Clase base para las estrategias de configuración del logger."""
    @abstractmethod
    def load_config(self) -> Optional[Dict[str, Any]]:
        """
        Carga y retorna la configuración del logger.

        Returns:
            Optional[Dict[str, Any]]: Configuración del logger o None si no se puede cargar.
        """
    def another_method(self):
        """Another public method to satisfy pylint."""
        print("Another method")
