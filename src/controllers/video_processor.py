"""
Path: src/controllers/video_processor.py
Controlador que maneja el procesamiento de frames de video.
Desacopla la lógica de procesamiento del componente de UI y captura.
"""

import time
import cv2
import numpy as np
from typing import Dict, Tuple, Any, Optional
from src.image_processing import ProcessingController
from src.views.notifier import Notifier, ConsoleNotifier
from utils.logging.logger_configurator import get_logger

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
        self.logger = logger or get_logger()
        self.notifier = notifier or ConsoleNotifier(self.logger)
        self.controller = ProcessingController(notifier=self.notifier)
        
        # Parámetros de procesamiento
        self.grados_rotacion = grados_rotacion
        self.altura = altura
        self.horizontal = horizontal
        self.pixels_por_mm = pixels_por_mm
        
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
                
            # Actualizar el controlador de procesamiento si es necesario
            if hasattr(self, 'controller') and self.controller:
                self.controller.update_parameters(
                    self.grados_rotacion,
                    self.altura,
                    self.horizontal,
                    self.pixels_por_mm
                )
                
            self.logger.info(f"Parámetros de procesamiento actualizados: {parameters}")
        except Exception as e:
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
        
        except Exception as e:
            self.logger.error(f"Error al procesar frame: {str(e)}")
            self.notifier.notify_error("Error al procesar frame", e)
            return None
    
    def scale_frame_to_size(self, frame: np.ndarray, target_width: int, target_height: int) -> Optional[np.ndarray]:
        """
        Escala un frame para ajustarlo a un tamaño objetivo manteniendo la relación de aspecto.
        
        Args:
            frame: Frame a escalar
            target_width: Ancho máximo objetivo
            target_height: Alto máximo objetivo
            
        Returns:
            Frame escalado o None si hubo un error
        """
        try:
            if frame is None:
                return None
                
            image_height, image_width = frame.shape[:2]
            scale_width = target_width / image_width
            scale_height = target_height / image_height
            scale = min(scale_width, scale_height)
            
            new_width = int(image_width * scale)
            new_height = int(image_height * scale)
            
            resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
            return cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            
        except cv2.error.CvError as e:
            self.logger.error(f"Error de OpenCV al escalar la imagen: {e}")
            return None
        except (ValueError, TypeError) as e:
            self.logger.error(f"Error al escalar la imagen: {e}")
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
        except Exception as e:
            self.logger.error(f"Error de procesamiento de imagen: {str(e)}")
            
            # Si hay un notificador, usar el método actualizado
            if hasattr(self, 'notifier') and self.notifier:
                # Usar correctamente el método, con message como único parámetro
                self.notifier.notify_error(f"Error de procesamiento de imagen: {str(e)}")
                
            return image
