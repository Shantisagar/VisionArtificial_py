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
import sys
from typing import Optional, List, Any, Dict, Set

from utils.logging.logger_factory import LoggerFactory

class LoggerConfigurator:
    """Configurador de logging para la aplicación."""

    # Almacenamiento para los handlers creados, evitando duplicación
    _handlers_cache: Dict[str, logging.Handler] = {}
    
    # Conjunto para seguir los nombres de loggers ya configurados
    _configured_loggers: Set[str] = set()

    def __init__(
        self,
        log_path: str = "logs",
        log_level: int = logging.INFO,
        logger_name: str = "vision_artificial"
    ):
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
        self.formatter = self._create_standard_formatter()

        # Crear el directorio de logs si no existe
        os.makedirs(log_path, exist_ok=True)

        # No podemos usar self.logger aquí porque aún no existe
        print(
            f"LoggerConfigurator inicializado: path={log_path}, "
            f"level={log_level}, name={logger_name}"
        )

    def register_filter(self, filter_class: Any) -> None:
        """
        Registra un filtro para usarlo en la configuración.
        
        Args:
            filter_class: Clase del filtro a instanciar
        """
        # Solo añadir filtros nuevos, evitar duplicados
        for existing_filter in self.filters:
            if isinstance(existing_filter, filter_class):
                print(f"Filtro {filter_class.__name__} ya registrado, omitiendo")
                return
                
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
                self._prepare_log_directories(config)

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

        except (FileNotFoundError, json.JSONDecodeError, PermissionError) as e:
            print(f"Error al cargar configuración desde JSON: {e}")
            print("Fallback a configuración manual.")
            fallback_logger = self.configure()
            fallback_logger.error(
                "Error al cargar configuración desde JSON: %s, usando configuración manual", e
            )
            return fallback_logger
            
    def _prepare_log_directories(self, config: Dict) -> None:
        """
        Prepara los directorios para los archivos de log definidos en la configuración.
        
        Args:
            config: Configuración de logging en formato diccionario
        """
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

    def configure(self, filters: Optional[List[Any]] = None) -> logging.Logger:
        """
        Configura y devuelve un logger con los filtros proporcionados.
        
        Args:
            filters: Lista opcional de filtros a aplicar
            
        Returns:
            Logger configurado
        """
        print(f"Configurando logger manualmente: {self.logger_name}")
        
        # Obtener o crear el logger
        logger = self._get_or_create_logger()
        
        # Si este logger ya está configurado, simplemente devolverlo
        if self.logger_name in self._configured_loggers:
            print(f"Logger '{self.logger_name}' ya configurado, reutilizando")
            return logger
            
        # Añadir handlers si no existen
        self._add_handlers_to_logger(logger, filters)
            
        # Registrar en LoggerFactory para acceso global
        LoggerFactory.set_default_logger(logger)
        
        # Marcar este logger como configurado
        self._configured_loggers.add(self.logger_name)
        
        # Mensaje inicial con información del sistema
        logger.debug("Logger configurado manualmente")
        logger.debug(f"Versión Python: {sys.version}")
        logger.debug(f"Plataforma: {sys.platform}")
        
        return logger
    
    def _get_or_create_logger(self) -> logging.Logger:
        """
        Obtiene un logger existente o crea uno nuevo configurándolo.
        
        Returns:
            Logger configurado con el nivel adecuado
        """
        logger = logging.getLogger(self.logger_name)
        logger.setLevel(self.log_level)
        
        # Si el logger ya tiene handlers, verificamos si necesitamos propagar
        if logger.hasHandlers():
            # Solo desactivamos la propagación para el logger principal
            # para evitar duplicación de logs
            if not logger.name or logger.name == 'root':
                logger.propagate = False
            
        return logger
    
    def _add_handlers_to_logger(self, logger: logging.Logger, filters: Optional[List[Any]]) -> None:
        """
        Añade los handlers necesarios al logger si no existen ya.
        
        Args:
            logger: Logger al que añadir los handlers
            filters: Filtros adicionales a aplicar
        """
        # Si ya tiene handlers, no añadir más
        if logger.handlers:
            print(f"Logger ya tiene handlers ({len(logger.handlers)}), evitando duplicación")
            return
            
        # Crear los handlers necesarios o recuperar del caché
        console_handler = self._get_or_create_console_handler()
        file_handler = self._get_or_create_file_handler('app.log')
        error_handler = self._get_or_create_error_handler('error.log')
        
        # Aplicar filtros a los handlers
        self._apply_filters_to_handlers([console_handler, file_handler], filters)
        
        # Añadir los handlers al logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)
        
        print(f"Handlers agregados al logger: {len(logger.handlers)} handlers")
    
    def _get_or_create_console_handler(self) -> logging.Handler:
        """
        Obtiene o crea un handler para consola.
        
        Returns:
            Handler configurado para consola
        """
        handler_key = 'console'
        if handler_key in self._handlers_cache:
            return self._handlers_cache[handler_key]
            
        console = logging.StreamHandler()
        console.setLevel(self.log_level)
        console.setFormatter(self.formatter)
        
        self._handlers_cache[handler_key] = console
        print(f"Handler de consola creado con nivel: {self.log_level}")
        
        return console
    
    def _get_or_create_file_handler(self, filename: str) -> logging.Handler:
        """
        Obtiene o crea un handler para archivo de log.
        
        Args:
            filename: Nombre del archivo de log
            
        Returns:
            Handler configurado para archivo
        """
        handler_key = f'file_{filename}'
        if handler_key in self._handlers_cache:
            return self._handlers_cache[handler_key]
            
        log_file_path = os.path.join(self.log_path, filename)
        print(f"Configurando handler para archivo: {log_file_path}")
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(self.formatter)
        
        self._handlers_cache[handler_key] = file_handler
        
        return file_handler
    
    def _get_or_create_error_handler(self, filename: str) -> logging.Handler:
        """
        Obtiene o crea un handler específico para errores.
        
        Args:
            filename: Nombre del archivo de log para errores
            
        Returns:
            Handler configurado para errores
        """
        handler_key = f'error_{filename}'
        if handler_key in self._handlers_cache:
            return self._handlers_cache[handler_key]
            
        error_file_path = os.path.join(self.log_path, filename)
        print(f"Configurando handler para errores: {error_file_path}")
        
        error_file = logging.handlers.RotatingFileHandler(
            error_file_path,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_file.setLevel(logging.ERROR)  # Solo para errores y críticos
        error_file.setFormatter(self.formatter)
        
        self._handlers_cache[handler_key] = error_file
        
        return error_file
    
    def _apply_filters_to_handlers(self, handlers: List[logging.Handler], 
                                   additional_filters: Optional[List[Any]]) -> None:
        """
        Aplica los filtros registrados a los handlers especificados.
        
        Args:
            handlers: Lista de handlers a los que aplicar filtros
            additional_filters: Filtros adicionales a aplicar
        """
        # Combinar filtros registrados con los adicionales
        all_filters = list(self.filters)  # Crear una copia
        if additional_filters:
            print(f"Añadiendo {len(additional_filters)} filtros adicionales")
            all_filters.extend(additional_filters)

        # Si no hay filtros, no hacer nada
        if not all_filters:
            return
            
        print(f"Aplicando {len(all_filters)} filtros a {len(handlers)} handlers")
        for handler in handlers:
            for filter_obj in all_filters:
                # Evitar añadir el mismo filtro varias veces
                should_add = True
                for existing_filter in handler.filters:
                    if type(existing_filter) == type(filter_obj):
                        should_add = False
                        break
                
                if should_add:
                    print(f"Aplicando filtro: {filter_obj.__class__.__name__} a {handler.__class__.__name__}")
                    handler.addFilter(filter_obj)
    
    def _create_standard_formatter(self) -> logging.Formatter:
        """
        Crea un formateador estándar para los logs.
        
        Returns:
            Formateador configurado
        """
        return logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )


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
