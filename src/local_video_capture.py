"""
Path: src/local_video_capture.py
Implementación de VideoCapture para cámaras locales y archivos de video.
Utiliza OpenCV para la captura.
"""

import cv2
import logging
import time
import numpy as np
from typing import Tuple, Optional, Union

from src.video_capture import VideoCapture

class LocalVideoCapture(VideoCapture):
    """Implementación de VideoCapture para cámaras locales y archivos de video."""
    
    def __init__(self, source: Union[int, str], logger: logging.Logger):
        """
        Inicializa la captura local.
        
        Args:
            source: Fuente de video (índice de cámara o ruta de archivo)
            logger: Logger configurado para registrar eventos
        """
        super().__init__(source, logger)
        self.cap = None
        self.logger.debug(f"Iniciando LocalVideoCapture para fuente: {source}")
        
    def start(self) -> bool:
        """
        Inicia la captura de video.
        
        Returns:
            True si se inició correctamente, False en caso contrario
        """
        if self.is_running:
            return True
            
        try:
            self.logger.debug(f"Abriendo captura para fuente: {self.source}")
            self.cap = cv2.VideoCapture(self.source)
            if not self.cap.isOpened():
                self.logger.error(f"No se pudo abrir la fuente de video: {self.source}")
                return False
                
            # Intentar leer un frame para verificar que la captura funciona
            ret, _ = self.cap.read()
            if not ret:
                self.logger.error("La captura se abrió pero no se pueden leer frames")
                return False
                
            self.is_running = True
            self.logger.info(f"Iniciada captura de video desde fuente local: {self.source}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al iniciar la captura de video: {e}")
            return False
        
    def stop(self) -> None:
        """Detiene la captura de video."""
        if not self.is_running:
            return
            
        try:
            self.logger.debug("Deteniendo captura de video local")
            if self.cap and self.cap.isOpened():
                self.cap.release()
                
            self.is_running = False
            self.logger.info("Captura de video detenida")
            
        except Exception as e:
            self.logger.error(f"Error al detener la captura de video: {e}")
        
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Lee un frame de la fuente de video.
        
        Returns:
            Tupla (éxito, frame) donde éxito es un booleano y frame es un array NumPy o None
        """
        if not self.is_running or not self.cap or not self.cap.isOpened():
            return False, None
            
        try:
            return self.cap.read()
        except Exception as e:
            self.logger.error(f"Error al leer frame: {e}")
            return False, None
    
    def is_opened(self) -> bool:
        """
        Verifica si la captura está abierta y funcionando.
        
        Returns:
            True si la captura está abierta, False en caso contrario
        """
        return self.is_running and self.cap and self.cap.isOpened()
