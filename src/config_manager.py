"""
Path: VisionArtificial\config_manager.py
Este módulo se encarga de leer y actualizar la configuración de la aplicación desde un archivo JSON.
"""

import json
import os
import sys
from utils.logging.logger_configurator import LoggerConfigurator

# Configuración del logger
logger = LoggerConfigurator().configure()

DEFAULT_CONFIG = {
    "grados_rotacion_default": 0.0,
    "horizontal_default": 0.0,
    "altura_default": 0.0,
    "url_default": "192.168.0.119",
    "ubicacion_default": "C:/AppServ/www/VisionArtificial_py/tests/calibracion_deteccion_papel.jpg",
    "pixels_por_mm_default": 35
}

class ConfigManager:
    def __init__(self, config_path, default_config=DEFAULT_CONFIG):
        self.config_path = config_path
        self.default_config = default_config
        self._ensure_config()

    def _ensure_config(self):
        if not os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'w') as archivo:
                    json.dump(self.default_config, archivo, indent=4)
                logger.info("Archivo de configuración creado con valores predeterminados.")
            except Exception as e:
                logger.error(f"Error al crear el archivo de configuración: {e}")
                sys.exit(1)

    def get_config(self):
        try:
            with open(self.config_path, 'r') as archivo:
                datos = json.load(archivo)
            return datos
        except Exception as e:
            logger.error(f"Error al leer el archivo de configuración: {e}")
            sys.exit(1)

    def update_config(self, nueva_config):
        try:
            with open(self.config_path, 'r+') as archivo:
                config = json.load(archivo)
                config.update(nueva_config)
                archivo.seek(0)
                json.dump(config, archivo, indent=4)
                archivo.truncate()
        except Exception as e:
            logger.error(f"Error al actualizar la configuración: {e}")
