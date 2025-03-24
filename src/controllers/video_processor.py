"""
Path: src/controllers/video_processor.py
Controlador que maneja el procesamiento de frames de video.
Desacopla la lógica de procesamiento del componente de UI y captura.
"""

from typing import Dict, Any, Optional  # Moved standard imports before third party
import time

import cv2  # pylint: disable=no-member
import numpy as np  # pylint: disable=no-member
from src.image_processing import ProcessingController
from src.views.notifier import Notifier, ConsoleNotifier
from src.utils.simple_logger import LoggerService

get_logger = LoggerService()

class VideoProcessor:
    """
    Clase responsable del procesamiento de frames de video.
    Separa la lógica de procesamiento de la captura y la UI.
    """

    def __init__(self,
                 grados_rotacion: float = 0.0,
                 altura: float = 0.0,
                 horizontal: float = 0.0,
                 pixels_por_mm: float = 1.0,
                 notifier: Optional[Notifier] = None,
                 logger=None):
        """
        Inicializa el procesador de video.
        
        Args:
            grados_rotacion: Grados de rotación para la imagen
            altura: Ajuste vertical para la imagen
            horizontal: Ajuste horizontal para la imagen
            pixels_por_mm: Relación de píxeles por milímetro
            notifier: Notificador para mensajes (opcional)
            logger: Logger configurado (opcional)
        """
        # Añadir dimensiones por defecto
        self.default_width = 640
        self.default_height = 480

        self.logger = logger or get_logger()
        self.notifier = notifier or ConsoleNotifier(self.logger)
        self.controller = ProcessingController(notifier=self.notifier)

        # Parámetros de procesamiento
        self.grados_rotacion = grados_rotacion
        self.altura = altura
        self.horizontal = horizontal
        self.pixels_por_mm = pixels_por_mm
        self.zoom = 1.0
        self.paper_color = "Blanco"

        # Estadísticas de procesamiento
        self.stats = {
            'frames_processed': 0,
            'total_frames': 0,
            'processing_start_time': time.time(),
            'last_frame_time': time.time(),
            'current_fps': 0.0,
            'average_fps': 0.0
        }

    def update_parameters(self, parameters: Dict[str, float]) -> None:
        """
        Actualiza los parámetros de procesamiento.
        
        Args:
            parameters: Diccionario con los parámetros a actualizar
        """
        try:
            if 'grados_rotacion' in parameters:
                self.grados_rotacion = -1 * parameters['grados_rotacion']  # Mantiene la inversión

            if 'altura' in parameters:
                self.altura = parameters['altura']

            if 'horizontal' in parameters:
                self.horizontal = parameters['horizontal']

            if 'pixels_por_mm' in parameters:
                self.pixels_por_mm = parameters['pixels_por_mm']

            if 'zoom' in parameters:
                self.zoom = parameters['zoom']

            if 'paper_color' in parameters:
                self.paper_color = parameters['paper_color']

            # Actualizar el controlador de procesamiento si es necesario
            if hasattr(self, 'controller') and self.controller:
                self.controller.update_parameters(
                    self.grados_rotacion,
                    self.altura,
                    self.horizontal,
                    self.pixels_por_mm
                )

            self.logger.info(f"Parámetros de procesamiento actualizados: {parameters}")
        except Exception as e: # pylint: disable=broad-exception-caught
            self.logger.error(f"Error al actualizar parámetros: {str(e)}")
            self.notifier.notify_error("Error al actualizar parámetros", e)

    def process_frame(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Procesa un frame de video aplicando las transformaciones configuradas.
        
        Args:
            frame: Frame de video a procesar (matriz numpy)
            
        Returns:
            Frame procesado o None si hubo un error
        """
        try:
            # Procesar el frame usando el controlador
            processed_frame = self.controller.process(
                frame,
                self.grados_rotacion,
                self.altura,
                self.horizontal,
                self.pixels_por_mm
            )

            # Aplicar zoom
            height, width = frame.shape[:2]
            new_width = int(width * self.zoom)
            new_height = int(height * self.zoom)
            frame = cv2.resize(frame, (new_width, new_height))  # pylint: disable=no-member

            # Aplicar filtro de contraste según el color de papel
            if self.paper_color == "Blanco":
                frame = self.apply_white_paper_filter(frame)
            elif self.paper_color == "Marrón":
                frame = self.apply_brown_paper_filter(frame)

            # Actualizar estadísticas
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

            return processed_frame

        except Exception as e:  # pylint: disable=broad-exception-caught
            self.logger.error(f"Error al procesar frame: {str(e)}")
            self.notifier.notify_error("Error al procesar frame", e)
            return None

    def scale_frame_to_size(self,
                            frame: np.ndarray,
                            target_width: Optional[int] = None,
                            target_height: Optional[int] = None) -> Optional[np.ndarray]:
        """
        Escala un frame para llenar el máximo espacio disponible manteniendo el aspecto.
        """
        try:
            if frame is None:
                return None

            # Use default values if target dimensions are None
            if target_width is None or target_height is None:
                target_width = self.default_width if target_width is None else target_width
                target_height = self.default_height if target_height is None else target_height
                self.logger.debug(f"Using default dimensions for scaling: {target_width}x{target_height}")

            # Verificar dimensiones válidas
            if target_width <= 0 or target_height <= 0:
                self.logger.warning(f"Invalid target dimensions: {target_width}x{target_height}, using defaults")
                target_width = max(self.default_width, 1)
                target_height = max(self.default_height, 1)

            # Convertir a RGB primero
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Calcular dimensiones
            image_height, image_width = frame_rgb.shape[:2]
            
            # Calcular ratios de escalado para ambas dimensiones
            width_ratio = target_width / image_width
            height_ratio = target_height / image_height
            
            # Usar el ratio menor para mantener la imagen visible completa
            scale = min(width_ratio, height_ratio)
            
            # Calcular nuevas dimensiones
            new_width = int(image_width * scale)
            new_height = int(image_height * scale)

            # Realizar el escalado
            resized_frame = cv2.resize(
                frame_rgb, 
                (new_width, new_height),
                interpolation=cv2.INTER_LINEAR
            )

            # Crear imagen negra del tamaño objetivo
            final_frame = np.zeros((target_height, target_width, 3), dtype=np.uint8)

            # Calcular posición para centrar
            y_offset = (target_height - new_height) // 2
            x_offset = (target_width - new_width) // 2

            # Insertar imagen escalada en el centro
            final_frame[y_offset:y_offset+new_height, 
                       x_offset:x_offset+new_width] = resized_frame

            return final_frame

        except Exception as e:
            self.logger.error(f"Error al escalar frame: {str(e)}")
            return None

    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Obtiene las estadísticas actuales del procesamiento.
        
        Returns:
            Diccionario con estadísticas de procesamiento
        """
        return {
            'frames_processed': self.stats['frames_processed'],
            'fps_current': round(self.stats['current_fps'], 1),
            'fps_average': round(self.stats['average_fps'], 1),
            'processing_time': round(time.time() - self.stats['processing_start_time'], 1)
        }

    def reset_stats(self) -> None:
        """Reinicia las estadísticas de procesamiento."""
        self.stats = {
            'frames_processed': 0,
            'total_frames': 0,
            'processing_start_time': time.time(),
            'last_frame_time': time.time(),
            'current_fps': 0.0,
            'average_fps': 0.0
        }

    def process_image(self, image):
        """
        Procesa una imagen y detecta objetos.
        
        Args:
            image: Imagen a procesar
            
        Returns:
            Imagen procesada con detecciones
        """
        try:
            # Usar el controlador de procesamiento para procesar la imagen
            if self.controller:
                return self.controller.process(
                    image,
                    self.grados_rotacion,
                    self.altura,
                    self.horizontal,
                    self.pixels_por_mm
                )
            return image
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.logger.error(f"Error de procesamiento de imagen: {str(e)}")

            # Si hay un notificador, usar el método actualizado
            if hasattr(self, 'notifier') and self.notifier:
                # Usar correctamente el método, con message como único parámetro
                self.notifier.notify_error(f"Error de procesamiento de imagen: {str(e)}")

            return image

    def apply_white_paper_filter(self, frame):
        " Aplica un filtro de contraste para papel blanco a un frame"
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # pylint: disable=no-member
        _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)  # pylint: disable=no-member
        frame[binary == 0] = (0, 0, 0)
        return frame

    def apply_brown_paper_filter(self, frame):
        " Lógica para aplicar filtro de contraste para papel marrón "
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # pylint: disable=no-member
        _, binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)  # pylint: disable=no-member
        frame[binary == 0] = (255, 0, 0)
        return frame
