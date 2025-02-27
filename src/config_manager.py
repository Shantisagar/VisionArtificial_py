"""
Gestor de configuración con soporte para múltiples fuentes y acceso unificado.
"""

import json
import os
import sys
from typing import Dict, Any, Optional
from utils.logging.logger_configurator import get_logger

class ConfigManager:
    """
    Gestor de configuración que permite trabajar con múltiples fuentes
    y provee una interfaz unificada para acceder a la configuración.
    """
    
    def __init__(self, config_path=None):
        """
        Inicializa el gestor de configuración con la ruta de configuración especificada.
        
        Args:
            config_path: Ruta al archivo de configuración o None
        """
        self.logger = get_logger()
        self.config_path = config_path
        self._config = {}
        if config_path:
            self._load_config()
    
    @classmethod
    def from_file(cls, file_path: str) -> 'ConfigManager':
        """
        Crea un ConfigManager con una fuente de archivo.
        
        Args:
            file_path: Ruta al archivo de configuración
            
        Returns:
            Una instancia de ConfigManager configurada
        """
        return cls(config_path=file_path)
    
    def _load_config(self) -> None:
        """Carga la configuración desde el archivo."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as file:
                    self._config = json.load(file)
            else:
                self.logger.warning(f"Archivo de configuración no encontrado: {self.config_path}")
        except Exception as e:
            self.logger.error(f"Error al cargar configuración desde archivo: {e}")
    
    def get_config(self) -> Dict[str, Any]:
        """
        Devuelve la configuración completa.
        
        Returns:
            Diccionario con la configuración actual
        """
        return self._config.copy()
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor específico de la configuración.
        
        Args:
            key: Clave de la configuración a recuperar
            default: Valor por defecto si la clave no existe
            
        Returns:
            El valor de la configuración o el valor por defecto
        """
        return self._config.get(key, default)
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """
        Actualiza la configuración y la persiste en el archivo.
        
        Args:
            new_config: Diccionario con los valores a actualizar
        """
        # Actualizar la configuración en memoria
        self._config.update(new_config)
        
        # Persistir en el archivo
        try:
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as file:
                json.dump(self._config, file, indent=4)
                
            self.logger.debug(f"Configuración guardada en {self.config_path}")
        except Exception as e:
            self.logger.error(f"Error al guardar configuración en archivo: {e}")
