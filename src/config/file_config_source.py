"""
Path: src/config/file_config_source.py
Implementación de fuente de configuración basada en archivos JSON.
"""

import json
import os
from typing import Dict, Any
from src.config.config_source import ConfigSource
from utils.logging.logger_configurator import get_logger

class FileConfigSource(ConfigSource):
    """Implementación de ConfigSource para archivos JSON."""
    
    def __init__(self, file_path: str):
        """
        Inicializa la fuente de configuración con la ruta del archivo.
        
        Args:
            file_path: Ruta al archivo de configuración
        """
        self.file_path = file_path
        self.logger = get_logger()
    
    def load_config(self) -> Dict[str, Any]:
        """
        Carga la configuración desde un archivo JSON.
        
        Returns:
            Diccionario de configuración o diccionario vacío si hay error
        """
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as file:
                    return json.load(file)
            else:
                self.logger.warning(f"Archivo de configuración no encontrado: {self.file_path}")
                return {}
        except Exception as e:
            self.logger.error(f"Error al cargar configuración desde archivo: {e}")
            return {}
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """
        Guarda la configuración en un archivo JSON.
        
        Args:
            config: Diccionario de configuración a guardar
        """
        try:
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            
            with open(self.file_path, 'w') as file:
                json.dump(config, file, indent=4)
                
            self.logger.debug(f"Configuración guardada en {self.file_path}")
        except Exception as e:
            self.logger.error(f"Error al guardar configuración en archivo: {e}")
