"""
Decoradores para estandarizar el manejo de excepciones en funciones y métodos.
"""

import functools
import inspect
from typing import Callable, Optional, Type, Union, List, Any

from utils.error_handling.error_handler import get_error_handler, ErrorSeverity


def _get_default_return_value(return_annotation) -> Any:
    """
    Helper function to create a default return value based on type annotation.
    
    Args:
        return_annotation: The return type annotation
        
    Returns:
        A default value appropriate for the annotation
    """
    # Initialize default value
    default_value = None

    if return_annotation is not inspect.Signature.empty:
        if return_annotation in (int, float):
            default_value = 0
        elif return_annotation is bool:
            default_value = False
        elif return_annotation is str:
            default_value = ""
        else:
            origin = getattr(return_annotation, "__origin__", None)
            if origin is list:
                default_value = []
            elif origin is dict:
                default_value = {}

    return default_value


def _get_context(func, add_function_name, context_fn, args, kwargs):
    """
    Helper function to build context dict for error handling.
    
    Returns:
        dict: Context dictionary for error handling
    """
    context = {}

    # Add function name if needed
    if add_function_name:
        context["function"] = func.__name__

    # Get additional context if provided
    if context_fn:
        try:
            if inspect.signature(context_fn).parameters:
                additional_context = context_fn(*args, **kwargs)
            else:
                additional_context = context_fn()

            if additional_context:
                context.update(additional_context)
        except (TypeError, ValueError, KeyError) as context_error:
            get_error_handler().handle_exception(
                context_error,
                ErrorSeverity.WARNING,
                {"message": "Error al obtener contexto adicional"}
            )

    return context


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
            except (ValueError, TypeError, KeyError) as e:  # Replace with specific exceptions
                # Create context and handle the exception
                context = _get_context(func, add_function_name, context_fn, args, kwargs)
                get_error_handler().handle_exception(e, severity, context)

                # Reraise if needed
                if reraise:
                    raise

                # Return appropriate default value based on return annotation
                return_annotation = inspect.signature(func).return_annotation
                return _get_default_return_value(return_annotation)

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
            # pylint: disable=broad-exception-caught
            except Exception as e:
                # Only handle specific exceptions
                if not any(isinstance(e, exc) for exc in exceptions):
                    raise

                # Create context and handle the exception
                context = _get_context(func, add_function_name, context_fn, args, kwargs)
                get_error_handler().handle_exception(e, severity, context)

                # Reraise if needed
                if reraise:
                    raise

                # Return appropriate default value
                return_annotation = inspect.signature(func).return_annotation
                return _get_default_return_value(return_annotation)

        return wrapper
    return decorator
