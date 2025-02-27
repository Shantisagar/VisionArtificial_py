"""
Path: app/logs/dependency_injection.py
Contenedor de dependencias para inyección de dependencias.
"""

from utils.logging.logger_configurator import LoggerConfigurator
from utils.logging.info_error_filter import InfoErrorFilter
from utils.logging.exclude_http_logs_filter import ExcludeHTTPLogsFilter

# Crear una instancia global de LoggerConfigurator
configurator = LoggerConfigurator()

# Registrar filtros dinámicos
configurator.register_filter('info_error_filter', InfoErrorFilter)
configurator.register_filter('exclude_http_logs_filter', ExcludeHTTPLogsFilter)

# Configurar el logger con los filtros registrados
app_logger = configurator.configure()

def get_logger():
    """
    Retorna la instancia global del logger configurado.
    """
    return app_logger
