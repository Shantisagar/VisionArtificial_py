"""
Path: src/capture/http_video_capture.py
Implementación de captura de video para fuentes HTTP.
Incluye mecanismos para backoff exponencial y manejo de errores.
"""

import threading
import time
from typing import Callable
import requests
import cv2
import numpy as np
from src.capture.video_capture_interface import VideoCapture
from src.utils.simple_logger import LoggerService

get_logger = LoggerService()

class HttpVideoCapture(VideoCapture):
    """
    Implementación concreta para capturar video desde fuentes HTTP.
    Maneja conexiones inestables utilizando backoff exponencial.
    """

    def __init__(self, url: str, interval: float = 2.5, max_retries: int = 10,
                 max_backoff: float = 10.0, logger=None):
        """
        Inicializa la captura de video HTTP.
        
        Args:
            url: URL de la fuente HTTP
            interval: Intervalo entre capturas en segundos
            max_retries: Número máximo de intentos antes de exponential backoff
            max_backoff: Tiempo máximo de espera entre reintentos (segundos)
            logger: Logger configurado (opcional)
        """
        self.url = url
        self.interval = interval
        self.max_retries = max_retries
        self.max_backoff = max_backoff
        self.logger = logger or get_logger()
        self._running = False
        self._thread = None
        self._frame_callback = None
        self._error_count = 0
        self._last_successful_capture = 0
        self._last_frame_shape = None

    def start(self) -> bool:
        """
        Inicia la captura de video desde la fuente HTTP.
        
        Returns:
            bool: True si se inicia correctamente, False en caso de error
        """
        if self._running:
            self.logger.warning("La captura HTTP ya está en ejecución")
            return True

        try:
            # Verificar que la URL es accesible
            response = requests.head(self.url, timeout=5)
            if response.status_code >= 400:
                self.logger.error(
                    f"La URL no es accesible: {self.url}, código: {response.status_code}"
                )
                return False

            self._running = True
            self._error_count = 0
            self._thread = threading.Thread(target=self._http_capture_loop, daemon=True)
            self._thread.start()
            self.logger.info(f"Iniciada captura de video HTTP desde: {self.url}")
            return True

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error al verificar URL: {e}")
            return False
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.logger.error(f"Error al iniciar captura HTTP: {e}")
            return False

    def stop(self) -> None:
        """
        Detiene la captura de video y libera recursos.
        """
        self._running = False

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

        self.logger.info("Captura de video HTTP detenida")

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

    def _http_capture_loop(self) -> None:
        """
        Bucle principal de captura HTTP que se ejecuta en un hilo separado.
        Implementa backoff exponencial para manejar errores de conexión.
        """
        while self._running:
            try:
                # Calcular tiempo de espera basado en número de errores (backoff exponencial)
                wait_time = min(
                    self.interval * (1.5 ** min(self._error_count, 10)),
                    self.max_backoff
                )

                response = requests.get(self.url, timeout=5)
                if response.status_code == 200:
                    # Convertir bytes de la respuesta a una imagen
                    image_bytes = np.asarray(bytearray(response.content), dtype=np.uint8)
                    frame = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)  # pylint: disable=no-member

                    if frame is not None:
                        # Guardar información del frame
                        self._last_frame_shape = frame.shape
                        self._last_successful_capture = time.time()
                        self._error_count = 0  # Resetear contador de errores

                        # Llamar al callback si está configurado
                        if self._frame_callback:
                            self._frame_callback(frame)
                    else:
                        self._error_count += 1
                        self.logger.error("No se pudo decodificar la imagen HTTP")
                else:
                    self._error_count += 1
                    self.logger.error(f"Error HTTP: {response.status_code}")

                # Esperar antes de la siguiente captura
                time.sleep(wait_time)

            except requests.exceptions.RequestException as e:
                self._error_count += 1
                wait_time = min(
                    self.interval * (1.5 ** min(self._error_count, 10)),
                    self.max_backoff
                )
                self.logger.error(f"Error de conexión HTTP: {e}. Reintentando en {wait_time:.1f}s")
                time.sleep(wait_time)
            except Exception as e:  # pylint: disable=broad-exception-caught
                self._error_count += 1
                wait_time = min(
                    self.interval * (1.5 ** min(self._error_count, 10)),
                    self.max_backoff
                )
                self.logger.error(f"Error en captura HTTP: {e}. Reintentando en {wait_time:.1f}s")
                time.sleep(wait_time)

    @property
    def source_info(self) -> dict:
        """
        Proporciona información sobre la fuente de video.
        
        Returns:
            dict: Información de la fuente HTTP
        """
        info = {
            'type': 'http',
            'url': self.url,
            'interval': self.interval,
            'width': None,
            'height': None,
            'time_since_last_frame': None,
            'error_count': self._error_count
        }

        # Agregar información del último frame si está disponible
        if self._last_frame_shape:
            info['height'] = self._last_frame_shape[0]
            info['width'] = self._last_frame_shape[1]

        # Calcular tiempo desde la última captura exitosa
        if self._last_successful_capture > 0:
            info['time_since_last_frame'] = time.time() - self._last_successful_capture

        return info
