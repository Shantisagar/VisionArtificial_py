# pylint: disable=unnecessary-pass
"""
Path: src/capture/video_capture_interface.py
Interfaz para las clases de captura de video.
Define un contrato común para diferentes fuentes de video.
"""

import abc
from typing import Callable
import numpy as np

class VideoCapture(abc.ABC):
    """
    Interfaz abstracta para fuentes de captura de video.
    Define métodos comunes que deben implementar todas las fuentes de video.
    """

    @abc.abstractmethod
    def start(self) -> bool:
        """
        Inicia la captura de video.
        
        Returns:
            bool: True si la captura se inició correctamente, False en caso contrario
        """
        pass

    @abc.abstractmethod
    def stop(self) -> None:
        """
        Detiene la captura de video y libera recursos.
        """
        pass

    @abc.abstractmethod
    def is_running(self) -> bool:
        """
        Verifica si la captura está activa.
        
        Returns:
            bool: True si la captura está activa, False en caso contrario
        """
        pass

    @abc.abstractmethod
    def set_frame_callback(self, callback: Callable[[np.ndarray], None]) -> None:
        """
        Establece el callback que será llamado cuando se captura un nuevo frame.
        
        Args:
            callback: Función que recibe un frame y lo procesa
        """
        pass

    @property
    @abc.abstractmethod
    def source_info(self) -> dict:
        """
        Proporciona información sobre la fuente de video.
        
        Returns:
            dict: Diccionario con información de la fuente
        """
        pass
