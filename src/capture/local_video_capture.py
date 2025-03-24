"""
Path: src/capture/local_video_capture.py
Implementación de captura de video para fuentes locales como cámaras o archivos.
"""

import threading
import time
from typing import Callable, Optional, Union
import cv2
import numpy as np
from src.capture.video_capture_interface import VideoCapture
from src.utils.simple_logger import LoggerService

get_logger = LoggerService()

class LocalVideoCapture(VideoCapture):
    """
    Implementación concreta para capturar video desde fuentes locales (cámaras, archivos, etc.)
    """

    def __init__(self, source: Union[int, str], fps_limit: Optional[float] = None, logger=None):
        """
        Inicializa la captura de video local.
        
        Args:
            source: Índice de la cámara (int) o ruta al archivo de video (str)
            fps_limit: Límite de FPS para la captura (None para no limitar)
            logger: Logger configurado (opcional)
        """
        self.source = source
        self.fps_limit = fps_limit
        self.logger = logger or get_logger()
        self.cap = None
        self._running = False
        self._thread = None
        self._frame_callback = None
        self._lock = threading.Lock()
        self._frame_interval = 0 if fps_limit is None else 1.0 / fps_limit
        self._last_frame_time = 0

    def start(self) -> bool:
        """
        Inicia la captura de video desde la fuente local.
        
        Returns:
            bool: True si se inicia la captura correctamente, False en caso de error
        """
        if self._running:
            self.logger.warning("La captura ya está en ejecución")
            return True

        try:
            with self._lock:
                self.cap = cv2.VideoCapture(self.source)  # pylint: disable=no-member
                if not self.cap.isOpened():
                    self.logger.error(f"No se pudo abrir la fuente de video: {self.source}")
                    return False

            self._running = True
            self._thread = threading.Thread(target=self._capture_loop, daemon=True)
            self._thread.start()
            self.logger.info(f"Iniciada captura de video desde fuente local: {self.source}")
            return True

        except cv2.error as e:  # pylint: disable=catching-non-exception
            self.logger.error(f"Error de OpenCV al iniciar captura: {e}")
            return False
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.logger.error(f"Error al iniciar captura de video: {e}")
            return False

    def stop(self) -> None:
        """
        Detiene la captura de video y libera recursos.
        """
        self._running = False

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

        with self._lock:
            if self.cap:
                self.cap.release()
                self.cap = None

        self.logger.info("Captura de video local detenida")

    def is_running(self) -> bool:
        """
        Verifica si la captura está activa.
        
        Returns:
            bool: True si la captura está activa, False en caso contrario
        """
        return self._running and self._thread and self._thread.is_alive()

    def set_frame_callback(self, callback: Callable[[np.ndarray], None]) -> None:
        """
        Establece el callback que será llamado cuando se captura un nuevo frame.
        
        Args:
            callback: Función que recibe un frame y lo procesa
        """
        self._frame_callback = callback

    def _capture_loop(self) -> None:
        """
        Bucle principal de captura que se ejecuta en un hilo separado.
        """
        while self._running:
            try:
                current_time = time.time()
                # Controlar el FPS si está configurado
                if self.fps_limit and (current_time - self._last_frame_time) < self._frame_interval:
                    # Dormir un pequeño intervalo para no saturar el CPU
                    time.sleep(0.001)
                    continue

                with self._lock:
                    if not self.cap or not self.cap.isOpened():
                        self.logger.warning("La captura se ha cerrado")
                        self._running = False
                        break

                    ret, frame = self.cap.read()

                if not ret:
                    self.logger.warning("No se pudo leer el frame, reintentando...")
                    time.sleep(0.1)
                    continue

                self._last_frame_time = current_time

                # Llamar al callback si está configurado
                if self._frame_callback:
                    self._frame_callback(frame)

            except cv2.error as e:  # pylint: disable=catching-non-exception
                self.logger.error(f"Error de OpenCV durante la captura: {e}")
                time.sleep(0.1)
            except Exception as e:  # pylint: disable=broad-exception-caught
                self.logger.error(f"Error en el bucle de captura: {e}")
                time.sleep(0.1)

    @property
    def source_info(self) -> dict:
        """
        Proporciona información sobre la fuente de video.
        
        Returns:
            dict: Información de la fuente, incluyendo resolución y FPS si está disponible
        """
        info = {
            'type': 'local',
            'source': self.source,
            'fps_limit': self.fps_limit,
            'width': None,
            'height': None,
            'fps': None
        }

        with self._lock:
            if self.cap and self.cap.isOpened():
                info['width'] = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # pylint: disable=no-member
                info['height'] = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # pylint: disable=no-member
                info['fps'] = self.cap.get(cv2.CAP_PROP_FPS)  # pylint: disable=no-member

        return info
