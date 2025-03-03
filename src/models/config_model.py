"""
Path: src/models/config_model.py
Modelo para gestión de configuraciones de la aplicación.
Encargado de cargar y guardar parámetros de configuración.
"""

import json
import os
import logging
from typing import Dict, Any, Optional
from utils.logging.error_manager import handle_exception

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

        self.logger.debug(
            f"ConfigModel inicializado con archivo de configuración: {self.config_file}"
        )
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.logger.debug(f"Ruta base del proyecto: {base_path}")
        self.logger.debug(f"Directorio actual de trabajo: {os.getcwd()}")

    def load_config(self) -> Dict[str, Any]:
        """
        Carga la configuración desde el archivo JSON.
        
        Returns:
            Diccionario con la configuración
        """
        self.logger.debug(f"Intentando cargar configuración desde: {self.config_file}")
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.logger.debug("Archivo de configuración abierto correctamente")
                config = json.load(f)
                self.logger.debug(f"Configuración cargada: {config}")
                self.logger.info(f"Configuración cargada desde {self.config_file}")
                return config
        except FileNotFoundError as e:
            self.logger.debug(f"Archivo no encontrado: {self.config_file}")
            handle_exception(e, {
                "component": "ConfigModel", 
                "method": "load_config",
                "filepath": self.config_file
            })
            self.logger.warning(
                f"Archivo de configuración no encontrado: {self.config_file}. "
                "Se usarán valores predeterminados."
            )
            return self._get_default_config()
        except json.JSONDecodeError as e:
            self.logger.debug(f"Error de formato JSON: {e}, línea: {e.lineno}, columna: {e.colno}")
            handle_exception(e, {
                "component": "ConfigModel", 
                "method": "load_config",
                "filepath": self.config_file,
                "line": e.lineno,
                "column": e.colno
            })
            self.logger.error(f"Error al decodificar el archivo de configuración: {e}")
            return self._get_default_config()

    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        Guarda la configuración en el archivo JSON.
        
        Args:
            config: Diccionario con la configuración a guardar
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        self.logger.debug(f"Intentando guardar configuración: {config}")
        try:
            # Asegurar que existe el directorio
            config_dir = os.path.dirname(self.config_file)
            self.logger.debug(f"Verificando directorio de configuración: {config_dir}")
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            self.logger.debug("Directorio confirmado")

            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.logger.debug("Archivo abierto para escritura")
                json.dump(config, f, indent=4)
                self.logger.debug("Configuración escrita correctamente")

            self.logger.info(f"Configuración guardada en {self.config_file}")
            return True
        except (IOError, OSError) as e:
            self.logger.debug(f"Excepción al guardar: {type(e).__name__}, {str(e)}")
            handle_exception(e, {
                "component": "ConfigModel", 
                "method": "save_config",
                "filepath": self.config_file,
                "config": str(config)
            })
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
        self.logger.debug(f"Generando configuración predeterminada: {default_config}")
        self.logger.info("Usando configuración predeterminada")
        return default_config

    def get_parameters(self) -> Dict[str, Any]:
        """
        Obtiene los parámetros de la configuración.
        
        Returns:
            Diccionario con los parámetros
        """
        self.logger.debug("Solicitando parámetros de configuración")
        config = self.load_config()
        parameters = config.get("parameters", self._get_default_config()["parameters"])
        self.logger.debug(f"Parámetros obtenidos: {parameters}")
        return parameters

    def get_video_source(self) -> Any:
        """
        Obtiene la fuente de video de la configuración.
        
        Returns:
            Índice o URL de la fuente de video
        """
        self.logger.debug("Solicitando fuente de video")
        config = self.load_config()
        video_source = config.get("video_source", self._get_default_config()["video_source"])
        self.logger.debug(f"Fuente de video: {video_source}")
        return video_source
