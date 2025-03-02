"""
Path: src/models/config_model.py
Modelo para gestión de configuraciones de la aplicación.
Encargado de cargar y guardar parámetros de configuración.
"""

import json
import os
import logging
from typing import Dict, Any, Optional

class ConfigModel:
    """Clase responsable de gestionar la configuración de la aplicación."""

    def __init__(self, logger: logging.Logger, config_path: Optional[str] = None):
        """
        Inicializa el modelo de configuración.
        
        Args:
            logger: Logger configurado para registrar eventos
            config_path: Ruta al archivo de configuración (opcional)
        """
        self.logger = logger
        
        # Si no se especifica una ruta, usar la ruta predeterminada en el directorio config
        if config_path is None:
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.config_file = os.path.join(base_path, 'config', 'parameters.json')
        else:
            self.config_file = config_path
            
        self.logger.debug(f"Modelo de configuración inicializado con archivo: {self.config_file}")

    def load_config(self) -> Dict[str, Any]:
        """
        Carga la configuración desde el archivo JSON.
        
        Returns:
            Diccionario con la configuración
        """
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.logger.info(f"Configuración cargada desde {self.config_file}")
                return config
        except FileNotFoundError:
            self.logger.warning(
                f"Archivo de configuración no encontrado: {self.config_file}. "
                "Se usarán valores predeterminados."
            )
            return self._get_default_config()
        except json.JSONDecodeError as e:
            self.logger.error(f"Error al decodificar el archivo de configuración: {e}")
            return self._get_default_config()
        except Exception as e:
            self.logger.error(f"Error inesperado al cargar configuración: {e}")
            return self._get_default_config()

    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        Guarda la configuración en el archivo JSON.
        
        Args:
            config: Diccionario con la configuración a guardar
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        try:
            # Asegurar que existe el directorio
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)

            self.logger.info(f"Configuración guardada en {self.config_file}")
            return True
        except (IOError, OSError) as e:
            self.logger.error(f"Error al guardar configuración: {e}")
            return False

    def _get_default_config(self) -> Dict[str, Any]:
        """
        Retorna la configuración predeterminada.
        
        Returns:
            Diccionario con la configuración predeterminada
        """
        default_config = {
            "video_source": 0,
            "parameters": {
                "grados_rotacion": 0,
                "pixels_por_mm": 10,
                "altura": 0,
                "horizontal": 0
            }
        }
        self.logger.info("Usando configuración predeterminada")
        return default_config

    def get_parameters(self) -> Dict[str, Any]:
        """
        Obtiene los parámetros de la configuración.
        
        Returns:
            Diccionario con los parámetros
        """
        config = self.load_config()
        return config.get("parameters", self._get_default_config()["parameters"])

    def get_video_source(self) -> Any:
        """
        Obtiene la fuente de video de la configuración.
        
        Returns:
            Índice o URL de la fuente de video
        """
        config = self.load_config()
        return config.get("video_source", self._get_default_config()["video_source"])
