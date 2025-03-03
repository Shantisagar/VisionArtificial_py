"""
Path: src/controllers/video_stream_controller.py
Controlador que coordina la interacción entre el modelo de video y su vista.
"""

from typing import Optional
import logging
from src.models.video_stream_model import VideoStreamModel
from src.views.video_stream_view import VideoStreamView
from src.views.notifier import Notifier

class VideoStreamController:
    "Controlador que coordina la interacción entre el modelo de video y su vista."
    def __init__(self, logger: logging.Logger, notifier: Optional[Notifier] = None):
        self.logger = logger
        self.notifier = notifier
        self.model: Optional[VideoStreamModel] = None
        self.view: Optional[VideoStreamView] = None
        self.running = False

    def initialize(self, root, video_url: str, grados_rotacion: float,
                  altura: float, horizontal: float, pixels_por_mm: float) -> bool:
        """Inicializa el controlador con modelo y vista."""
        try:
            # Crear e inicializar modelo
            self.model = VideoStreamModel(logger=self.logger, notifier=self.notifier)
            if not self.model.initialize(
                video_url, grados_rotacion, altura, horizontal, pixels_por_mm
            ):
                raise RuntimeError("Fallo al inicializar el modelo")

            # Crear e inicializar vista
            self.view = VideoStreamView(root, logger=self.logger)
            self.view.setup_ui()
            self.view.set_frame_update_callback(self._update_frame)

            return True
        except RuntimeError as e:
            self.logger.error(f"Error al inicializar controlador: {e}")
            if self.notifier:
                self.notifier.notify_error(f"Error de inicialización: {e}")
            return False

    def start(self) -> bool:
        """Inicia la captura y visualización."""
        try:
            if not self.model or not self.view:
                raise RuntimeError("Controlador no inicializado")

            if not self.model.start():
                raise RuntimeError("Fallo al iniciar la captura")

            self.running = True
            self.view.start_updates()
            return True

        except (RuntimeError, ValueError) as e:
            self.logger.error(f"Error al iniciar controlador: {e}")
            if self.notifier:
                self.notifier.notify_error(f"Error al iniciar: {e}")
            return False

    def stop(self) -> None:
        """Detiene la captura y visualización."""
        self.running = False
        if self.model:
            self.model.stop()
        if self.view:
            self.view.stop()

    def _update_frame(self) -> None:
        """Callback para actualizar frames desde el modelo a la vista."""
        if self.running and self.model and self.view:
            try:
                frame = self.model.get_latest_frame()
                if frame is not None:
                    self.view.update_frame(frame)
            except (RuntimeError, ValueError) as e:
                self.logger.error(f"Error al actualizar frame: {e}")

    def update_parameters(self, parameters: dict) -> None:
        """Actualiza los parámetros del modelo."""
        if self.model:
            self.model.update_parameters(parameters)

    def get_processing_stats(self) -> dict:
        """Obtiene estadísticas del procesamiento."""
        return self.model.get_processing_stats() if self.model else {}
