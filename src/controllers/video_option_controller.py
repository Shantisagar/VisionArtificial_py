"""
Controlador para la selección y configuración de fuentes de video.
Implementa el patrón Strategy para permitir extensión sin modificar el controlador.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Type


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


class TestingSource(VideoSource):
    """Fuente de video para pruebas usando una imagen estática."""
    
    def get_source_url(self, config: Dict[str, Any]) -> str:
        """Devuelve la ruta a la imagen de prueba."""
        return config["ubicacion_default"]
    
    def get_description(self) -> str:
        """Devuelve la descripción de la fuente de prueba."""
        return "Testing (imagen estática)"
    
    def get_option_key(self) -> str:
        """Devuelve la clave de opción para pruebas."""
        return "0"


class RTSPSource(VideoSource):
    """Fuente de video RTSP para transmisión en tiempo real."""
    
    def get_source_url(self, config: Dict[str, Any]) -> str:
        """Construye y devuelve la URL RTSP."""
        return f"rtsp://{config['url_default']}:8080/h264.sdp"
    
    def get_description(self) -> str:
        """Devuelve la descripción de la fuente RTSP."""
        return "RTSP (cámara IP)"
    
    def get_option_key(self) -> str:
        """Devuelve la clave de opción para RTSP."""
        return "1"


class HTTPSource(VideoSource):
    """Fuente de video HTTP para captura de imágenes."""
    
    def get_source_url(self, config: Dict[str, Any]) -> str:
        """Construye y devuelve la URL HTTP."""
        return f"http://{config['url_default']}:8080/photo.jpg"
    
    def get_description(self) -> str:
        """Devuelve la descripción de la fuente HTTP."""
        return "HTTP (cámara IP)"
    
    def get_option_key(self) -> str:
        """Devuelve la clave de opción para HTTP."""
        return "2"


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
        return "3"


class VideoOptionController:
    """
    Controlador para la selección de fuentes de video.
    Permite agregar nuevas fuentes sin modificar el código existente.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Inicializa el controlador con las fuentes disponibles.
        
        Args:
            logger: Logger para registrar eventos
        """
        self.logger = logger
        self._sources: Dict[str, VideoSource] = {}
        
        # Registrar las fuentes por defecto
        self.register_source(TestingSource())
        self.register_source(RTSPSource())
        self.register_source(HTTPSource())
        self.register_source(WebcamSource())
    
    def register_source(self, source: VideoSource) -> None:
        """
        Registra una nueva fuente de video en el controlador.
        
        Args:
            source: Implementación de VideoSource a registrar
        """
        key = source.get_option_key()
        self._sources[key] = source
        if self.logger:
            self.logger.debug(f"Registrada fuente de video: {source.get_description()}")
    
    def get_available_sources(self) -> List[VideoSource]:
        """
        Obtiene una lista de todas las fuentes de video disponibles.
        
        Returns:
            Lista de fuentes de video registradas
        """
        return list(self._sources.values())
    
    def get_menu_options(self) -> List[str]:
        """
        Genera las opciones de menú para mostrar al usuario.
        
        Returns:
            Lista de strings con las opciones formateadas
        """
        options = []
        for source in self._sources.values():
            options.append(f"{source.get_option_key()} - {source.get_description()}")
        return options
    
    def get_source_url(self, option_key: str, config: Dict[str, Any]) -> Optional[Any]:
        """
        Obtiene la URL de la fuente de video seleccionada.
        
        Args:
            option_key: Clave de la opción seleccionada
            config: Configuración necesaria para construir la URL
            
        Returns:
            URL o identificador de la fuente, o None si la opción no existe
        """
        if option_key in self._sources:
            source = self._sources[option_key]
            if self.logger:
                self.logger.info(f"Seleccionada fuente de video: {source.get_description()}")
            return source.get_source_url(config)
        
        if self.logger:
            self.logger.error(f"Opción de video no válida: {option_key}")
        return None
