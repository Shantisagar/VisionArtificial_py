"""
Path: utils/logging/logger_factory.py
Factory para la creación de loggers con diferentes configuraciones.
Implementa patrón Singleton para facilitar el acceso global y la inyección.
"""

import logging
from typing import Optional, Dict

class LoggerFactory:
    """Factory para crear y gestionar loggers de forma centralizada."""

    _instance = None
    _loggers: Dict[str, logging.Logger] = {}
    _default_logger = None

    def __new__(cls):
        """Implementación del patrón Singleton."""
        if cls._instance is None:
            cls._instance = super(LoggerFactory, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_logger(cls, name: str = "default") -> logging.Logger:
        """
        Obtiene un logger existente o crea uno nuevo si no existe.
        
        Args:
            name: Nombre del logger a obtener
            
        Returns:
            Un objeto logger configurado
        """
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger

            # Si este es el primer logger, establecerlo como predeterminado
            if cls._default_logger is None:
                cls._default_logger = logger

        return cls._loggers[name]

    @classmethod
    def set_default_logger(cls, logger: logging.Logger) -> None:
        """
        Establece el logger predeterminado.
        
        Args:
            logger: Logger a establecer como predeterminado
        """
        cls._default_logger = logger

    @classmethod
    def get_default_logger(cls) -> Optional[logging.Logger]:
        """
        Obtiene el logger predeterminado.
        
        Returns:
            El logger predeterminado o None si no está configurado
        """
        return cls._default_logger
