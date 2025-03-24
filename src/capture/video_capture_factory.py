"""
Path: src/capture/video_capture_factory.py
Fábrica para crear instancias de capturas de video según el tipo de fuente.
"""

from typing import Union, Optional
from src.capture.video_capture_interface import VideoCapture
from src.capture.local_video_capture import LocalVideoCapture
from src.capture.http_video_capture import HttpVideoCapture
from src.utils.simple_logger import LoggerService

get_logger = LoggerService()

class VideoCaptureFactory:
    """
    Factory para crear la implementación adecuada de VideoCapture
    según el tipo de fuente especificada.
    """

    @staticmethod
    def create_capture(source: Union[str, int],
                      fps_limit: Optional[float] = None,
                      logger=None) -> VideoCapture:
        """
        Crea y devuelve la implementación adecuada de VideoCapture.
        
        Args:
            source: URL HTTP o índice/ruta de cámara local
            fps_limit: Límite de FPS para fuentes locales (no aplica a HTTP)
            logger: Logger configurado (opcional)
            
        Returns:
            Instancia de VideoCapture apropiada para la fuente
            
        Raises:
            ValueError: Si no se puede determinar el tipo de fuente
        """
        logger = logger or get_logger()

        # Determinar el tipo de fuente
        if isinstance(source, str) and source.lower().startswith('http'):
            logger.info(f"Creando captura HTTP para: {source}")
            return HttpVideoCapture(url=source, logger=logger)
        elif isinstance(source, (str, int)):
            logger.info(f"Creando captura local para: {source}")
            return LocalVideoCapture(source=source, fps_limit=fps_limit, logger=logger)
        else:
            logger.error(f"Tipo de fuente no soportado: {type(source)}")
            raise ValueError(f"Tipo de fuente no soportado: {type(source)}")
