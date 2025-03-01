"""
Path: src/config/config_source.py
Contrato para las fuentes de configuración que define una interfaz común.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class ConfigSource(ABC):
    """Interfaz abstracta para diferentes fuentes de configuración."""

    @abstractmethod
    def load_config(self) -> Dict[str, Any]:
        """
        Carga la configuración desde la fuente.
        
        Returns:
            Un diccionario con la configuración
        """
        pass

    @abstractmethod
    def save_config(self, config: Dict[str, Any]) -> None:
        """
        Guarda la configuración en la fuente.
        
        Args:
            config: Diccionario de configuración a guardar
        """
        pass
