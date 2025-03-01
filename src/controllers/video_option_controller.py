"""
Path: src/controllers/video_option_controller.py
Controlador para la selección y configuración de fuentes de video.
Simplificado para usar solo la cámara web como fuente.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class VideoSource(ABC):
    """Interfaz para fuentes de video que define el contrato para todas las implementaciones."""

    @abstractmethod
    def get_source_url(self, config: Dict[str, Any]) -> Any:
        """
        Obtiene la URL o identificador para la fuente de video.
        
        Args:
            config: Configuración necesaria para construir la URL
            
        Returns:
            URL, path o identificador para la fuente de video
        """
        pass

    @abstractmethod
    def get_description(self) -> str:
        """
        Obtiene una descripción de la fuente de video.
        
        Returns:
            Descripción legible para el usuario
        """
        pass

    @abstractmethod
    def get_option_key(self) -> str:
        """
        Obtiene la clave de opción para esta fuente de video.
        
        Returns:
            Clave única que identifica esta fuente de video
        """
        pass


class WebcamSource(VideoSource):
    """Fuente de video para cámara web local."""

    def get_source_url(self, config: Dict[str, Any]) -> int:
        """Devuelve el índice de la cámara web."""
        return 0  # Índice para cámara web por defecto

    def get_description(self) -> str:
        """Devuelve la descripción de la fuente de cámara web."""
        return "Cámara web"

    def get_option_key(self) -> str:
        """Devuelve la clave de opción para cámara web."""
        return "1"  # Cambiado de "3" a "1" para ser la opción principal


class VideoOptionController:
    """
    Controlador simplificado para la selección de fuentes de video.
    Ahora solo trabaja con la fuente WebcamSource.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Inicializa el controlador con la fuente de cámara web.
        
        Args:
            logger: Logger para registrar eventos
        """
        self.logger = logger
        self._source = WebcamSource()

        if self.logger:
            self.logger.debug(
                f"Inicializado controlador de video con fuente: {self._source.get_description()}"
            )

    def get_menu_options(self) -> List[str]:
        """
        Genera las opciones de menú para mostrar al usuario.
        
        Returns:
            Lista con la opción de cámara web
        """
        return [f"{self._source.get_option_key()} - {self._source.get_description()}"]

    def get_source_url(self, option_key: str, config: Dict[str, Any]) -> Any:
        """
        Obtiene la URL de la cámara web. Ignora el parámetro option_key ya que
        solo hay una fuente disponible.
        
        Args:
            option_key: Ignorado, se mantiene por compatibilidad con interfaz existente
            config: Configuración necesaria para construir la URL
            
        Returns:
            Índice de la cámara web (0)
        """
        if self.logger:
            self.logger.info(f"Usando fuente de video: {self._source.get_description()}")

        return self._source.get_source_url(config)
