"""
Excepciones personalizadas para la aplicación.
Permite la categorización de errores y un manejo más específico.
"""

# Base exception for all application exceptions
class AppException(Exception):
    """Excepción base para todas las excepciones de la aplicación."""

    def __init__(self, message: str, *args):
        """
        Inicializa la excepción con un mensaje descriptivo.
        
        Args:
            message: Mensaje descriptivo del error
            args: Argumentos adicionales
        """
        self.message = message
        super().__init__(message, *args)


# Configuration errors
class ConfigurationError(AppException):
    """Error relacionado con la configuración de la aplicación."""
    # No empty pass statement needed


class ConfigFileNotFoundError(ConfigurationError):
    """El archivo de configuración no fue encontrado."""

    def __init__(self, file_path: str, *args):
        """
        Inicializa la excepción con la ruta del archivo.
        
        Args:
            file_path: Ruta del archivo de configuración
            args: Argumentos adicionales
        """
        message = f"Archivo de configuración no encontrado: {file_path}"
        self.file_path = file_path
        super().__init__(message, *args)


class ConfigParsingError(ConfigurationError):
    """Error al interpretar el archivo de configuración."""
    # No empty pass statement needed


# Video source errors
class VideoSourceError(AppException):
    """Error relacionado con la fuente de video."""
    # No empty pass statement needed


class VideoConnectionError(VideoSourceError):
    """Error de conexión con la fuente de video."""
    # No empty pass statement needed


class InvalidVideoOptionError(VideoSourceError):
    """Opción de video no válida."""

    def __init__(self, option: str, *args):
        """
        Inicializa la excepción con la opción inválida.
        
        Args:
            option: Opción de video inválida
            args: Argumentos adicionales
        """
        message = f"Opción de video no válida: {option}"
        self.option = option
        super().__init__(message, *args)


# Input validation errors
class InputValidationError(AppException):
    """Error de validación de entrada."""
    # No empty pass statement needed


class NumericRangeError(InputValidationError):
    """Valor numérico fuera del rango permitido."""

    def __init__(self, param_name: str, value: float, min_val: float, max_val: float, *args):
        """
        Inicializa la excepción con detalles del rango válido.
        
        Args:
            param_name: Nombre del parámetro
            value: Valor proporcionado
            min_val: Valor mínimo permitido
            max_val: Valor máximo permitido
            args: Argumentos adicionales
        """
        message = (
            f"El valor {value} para '{param_name}' está fuera del rango permitido: "
            f"[{min_val}, {max_val}]"
        )
        self.param_name = param_name
        self.value = value
        self.min_val = min_val
        self.max_val = max_val
        super().__init__(message, *args)


class RequiredParameterError(InputValidationError):
    """Falta un parámetro requerido."""

    def __init__(self, param_name: str, *args):
        """
        Inicializa la excepción con el nombre del parámetro.
        
        Args:
            param_name: Nombre del parámetro requerido
            args: Argumentos adicionales
        """
        message = f"Parámetro requerido no proporcionado: {param_name}"
        self.param_name = param_name
        super().__init__(message, *args)


# Image processing errors
class ImageProcessingError(AppException):
    """Error durante el procesamiento de la imagen."""
    # No empty pass statement needed


class FrameCapturingError(ImageProcessingError):
    """Error al capturar un frame de video."""
    # No empty pass statement needed


class ImageTransformationError(ImageProcessingError):
    """Error al transformar una imagen."""
    # No empty pass statement needed


# UI errors
class UIError(AppException):
    """Error relacionado con la interfaz de usuario."""
    # No empty pass statement needed


class UIInitializationError(UIError):
    """Error al inicializar la interfaz de usuario."""
    # No empty pass statement needed


class UIRenderingError(UIError):
    """Error al renderizar elementos de la interfaz."""
    # No empty pass statement needed
