"""
Sistema centralizado de manejo de excepciones y logging.
Implementa patrones Singleton y Facade para proporcionar una interfaz
unificada para el manejo de errores en toda la aplicación.
"""

import sys
import traceback
import logging
from typing import Optional, Callable, Type, Dict, List, Any
from enum import Enum

from utils.logging.logger_configurator import get_logger


class ErrorSeverity(Enum):
    """Niveles de severidad para clasificar errores."""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    FATAL = 60  # Error que termina la aplicación


class ErrorHandler:
    """
    Manejador centralizado de excepciones.
    Implementa el patrón Singleton para garantizar una única instancia.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Implementa el patrón Singleton."""
        if cls._instance is None:
            cls._instance = super(ErrorHandler, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Inicializa el manejador de errores con un logger.
        
        Args:
            logger: Logger a utilizar (opcional)
        """
        # Solo inicializar una vez debido al patrón Singleton
        self._initialized = False
        if self._initialized:
            return

        self._initialized = True
        self.logger = logger or get_logger()
        self.error_callbacks: Dict[Type[Exception], List[Callable]] = {}
        self.default_callbacks: List[Callable] = []

    def handle_exception(self,
                         exception: Exception,
                         severity: ErrorSeverity = ErrorSeverity.ERROR,
                         context: Optional[Dict[str, Any]] = None) -> None:
        """
        Maneja una excepción con el nivel de severidad y contexto especificados.
        
        Args:
            exception: Excepción a manejar
            severity: Nivel de severidad del error
            context: Información contextual adicional
        """
        # Normalizar contexto
        context = context or {}
        exception_type = type(exception)
        error_message = str(exception)
        stack_trace = traceback.format_exc()

        # Construir mensaje descriptivo con contexto
        message = f"{exception_type.__name__}: {error_message}"
        if context:
            context_str = ", ".join(f"{k}={v}" for k, v in context.items())
            message += f" [Contexto: {context_str}]"

        # Registrar según la severidad
        if severity == ErrorSeverity.DEBUG:
            self.logger.debug(message)
            self.logger.debug(stack_trace)
        elif severity == ErrorSeverity.INFO:
            self.logger.info(message)
        elif severity == ErrorSeverity.WARNING:
            self.logger.warning(message)
            self.logger.debug(stack_trace)
        elif severity == ErrorSeverity.ERROR:
            self.logger.error(message)
            self.logger.debug(stack_trace)
        elif severity == ErrorSeverity.CRITICAL:
            self.logger.critical(message)
            self.logger.debug(stack_trace)
        elif severity == ErrorSeverity.FATAL:
            # Fix: Use lazy % formatting instead of f-string
            self.logger.critical("ERROR FATAL: %s", message)
            self.logger.critical(stack_trace)
            sys.exit(1)

        # Ejecutar callbacks específicos para este tipo de excepción
        for callback in self.error_callbacks.get(exception_type, []):
            try:
                callback(exception, severity, context)
            except (TypeError, ValueError) as e:
                # Fix: Use lazy % formatting instead of f-string
                self.logger.error("Error en callback de manejo de excepción: %s", e)

        # Ejecutar callbacks por defecto
        for callback in self.default_callbacks:
            try:
                callback(exception, severity, context)
            except (TypeError, ValueError) as e:
                # Fix: Use lazy % formatting instead of f-string
                self.logger.error("Error en callback por defecto: %s", e)

    def register_callback(self,
                         exception_type: Optional[Type[Exception]],
                         callback: Callable) -> None:
        """
        Registra un callback para un tipo específico de excepción.
        Si exception_type es None, se registra como callback por defecto.
        
        Args:
            exception_type: Tipo de excepción o None para callback por defecto
            callback: Función a llamar cuando ocurra la excepción
        """
        if exception_type is None:
            self.default_callbacks.append(callback)
        else:
            if exception_type not in self.error_callbacks:
                self.error_callbacks[exception_type] = []
            self.error_callbacks[exception_type].append(callback)

    def unregister_callback(self,
                           exception_type: Optional[Type[Exception]],
                           callback: Callable) -> bool:
        """
        Elimina un callback registrado.
        
        Args:
            exception_type: Tipo de excepción o None para callback por defecto
            callback: Función a eliminar
            
        Returns:
            True si el callback fue eliminado, False si no se encontró
        """
        if exception_type is None:
            if callback in self.default_callbacks:
                self.default_callbacks.remove(callback)
                return True
            return False

        if exception_type in self.error_callbacks:
            if callback in self.error_callbacks[exception_type]:
                self.error_callbacks[exception_type].remove(callback)
                return True
        return False


class ErrorHandlerSingleton:
    """
    Singleton para el manejador de errores.
    """
    _error_handler: Optional[ErrorHandler] = None

    @classmethod
    def get_error_handler(cls) -> ErrorHandler:
        """
        Obtiene la instancia única del manejador de errores.
        
        Returns:
            La instancia del manejador de errores
        """
        if cls._error_handler is None:
            cls._error_handler = ErrorHandler()
        return cls._error_handler

    @classmethod
    def set_error_handler(cls, handler: ErrorHandler) -> None:
        """
        Establece un manejador de errores personalizado.
        
        Args:
            handler: El manejador de errores a utilizar
        """
        cls._error_handler = handler


# Functions to access the singleton
def get_error_handler() -> ErrorHandler:
    """
    Obtiene la instancia única del manejador de errores.
    
    Returns:
        La instancia del manejador de errores
    """
    return ErrorHandlerSingleton.get_error_handler()


def set_error_handler(handler: ErrorHandler) -> None:
    """
    Establece un manejador de errores personalizado.
    
    Args:
        handler: El manejador de errores a utilizar
    """
    ErrorHandlerSingleton.set_error_handler(handler)
