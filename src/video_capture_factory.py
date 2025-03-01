"""
Path: src/video_capture_factory.py
Factory para crear diferentes tipos de captura de video.
Selecciona la implementación adecuada según la fuente proporcionada.
"""

import logging
import re
import os
from typing import Union

from src.video_capture import VideoCapture
from src.local_video_capture import LocalVideoCapture
from src.network_video_capture import NetworkVideoCapture

class VideoCaptureFactory:
    """Factory para crear capturas de video de diferentes fuentes."""
    
    @staticmethod
    def create_capture(source: Union[int, str], logger: logging.Logger) -> VideoCapture:
        """
        Crea una instancia de captura de video apropiada según la fuente.
        
        Args:
            source: Fuente de video (índice de cámara, ruta de archivo o URL)
            logger: Logger configurado para registrar eventos
            
        Returns:
            Instancia de VideoCapture apropiada para la fuente proporcionada
        """
        # Si la fuente es un entero, es una cámara local
        if isinstance(source, int):
            logger.info(f"Creando captura local para: {source}")
            return LocalVideoCapture(source, logger)
        
        # Si es una cadena, determinar si es un archivo local o una URL
        if isinstance(source, str):
            # Comprobar si es una URL (http, rtsp, etc.)
            if re.match(r'^(https?|rtsp|rtmp)://', source):
                logger.info(f"Creando captura de red para: {source}")
                return NetworkVideoCapture(source, logger)
                
            # Comprobar si es una ruta de archivo que existe
            if os.path.isfile(source):
                logger.info(f"Creando captura de archivo local: {source}")
                return LocalVideoCapture(source, logger)
                
            # Si es un número como cadena, convertir a entero y usar captura local
            if source.isdigit():
                index = int(source)
                logger.info(f"Creando captura local para índice numérico: {index}")
                return LocalVideoCapture(index, logger)
        
        # Por defecto, intentar captura local
        logger.warning(f"Tipo de fuente no reconocido: {source}, intentando captura local")
        return LocalVideoCapture(source, logger)