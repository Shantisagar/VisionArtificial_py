"""
Path: src/utils/event_system.py
Sistema de eventos para comunicación desacoplada entre componentes.
Implementa un patrón observador simple pero efectivo.
"""

import logging
from typing import Dict, Callable, List, Any, Optional
from enum import Enum, auto

class EventType(Enum):
    """Tipos de eventos del sistema"""
    PARAMETER_UPDATE = auto()
    PROCESSING_STATS = auto()
    VIDEO_FRAME = auto()
    NOTIFICATION = auto()
    APPLICATION_STATUS = auto()
    # Añadir más tipos de eventos según sea necesario

class EventSystem:
    """
    Sistema de eventos para permitir comunicación desacoplada entre componentes.
    Implementa un patrón observador (publish/subscribe).
    """
    
    def __init__(self, logger: logging.Logger):
        """
        Inicializa el sistema de eventos.
        
        Args:
            logger: Logger configurado para registrar eventos
        """
        self.logger = logger
        self.subscribers: Dict[EventType, List[Callable]] = {}
        for event_type in EventType:
            self.subscribers[event_type] = []
        
        self.logger.debug("Sistema de eventos inicializado")
    
    def subscribe(self, event_type: EventType, callback: Callable) -> None:
        """
        Suscribe un callback a un tipo de evento.
        
        Args:
            event_type: Tipo de evento al que suscribirse
            callback: Función a llamar cuando ocurra el evento
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        if callback not in self.subscribers[event_type]:
            self.subscribers[event_type].append(callback)
            self.logger.debug(f"Suscrito a evento {event_type.name}")
        else:
            self.logger.warning(f"Callback ya suscrito a evento {event_type.name}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable) -> None:
        """
        Cancela la suscripción de un callback a un tipo de evento.
        
        Args:
            event_type: Tipo de evento del que desuscribirse
            callback: Función a eliminar de las suscripciones
        """
        if event_type in self.subscribers and callback in self.subscribers[event_type]:
            self.subscribers[event_type].remove(callback)
            self.logger.debug(f"Desuscrito de evento {event_type.name}")
    
    def publish(self, event_type: EventType, data: Optional[Any] = None) -> None:
        """
        Publica un evento para que sea recibido por todos los suscriptores.
        
        Args:
            event_type: Tipo de evento a publicar
            data: Datos asociados al evento (opcional)
        """
        if event_type not in self.subscribers:
            self.logger.warning(f"Intento de publicar un evento de tipo desconocido: {event_type}")
            return
        
        self.logger.debug(f"Publicando evento {event_type.name} con datos: {data}")
        for callback in self.subscribers[event_type]:
            try:
                if data is not None:
                    callback(data)
                else:
                    callback()
            except Exception as e:
                self.logger.error(f"Error en callback de evento {event_type.name}: {e}")
