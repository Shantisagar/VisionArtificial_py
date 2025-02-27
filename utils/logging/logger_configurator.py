"""
Configurador de logging que permite inyectar configuraciones personalizadas.
"""

import logging
import sys
from typing import Optional

# Singleton logger para mantener una referencia global
_default_logger = None

class LoggerConfigurator:
    """Configura loggers con diferentes niveles y formatos."""

    def __init__(self, 
                 level: int = logging.INFO, 
                 format_string: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'):
        """
        Inicializa el configurador con opciones personalizables.
        
        Args:
            level: Nivel de log (INFO, DEBUG, etc.)
            format_string: Formato de las entradas de log
        """
        self.level = level
        self.format_string = format_string
        
    def configure(self, name: str = "app_logger") -> logging.Logger:
        """
        Configura y devuelve un logger.
        
        Args:
            name: Nombre del logger a configurar
            
        Returns:
            El logger configurado
        """
        global _default_logger
        
        # Crear o obtener el logger por nombre
        logger = logging.getLogger(name)
        
        # Evitar duplicar handlers si ya está configurado
        if not logger.handlers:
            logger.setLevel(self.level)
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(self.level)
            formatter = logging.Formatter(self.format_string)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        # Almacenar como logger predeterminado si es el primero
        if _default_logger is None:
            _default_logger = logger
        
        return logger

def get_logger() -> logging.Logger:
    """
    Función de utilidad para acceder al logger predeterminado.
    
    Returns:
        El logger predeterminado configurado o uno nuevo si no existe
    """
    global _default_logger
    
    if _default_logger is None:
        # Si no hay logger predeterminado, crear uno básico
        _default_logger = LoggerConfigurator().configure()
        
    return _default_logger
