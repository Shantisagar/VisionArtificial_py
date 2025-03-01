"""
Paquete de manejo de errores centralizado para la aplicación.
Proporciona una API unificada para el manejo de excepciones.
"""

from utils.error_handling.error_handler import (
    ErrorHandler, ErrorSeverity, get_error_handler, set_error_handler
)
from utils.error_handling.decorators import (
    handle_exceptions, handle_specific_exceptions
)
from utils.error_handling.contexts import (
    error_context, specific_error_context, collect_context
)
from utils.error_handling.exceptions import (
    AppException, ConfigurationError, VideoSourceError,
    InputValidationError, ImageProcessingError, UIError
)

__all__ = [
    'ErrorHandler', 'ErrorSeverity', 'get_error_handler', 'set_error_handler',
    'handle_exceptions', 'handle_specific_exceptions',
    'error_context', 'specific_error_context', 'collect_context',
    'AppException', 'ConfigurationError', 'VideoSourceError', 
    'InputValidationError', 'ImageProcessingError', 'UIError'
]
