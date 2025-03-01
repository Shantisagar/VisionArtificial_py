"""
Path: utils/logging/dependency_injection.py
Contenedor de dependencias para inyección de dependencias.
"""

import os
from utils.logging.logger_configurator import LoggerConfigurator
from utils.logging.info_error_filter import InfoErrorFilter
from utils.logging.exclude_http_logs_filter import ExcludeHTTPLogsFilter

# Definir la ruta al archivo JSON
JSON_CONFIG_PATH = '/c:/AppServ/www/VisionArtificial_py/utils/logging/logging.json'

# Crear una instancia global de LoggerConfigurator
configurator = LoggerConfigurator()

# Intenta configurar desde JSON primero
if os.path.exists(JSON_CONFIG_PATH):
    APP_LOGGER = configurator.configure_from_json(JSON_CONFIG_PATH)
else:
    # Fallback a la configuración anterior
    configurator.register_filter(InfoErrorFilter)
    configurator.register_filter(ExcludeHTTPLogsFilter)
    APP_LOGGER = configurator.configure()

def get_logger():
    """
    Retorna la instancia global del logger configurado.
    """
    return APP_LOGGER
