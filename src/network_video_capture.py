"""
Path: src/network_video_capture.py
Implementación de VideoCapture para cámaras de red mediante protocolos
como RTSP, HTTP, etc. Utiliza OpenCV para la captura.
"""

import cv2
import logging
import time
import numpy as np
import threading
from typing import Tuple, Optional

from src.video_capture import VideoCapture

class NetworkVideoCapture(VideoCapture):
    """Implementación de VideoCapture para cámaras de red."""
    
    def __init__(self, source: str, logger: logging.Logger):
        """
        Inicializa la captura de red.
        
        Args:
            source: URL de la fuente de video
            logger: Logger configurado para registrar eventos
        """
        super().__init__(source, logger)
        self.cap = None
        self.frame_buffer = None
        self.lock = threading.Lock()
        self.fetch_thread = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 2  # segundos
        
        self.logger.debug(f"Iniciando NetworkVideoCapture para URL: {source}")
        
    def start(self) -> bool:
        """
        Inicia la captura de video.
        
        Returns:
            True si se inició correctamente, False en caso contrario
        """
        if self.is_running:
            return True
            
        try:
            # Configurar opciones para captura de red
            self.logger.debug(f"Intentando conectar a URL: {self.source}")
            self.cap = cv2.VideoCapture(self.source)
            
            # Algunos ajustes recomendados para transmisiones de red
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
            
            if not self.cap.isOpened():
                self.logger.error(f"No se pudo abrir la URL: {self.source}")
                return False
                
            # Intentar leer un frame para verificar que la captura funciona
            ret, frame = self.cap.read()
            if not ret:
                self.logger.error("La captura se abrió pero no se pueden leer frames")
                return False
                
            # Guardar el primer frame en el buffer
            with self.lock:
                self.frame_buffer = frame
            
            self.is_running = True
            
            # Iniciar hilo para captura continua
            self.logger.debug("Iniciando hilo de captura continua")
            self.fetch_thread = threading.Thread(target=self._fetch_frames)
            self.fetch_thread.daemon = True
            self.fetch_thread.start()
            
            self.logger.info(f"Iniciada captura de video desde URL: {self.source}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al iniciar la captura de red: {e}")
            return False
        
    def stop(self) -> None:
        """Detiene la captura de video."""
        if not self.is_running:
            return
            
        try:
            self.logger.debug("Deteniendo captura de red")
            self.is_running = False
            
            # Esperar a que finalice el hilo de captura
            if self.fetch_thread and self.fetch_thread.is_alive():
                self.fetch_thread.join(timeout=1.0)
                
            # Liberar recursos
            if self.cap and self.cap.isOpened():
                self.cap.release()
                
            self.logger.info("Captura de red detenida")
            
        except Exception as e:
            self.logger.error(f"Error al detener la captura de red: {e}")
        
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Lee un frame de la fuente de video.
        
        Returns:
            Tupla (éxito, frame) donde éxito es un booleano y frame es un array NumPy o None
        """
        if not self.is_running:
            return False, None
            
        try:
            with self.lock:
                if self.frame_buffer is None:
                    return False, None
                # Devolver una copia del frame para evitar race conditions
                frame = self.frame_buffer.copy()
                
            return True, frame
            
        except Exception as e:
            self.logger.error(f"Error al leer frame de la red: {e}")
            return False, None
    
    def is_opened(self) -> bool:
        """
        Verifica si la captura está abierta y funcionando.
        
        Returns:
            True si la captura está abierta, False en caso contrario
        """
        return self.is_running and self.frame_buffer is not None
        
    def _fetch_frames(self) -> None:
        """
        Función ejecutada en un hilo separado para obtener frames
        continuamente de la fuente de red.
        """
        self.logger.debug("Iniciando hilo de captura continua de frames")
        
        while self.is_running:
            try:
                if not self.cap or not self.cap.isOpened():
                    self._try_reconnect()
                    continue
                    
                ret, frame = self.cap.read()
                
                if not ret:
                    self.logger.warning("No se pudo leer frame de la red, intentando reconectar...")
                    self._try_reconnect()
                    continue
                    
                # Actualizar el buffer con el nuevo frame
                with self.lock:
                    self.frame_buffer = frame
                    
                # Restablecer contador de reconexión si todo va bien
                self.reconnect_attempts = 0
                
            except Exception as e:
                self.logger.error(f"Error en el hilo de captura de red: {e}")
                self._try_reconnect()
                
        self.logger.debug("Finalizando hilo de captura continua de frames")
            
    def _try_reconnect(self) -> None:
        """Intenta reconectar a la fuente de video."""
        self.reconnect_attempts += 1
        
        if self.reconnect_attempts > self.max_reconnect_attempts:
            self.logger.error(f"Máximo número de intentos de reconexión alcanzado ({self.max_reconnect_attempts})")
            self.is_running = False
            return
            
        self.logger.info(f"Intento de reconexión {self.reconnect_attempts}/{self.max_reconnect_attempts}...")
        
        try:
            # Cerrar la captura existente si está abierta
            if self.cap and self.cap.isOpened():
                self.cap.release()
                
            # Esperar antes de intentar reconectar
            time.sleep(self.reconnect_delay)
            
            # Crear nueva captura
            self.cap = cv2.VideoCapture(self.source)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
            
            if not self.cap.isOpened():
                self.logger.warning("No se pudo reconectar, intentando de nuevo...")
                return
                
            # Leer un frame para verificar que funciona
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame_buffer = frame
                self.logger.info("Reconexión exitosa")
                
        except Exception as e:
            self.logger.error(f"Error durante la reconexión: {e}")
