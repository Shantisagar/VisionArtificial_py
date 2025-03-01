"""
Path: utils/logging/logger_factory.py
Factory para la creación de loggers con diferentes configuraciones.
Implementa patrón Singleton para facilitar el acceso global y la inyección.
"""

import logging
from typing import Optional, Dict, Any, Type

class LoggerFactory:
    """Factory para crear y gestionar loggers de forma centralizada."""

    _instance = None
    _loggers: Dict[str, logging.Logger] = {}
    _default_logger = None
    _initialized = False

    def __new__(cls):
        """Implementación del patrón Singleton."""
        if cls._instance is None:
            cls._instance = super(LoggerFactory, cls).__new__(cls)
            cls._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializa el factory si no se ha hecho antes."""
        # Solo inicializar una vez
        if not self._initialized:
            self._loggers = {}
            self._default_logger = None
            self._initialized = True

    @classmethod
    def get_logger(cls, name: str = "vision_artificial") -> logging.Logger:
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
        # También guardarlo en el diccionario si no existe
        if logger.name not in cls._loggers:
            cls._loggers[logger.name] = logger

    @classmethod
    def get_default_logger(cls) -> Optional[logging.Logger]:
        """
        Obtiene el logger predeterminado.
        
        Returns:
            El logger predeterminado o None si no está configurado
        """
        if cls._default_logger is None:
            # Si no hay logger predeterminado, crear uno básico
            cls._default_logger = cls.get_logger()
        return cls._default_logger
    
    @classmethod
    def clear_loggers(cls) -> None:
        """
        Limpia todos los loggers registrados.
        Útil para pruebas y reinicialización.
        """
        cls._loggers.clear()
        cls._default_logger = None
