"""
Decoradores para estandarizar el manejo de excepciones en funciones y métodos.
"""

import functools
import inspect
from typing import Callable, Optional, Dict, Any, Type, Union, List

from utils.error_handling.error_handler import get_error_handler, ErrorSeverity


def handle_exceptions(severity: ErrorSeverity = ErrorSeverity.ERROR, 
                      context_fn: Optional[Callable] = None,
                      reraise: bool = False,
                      add_function_name: bool = True):
    """
    Decorador que maneja excepciones en funciones y métodos.
    
    Args:
        severity: Nivel de severidad del error
        context_fn: Función opcional que devuelve contexto adicional
        reraise: Si es True, relanza la excepción después de manejarla
        add_function_name: Si es True, añade el nombre de la función al contexto
        
    Returns:
        Decorador configurado
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Crear contexto
                context = {}
                # Añadir nombre de función al contexto si se solicita
                if add_function_name:
                    context["function"] = func.__name__

                # Obtener contexto adicional si se proporciona una función
                if context_fn:
                    try:
                        if inspect.signature(context_fn).parameters:
                            additional_context = context_fn(*args, **kwargs)
                        else:
                            # No pasar argumentos
                            additional_context = context_fn()
  
                        if additional_context:
                            context.update(additional_context)
                    except Exception as context_error:
                        get_error_handler().handle_exception(
                            context_error, 
                            ErrorSeverity.WARNING,
                            {"message": "Error al obtener contexto adicional"}
                        )

                # Manejar la excepción
                get_error_handler().handle_exception(e, severity, context)

                # Relanzar si es necesario
                if reraise:
                    raise

                # Retornar un valor por defecto según el tipo de retorno
                # Si hay una anotación de retorno, intentamos crear un valor por defecto
                return_annotation = inspect.signature(func).return_annotation
                if return_annotation is not inspect.Signature.empty:
                    if return_annotation in (int, float):
                        return 0
                    elif return_annotation is bool:
                        return False
                    elif return_annotation is str:
                        return ""
                    elif getattr(return_annotation, "__origin__", None) is list:
                        return []
                    elif getattr(return_annotation, "__origin__", None) is dict:
                        return {}
                return None
        return wrapper
    return decorator


def handle_specific_exceptions(exceptions: Union[Type[Exception], List[Type[Exception]]],
                             severity: ErrorSeverity = ErrorSeverity.ERROR,
                             context_fn: Optional[Callable] = None,
                             reraise: bool = False,
                             add_function_name: bool = True):
    """
    Decorador que maneja tipos específicos de excepciones.
    
    Args:
        exceptions: Tipo(s) de excepción a manejar
        severity: Nivel de severidad del error
        context_fn: Función opcional que devuelve contexto adicional
        reraise: Si es True, relanza la excepción después de manejarla
        add_function_name: Si es True, añade el nombre de la función al contexto
        
    Returns:
        Decorador configurado
    """
    if not isinstance(exceptions, (list, tuple)):
        exceptions = [exceptions]

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Solo manejar excepciones específicas
                if not any(isinstance(e, exc) for exc in exceptions):
                    raise

                # Crear contexto
                context = {}

                # Añadir nombre de función al contexto si se solicita
                if add_function_name:
                    context["function"] = func.__name__

                # Obtener contexto adicional si se proporciona una función
                if context_fn:
                    try:
                        if inspect.signature(context_fn).parameters:
                            # Pasar los mismos argumentos que la función original
                            additional_context = context_fn(*args, **kwargs)
                        else:
                            # No pasar argumentos
                            additional_context = context_fn()

                        if additional_context:
                            context.update(additional_context)
                    except Exception as context_error:
                        get_error_handler().handle_exception(
                            context_error, 
                            ErrorSeverity.WARNING,
                            {"message": "Error al obtener contexto adicional"}
                        )

                # Manejar la excepción
                get_error_handler().handle_exception(e, severity, context)

                # Relanzar si es necesario
                if reraise:
                    raise

                # Retornar un valor por defecto
                return_annotation = inspect.signature(func).return_annotation
                if return_annotation is not inspect.Signature.empty:
                    if return_annotation in (int, float):
                        return 0
                    elif return_annotation is bool:
                        return False
                    elif return_annotation is str:
                        return ""
                    elif getattr(return_annotation, "__origin__", None) is list:
                        return []
                    elif getattr(return_annotation, "__origin__", None) is dict:
                        return {}
                return None
        return wrapper
    return decorator
