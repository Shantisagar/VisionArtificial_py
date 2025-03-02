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
from typing import Optional, List, Any
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
        
        # No podemos usar self.logger aquí porque aún no existe
        print(f"LoggerConfigurator inicializado: path={log_path}, level={log_level}, name={logger_name}")

    def register_filter(self, filter_class: Any) -> None:
        """
        Registra un filtro para usarlo en la configuración.
        
        Args:
            filter_class: Clase del filtro a instanciar
        """
        self.filters.append(filter_class())
        # Como esto se llama antes de configurar el logger, usamos print para debug
        print(f"Filtro registrado: {filter_class.__name__}")

    def configure_from_json(self, json_path: str) -> logging.Logger:
        """
        Configura el logger utilizando un archivo JSON de configuración.
        
        Args:
            json_path: Ruta al archivo JSON de configuración
            
        Returns:
            Logger configurado
        """
        print(f"Configurando logger desde JSON: {json_path}")
        try:
            # Verificar existencia del archivo
            if not os.path.exists(json_path):
                print(f"Archivo de configuración JSON no encontrado: {json_path}")
                print("Fallback a configuración manual")
                return self.configure()

            print(f"Archivo JSON encontrado, intentando cargar: {json_path}")
            # Cargar configuración desde JSON
            with open(json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                print(f"JSON cargado correctamente, configuración: {config.keys()}")

            # Ajustar rutas de archivos si es necesario
            if 'handlers' in config:
                print(f"Analizando {len(config['handlers'])} handlers para ajustar rutas")
                for handler_name, handler_config in config['handlers'].items():
                    if 'filename' in handler_config:
                        original_path = handler_config['filename']
                        # Asegurar que el directorio exista
                        log_dir = os.path.dirname(handler_config['filename'])
                        if log_dir:
                            print(f"Creando directorio para handler {handler_name}: {log_dir}")
                            os.makedirs(log_dir, exist_ok=True)
                        print(f"Handler {handler_name}: ruta ajustada de {original_path}")

            print("Aplicando configuración mediante dictConfig")
            # Aplicar configuración
            logging.config.dictConfig(config)
            print("Configuración aplicada correctamente")

            # Obtener logger configurado
            logger = logging.getLogger(self.logger_name)
            logger.debug("Logger inicializado desde configuración JSON")
            print(f"Logger '{self.logger_name}' configurado con nivel: {logger.level}")

            # Registrar en LoggerFactory para acceso global
            LoggerFactory.set_default_logger(logger)
            logger.debug("Logger registrado en LoggerFactory")

            return logger

        except Exception as e:
            print(f"Error al cargar configuración desde JSON: {e}")
            print("Fallback a configuración manual.")
            fallback_logger = self.configure()
            fallback_logger.error(f"Error al cargar configuración desde JSON: {e}, usando configuración manual")
            return fallback_logger

    def configure(self, filters: Optional[List[Any]] = None) -> logging.Logger:
        """
        Configura y devuelve un logger con los filtros proporcionados.
        
        Args:
            filters: Lista opcional de filtros a aplicar
            
        Returns:
            Logger configurado
        """
        print(f"Configurando logger manualmente: {self.logger_name}")
        # Crear logger
        logger = logging.getLogger(self.logger_name)
        logger.setLevel(self.log_level)

        # Evitar duplicación de handlers
        if logger.handlers:
            print(f"Logger ya tiene handlers ({len(logger.handlers)}), evitando duplicación")
            # Registrar en LoggerFactory para acceso global
            LoggerFactory.set_default_logger(logger)
            return logger

        print("Configurando handlers")
        # Configurar handler para consola
        console = logging.StreamHandler()
        console.setLevel(self.log_level)
        print(f"Handler de consola configurado con nivel: {self.log_level}")

        # Configurar handler para archivo
        log_file_path = os.path.join(self.log_path, 'app.log')
        print(f"Configurando handler para archivo: {log_file_path}")
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(self.log_level)

        # Configurar un handler específico para errores
        error_file_path = os.path.join(self.log_path, 'error.log')
        print(f"Configurando handler para errores: {error_file_path}")
        error_file = logging.handlers.RotatingFileHandler(
            error_file_path,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_file.setLevel(logging.ERROR)

        # Aplicar filtros si se proporcionan
        all_filters = list(self.filters)  # Crear una copia
        if filters:
            print(f"Añadiendo {len(filters)} filtros adicionales")
            all_filters.extend(filters)

        print(f"Aplicando {len(all_filters)} filtros a los handlers")
        for f in all_filters:
            print(f"Aplicando filtro: {f.__class__.__name__}")
            console.addFilter(f)
            file_handler.addFilter(f)

        # Configurar formato mejorado con información de archivo y línea
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        console.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        error_file.setFormatter(formatter)
        print("Formato configurado para todos los handlers")

        # Agregar handlers
        logger.addHandler(console)
        logger.addHandler(file_handler)
        logger.addHandler(error_file)
        print(f"Handlers agregados al logger: {len(logger.handlers)} handlers")

        # Registrar en LoggerFactory para acceso global
        LoggerFactory.set_default_logger(logger)
        print("Logger registrado en LoggerFactory")

        # Ahora que tenemos un logger configurado, podemos usarlo
        logger.debug("Logger configurado manualmente")
        
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
    logger = LoggerFactory.get_logger(name)
    logger.debug(f"Logger '{name}' obtenido de LoggerFactory")
    return logger
