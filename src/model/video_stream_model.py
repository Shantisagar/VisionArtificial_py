"""
Path: src/model/video_stream_model.py
Modelo para manejar la captura y procesamiento de video.
Encapsula la lógica de negocio relacionada con el streaming de video.
"""

import queue
import threading
import time
from typing import Optional, Dict, Any
import cv2
import numpy as np
from src.capture.video_capture_factory import VideoCaptureFactory
from src.controllers.video_processor import VideoProcessor
from src.views.notifier import Notifier, ConsoleNotifier
from utils.logging.logger_configurator import get_logger

# pylint: disable=no-member

class VideoStreamModel:
    """
    Modelo que maneja la captura y procesamiento de video.
    Implementa el patrón Observer para notificar cambios en el estado.
    """

    def __init__(self, logger=None, notifier: Optional[Notifier] = None):
        """
        Inicializa el modelo de streaming de video.
        
        Args:
            logger: Logger configurado (opcional)
            notifier: Notificador para mensajes al usuario (opcional)
        """
        self.logger = logger or get_logger()
        self.notifier = notifier or ConsoleNotifier(self.logger)

        # Cola para frames procesados
        self.frame_queue = queue.Queue(maxsize=10)

        # Estado del modelo
        self.running = False
        self.video_capture = None
        self.capture_lock = threading.Lock()

        # Componentes de procesamiento
        self.video_processor = None

        # Estadísticas
        self.stats = {
            'frames_processed': 0,
            'total_frames': 0,
            'processing_start_time': time.time(),
            'last_frame_time': time.time(),
            'current_fps': 0.0,
            'average_fps': 0.0
        }

    def initialize(self, video_url: str,
                  grados_rotacion: float,
                  altura: float,
                  horizontal: float,
                  pixels_por_mm: float) -> bool:
        """
        Inicializa el modelo con los parámetros especificados.
        
        Args:
            video_url: URL o índice de la fuente de video
            grados_rotacion: Grados de rotación para la imagen
            altura: Ajuste vertical para la imagen
            horizontal: Ajuste horizontal para la imagen
            pixels_por_mm: Relación de píxeles por milímetro
            
        Returns:
            bool: True si la inicialización fue exitosa
        """
        try:
            # Inicializar el procesador de video
            self.video_processor = VideoProcessor(
                grados_rotacion=grados_rotacion,
                altura=altura,
                horizontal=horizontal,
                pixels_por_mm=pixels_por_mm,
                notifier=self.notifier,
                logger=self.logger
            )

            # Crear la instancia de captura usando la fábrica
            with self.capture_lock:
                self.video_capture = VideoCaptureFactory.create_capture(
                    source=video_url,
                    fps_limit=30,
                    logger=self.logger
                )

                # Establecer callback para procesar frames
                self.video_capture.set_frame_callback(self.process_and_enqueue)

            self.logger.info("Modelo de video inicializado correctamente")
            return True

        except Exception as e:
            self.logger.error(f"Error al inicializar el modelo de video: {str(e)}")
            self.notifier.notify_error("Error al inicializar la captura de video")
            return False

    def start(self) -> bool:
        """
        Inicia la captura y procesamiento de video.
        
        Returns:
            bool: True si se inició correctamente
        """
        try:
            if self.video_capture is None:
                raise RuntimeError("El modelo no está inicializado")

            self.running = True
            self.stats['processing_start_time'] = time.time()

            # Iniciar la captura de video
            with self.capture_lock:
                if not self.video_capture.start():
                    raise RuntimeError("No se pudo iniciar la captura de video")

            self.logger.info("Captura de video iniciada correctamente")
            return True

        except Exception as e:
            self.logger.error(f"Error al iniciar la captura de video: {str(e)}")
            self.notifier.notify_error("Error al iniciar la captura de video")
            self.running = False
            return False

    def stop(self) -> None:
        """Detiene la captura y procesamiento de video."""
        self.logger.info("Deteniendo captura de video...")
        self.running = False

        # Detener la captura de video
        with self.capture_lock:
            if self.video_capture:
                self.video_capture.stop()

        # Limpiar la cola de frames
        with self.frame_queue.mutex:
            self.frame_queue.queue.clear()

        self.logger.info("Captura de video detenida correctamente")

    def process_and_enqueue(self, frame: np.ndarray) -> None:
        """Procesa un frame y lo coloca en la cola."""
        try:
            if not self.running or frame is None:
                return

            # Inicializar dimensiones objetivo si no existen
            if not hasattr(self, 'target_width') or not hasattr(self, 'target_height'):
                # Usar dimensiones del frame como valores iniciales
                height, width = frame.shape[:2]
                self.target_width = width
                self.target_height = height
                self.logger.debug(f"Dimensiones iniciales establecidas: {width}x{height}")

            # Verificar que tenemos dimensiones válidas
            if not hasattr(self, 'target_width') or not hasattr(self, 'target_height'):
                self.target_width = self.video_processor.default_width
                self.target_height = self.video_processor.default_height

            # Procesar el frame usando el procesador de video
            processed_frame = self.video_processor.process_frame(frame)

            if processed_frame is not None:
                # Escalar el frame al tamaño del contenedor
                scaled_frame = self.video_processor.scale_frame_to_size(
                    processed_frame,
                    self.target_width,
                    self.target_height
                )

                if scaled_frame is not None:
                    # Ya no necesitamos convertir a RGB aquí porque scale_frame_to_size ya lo hace
                    self.frame_queue.put(scaled_frame)

                    # Actualizar estadísticas
                    self._update_stats()

        except Exception as e:
            self.logger.error(f"Error al procesar frame: {str(e)}")
            self.notifier.notify_error("Error al procesar frame")

    def _update_stats(self) -> None:
        """Actualiza las estadísticas de procesamiento."""
        try:
            current_time = time.time()
            self.stats['frames_processed'] += 1
            self.stats['total_frames'] += 1

            # Calcular FPS actual
            time_diff = current_time - self.stats['last_frame_time']
            if time_diff > 0:
                self.stats['current_fps'] = 1.0 / time_diff

            # Calcular FPS promedio
            total_time = current_time - self.stats['processing_start_time']
            if total_time > 0:
                self.stats['average_fps'] = self.stats['total_frames'] / total_time

            self.stats['last_frame_time'] = current_time
        except Exception as e:
            self.logger.error(f"Error al actualizar estadísticas: {str(e)}")

    def get_latest_frame(self) -> Optional[np.ndarray]:
        """
        Obtiene el último frame procesado de la cola.
        
        Returns:
            np.ndarray: Último frame procesado o None si no hay frames
        """
        try:
            return self.frame_queue.get_nowait()
        except queue.Empty:
            return None

    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Obtiene las estadísticas actuales del procesamiento.
        
        Returns:
            Dict con estadísticas de procesamiento
        """
        return {
            'frames_processed': self.stats['frames_processed'],
            'fps_current': round(self.stats['current_fps'], 1),
            'fps_average': round(self.stats['average_fps'], 1),
            'processing_time': round(time.time() - self.stats['processing_start_time'], 1)
        }

    def update_parameters(self, parameters: Dict[str, float]) -> None:
        """
        Actualiza los parámetros de procesamiento.
        
        Args:
            parameters: Diccionario con los nuevos valores de parámetros
        """
        try:
            if self.video_processor:
                self.video_processor.update_parameters(parameters)
                self.logger.info(f"Parámetros actualizados: {parameters}")
            else:
                self.logger.warning(
                    "No se pueden actualizar parámetros: procesador no inicializado"
                )

        except Exception as e:
            self.logger.error(f"Error al actualizar parámetros: {str(e)}")
            self.notifier.notify_error("Error al actualizar parámetros")

    def set_target_size(self, width: int, height: int) -> None:
        """Establece el tamaño objetivo para el escalado de frames."""
        # Asegurar valores mínimos razonables
        width = max(width, 320)
        height = max(height, 240)

        # Solo actualizar si hay un cambio significativo en el tamaño
        if hasattr(self, 'target_width') and hasattr(self, 'target_height'):
            width_change = abs(self.target_width - width)
            height_change = abs(self.target_height - height)
            
            # Ignorar cambios menores al 2%
            if (width_change / self.target_width < 0.02 and 
                height_change / self.target_height < 0.02):
                return

        self.target_width = width
        self.target_height = height
        self.logger.debug(
            f"Tamaño objetivo actualizado: {self.target_width}x{self.target_height}"
        )
