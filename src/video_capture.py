"""
Path: src/video_capture.py
Define la interfaz para la captura de video.
Clase base abstracta para diferentes implementaciones de captura de video.
"""

import abc
import logging
import numpy as np
from typing import Tuple, Optional

class VideoCapture(abc.ABC):
    """Clase base abstracta para la captura de video."""
    
    def __init__(self, source, logger: logging.Logger):
        """
        Inicializa la captura de video.
        
        Args:
            source: Fuente de video (puede ser un índice de cámara o URL)
            logger: Logger configurado para registrar eventos
        """
        self.source = source
        self.logger = logger
        self.is_running = False
        self.logger.debug(f"Inicializada clase base VideoCapture con fuente: {source}")
        
    @abc.abstractmethod
    def start(self) -> bool:
        """
        Inicia la captura de video.
        
        Returns:
            True si se inició correctamente, False en caso contrario
        """
        pass
    
    @abc.abstractmethod
    def stop(self) -> None:
        """Detiene la captura de video."""
        pass
    
    @abc.abstractmethod
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Lee un frame de la fuente de video.
        
        Returns:
            Tupla (éxito, frame) donde éxito es un booleano y frame es un array NumPy o None
        """
        pass
    
    @abc.abstractmethod
    def is_opened(self) -> bool:
        """
        Verifica si la captura está abierta y funcionando.
        
        Returns:
            True si la captura está abierta, False en caso contrario
        """
        pass
