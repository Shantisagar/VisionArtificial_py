"""
Administradores de contexto para estandarizar bloques try/except en la aplicación.
"""

import contextlib
from typing import Optional, Dict, Any, Type, Union, List, Generator, Callable

from utils.error_handling.error_handler import get_error_handler, ErrorSeverity


@contextlib.contextmanager
def error_context(severity: ErrorSeverity = ErrorSeverity.ERROR,
                 context: Optional[Dict[str, Any]] = None,
                 reraise: bool = False) -> Generator:
    """
    Contexto que maneja excepciones de forma estandarizada.
    
    Args:
        severity: Nivel de severidad del error
        context: Información contextual adicional
        reraise: Si es True, relanza la excepción después de manejarla
        
    Yields:
        Nada, simplemente define el bloque de contexto
    """
    try:
        yield
    except Exception as e:
        # Manejar la excepción
        get_error_handler().handle_exception(e, severity, context)
        
        # Relanzar si es necesario
        if reraise:
            raise


@contextlib.contextmanager
def specific_error_context(exceptions: Union[Type[Exception], List[Type[Exception]]],
                          severity: ErrorSeverity = ErrorSeverity.ERROR,
                          context: Optional[Dict[str, Any]] = None,
                          reraise: bool = False) -> Generator:
    """
    Contexto que maneja tipos específicos de excepciones.
    
    Args:
        exceptions: Tipo(s) de excepción a manejar
        severity: Nivel de severidad del error
        context: Información contextual adicional
        reraise: Si es True, relanza la excepción después de manejarla
        
    Yields:
        Nada, simplemente define el bloque de contexto
    """
    if not isinstance(exceptions, (list, tuple)):
        exceptions = [exceptions]
        
    try:
        yield
    except Exception as e:
        # Solo manejar excepciones específicas
        if not any(isinstance(e, exc) for exc in exceptions):
            raise
            
        # Manejar la excepción
        get_error_handler().handle_exception(e, severity, context)
        
        # Relanzar si es necesario
        if reraise:
            raise


def collect_context(func: Callable) -> Dict[str, Any]:
    """
    Función auxiliar para ejecutar recolectores de contexto.
    
    Args:
        func: Función que recolecta contexto
        
    Returns:
        Diccionario con la información contextual recolectada
    """
    try:
        context = func()
        return context if context else {}
    except Exception as e:
        get_error_handler().handle_exception(
            e,
            ErrorSeverity.WARNING,
            {"message": "Error al recolectar contexto"}
        )
        return {}
