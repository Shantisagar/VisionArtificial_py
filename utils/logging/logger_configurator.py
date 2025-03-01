"""
Path: utils/logging/logger_configurator.py
Configurador de logging para la aplicación.
Proporciona una API unificada para configurar el logging.
"""

import json
import logging
import logging.config
import logging.handlers
import os
from typing import Optional, List, Any, Dict, Union
from utils.logging.logger_factory import LoggerFactory

class LoggerConfigurator:
    """Configurador de logging para la aplicación."""

    def __init__(self, log_path: str = "logs", log_level: int = logging.INFO, logger_name: str = "vision_artificial"):
        """
        Inicializa el configurador de logging.
        
        Args:
            log_path: Ruta donde se almacenarán los logs
            log_level: Nivel de logging predeterminado
            logger_name: Nombre del logger principal
        """
        self.log_path = log_path
        self.log_level = log_level
        self.logger_name = logger_name
        self.filters = []

        # Crear el directorio de logs si no existe
        os.makedirs(log_path, exist_ok=True)

    def register_filter(self, filter_class: Any) -> None:
        """
        Registra un filtro para usarlo en la configuración.
        
        Args:
            filter_class: Clase del filtro a instanciar
        """
        self.filters.append(filter_class())

    def configure_from_json(self, json_path: str) -> logging.Logger:
        """
        Configura el logger utilizando un archivo JSON de configuración.
        
        Args:
            json_path: Ruta al archivo JSON de configuración
            
        Returns:
            Logger configurado
        """
        try:
            # Verificar existencia del archivo
            if not os.path.exists(json_path):
                print(f"Archivo de configuración {json_path} no encontrado. Usando configuración manual.")
                return self.configure()
            
            # Cargar configuración desde JSON
            with open(json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Ajustar rutas de archivos si es necesario
            if 'handlers' in config:
                for handler_name, handler_config in config['handlers'].items():
                    if 'filename' in handler_config:
                        # Asegurar que el directorio exista
                        log_dir = os.path.dirname(handler_config['filename'])
                        if log_dir:
                            os.makedirs(log_dir, exist_ok=True)
            
            # Aplicar configuración
            logging.config.dictConfig(config)
            
            # Obtener logger configurado
            logger = logging.getLogger(self.logger_name)
            
            # Registrar en LoggerFactory para acceso global
            LoggerFactory.set_default_logger(logger)
            
            return logger
            
        except Exception as e:
            print(f"Error al cargar configuración desde JSON: {e}")
            print("Fallback a configuración manual.")
            return self.configure()

    def configure(self, filters: Optional[List[Any]] = None) -> logging.Logger:
        """
        Configura y devuelve un logger con los filtros proporcionados.
        
        Args:
            filters: Lista opcional de filtros a aplicar
            
        Returns:
            Logger configurado
        """
        # Crear logger
        logger = logging.getLogger(self.logger_name)
        logger.setLevel(self.log_level)

        # Evitar duplicación de handlers
        if logger.handlers:
            # Registrar en LoggerFactory para acceso global
            LoggerFactory.set_default_logger(logger)
            return logger

        # Configurar handler para consola
        console = logging.StreamHandler()
        console.setLevel(self.log_level)

        # Configurar handler para archivo
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join(self.log_path, 'app.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(self.log_level)
        
        # Configurar un handler específico para errores
        error_file = logging.handlers.RotatingFileHandler(
            os.path.join(self.log_path, 'error.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_file.setLevel(logging.ERROR)

        # Aplicar filtros si se proporcionan
        all_filters = list(self.filters)  # Crear una copia
        if filters:
            all_filters.extend(filters)

        for f in all_filters:
            console.addFilter(f)
            file_handler.addFilter(f)

        # Configurar formato mejorado con información de archivo y línea
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        console.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        error_file.setFormatter(formatter)

        # Agregar handlers
        logger.addHandler(console)
        logger.addHandler(file_handler)
        logger.addHandler(error_file)

        # Registrar en LoggerFactory para acceso global
        LoggerFactory.set_default_logger(logger)

        return logger


def get_logger(name: str = "vision_artificial") -> logging.Logger:
    """
    Retorna un logger configurado.
    Wrapper simple para usar LoggerFactory.
    
    Args:
        name: Nombre del logger
        
    Returns:
        Logger configurado
    """
    return LoggerFactory.get_logger(name)
