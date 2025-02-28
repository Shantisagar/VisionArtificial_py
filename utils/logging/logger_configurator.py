"""
Módulo para la configuración centralizada del sistema de logging.
Implementa el patrón singleton con soporte para inyección de dependencias.
"""

import logging
import os
from datetime import datetime
from typing import Optional

class LoggerConfigurator:
    """Configurador de logger que implementa el patrón singleton con soporte para DI."""

    _instance = None
    _logger = None

    def __new__(cls, *args, **kwargs):
        """Implementación del patrón singleton con soporte para reinicialización."""
        if cls._instance is None:
            cls._instance = super(LoggerConfigurator, cls).__new__(cls)
        return cls._instance

    def __init__(self, log_level: int = logging.INFO, log_file: Optional[str] = None):
        """
        Inicializa el configurador con nivel de log y archivo opcionales.
        
        Args:
            log_level: Nivel de logging (default: logging.INFO)
            log_file: Ruta al archivo de logs (default: auto-generado)
        """
        # Solo configurar una vez
        if LoggerConfigurator._logger is None:
            self.log_level = log_level
            self.log_file = log_file or self._generate_log_file()

    def _generate_log_file(self) -> str:
        """
        Genera un nombre de archivo de log basado en la fecha y hora actuales.
        
        Returns:
            Ruta al archivo de log generado
        """
        log_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(log_dir, f"app_{timestamp}.log")

    def configure(self) -> logging.Logger:
        """
        Configura y devuelve el logger global.
        
        Returns:
            Logger configurado
        """
        if LoggerConfigurator._logger is None:
            # Crear el logger
            logger = logging.getLogger('VisionArtificial')
            logger.setLevel(self.log_level)

            # Evitar duplicación de handlers
            if not logger.handlers:
                # Configurar handler de archivo
                file_handler = logging.FileHandler(self.log_file)
                file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                file_handler.setFormatter(file_format)
                logger.addHandler(file_handler)

                # Configurar handler de consola
                console_handler = logging.StreamHandler()
                console_format = logging.Formatter('%(levelname)s: %(message)s')
                console_handler.setFormatter(console_format)
                logger.addHandler(console_handler)

            LoggerConfigurator._logger = logger
            logger.info("Logging configurado. Archivo de log: %s", self.log_file)

        return LoggerConfigurator._logger

    @classmethod
    def reset(cls) -> None:
        """Reinicia el singleton y el logger (útil para pruebas)."""
        cls._instance = None
        cls._logger = None

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """
        Obtiene el logger configurado o crea uno nuevo si no existe.
        
        Returns:
            Logger configurado
        """
        if cls._logger is None:
            cls._logger = cls().configure()
        return cls._logger

    @classmethod
    def set_logger(cls, logger: logging.Logger) -> None:
        """
        Establece un logger personalizado (para inyección de dependencias).
        
        Args:
            logger: El logger personalizado a utilizar
        """
        cls._logger = logger


def get_logger() -> logging.Logger:
    """
    Función auxiliar para obtener el logger global configurado.
    
    Returns:
        Logger global configurado
    """
    return LoggerConfigurator.get_logger()


def set_logger(logger: logging.Logger) -> None:
    """
    Función auxiliar para establecer un logger personalizado.
    
    Args:
        logger: El logger personalizado a utilizar
    """
    LoggerConfigurator.set_logger(logger)
