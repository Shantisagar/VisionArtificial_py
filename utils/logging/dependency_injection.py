"""
Path: app/logs/dependency_injection.py
Contenedor de dependencias para inyección de dependencias.
"""

from utils.logging.logger_configurator import LoggerConfigurator
from utils.logging.info_error_filter import InfoErrorFilter
from utils.logging.exclude_http_logs_filter import ExcludeHTTPLogsFilter

# Crear una instancia global de LoggerConfigurator
configurator = LoggerConfigurator()

# Añadir filtros directamente a la configuración
# En lugar de usar register_filter que no existe
# Suponemos que configure() acepta filtros como parámetros
info_error_filter = InfoErrorFilter()
exclude_http_logs_filter = ExcludeHTTPLogsFilter()

# Configurar el logger con los filtros
APP_LOGGER = configurator.configure(filters=[info_error_filter, exclude_http_logs_filter])

def get_logger():
    """
    Retorna la instancia global del logger configurado.
    """
    return APP_LOGGER
