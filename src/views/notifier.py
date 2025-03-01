"""
Path: src/views/notifier.py
Define la interfaz abstracta para sistemas de notificación.
Permite desacoplar la lógica de notificación de la lógica de negocio.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class Notifier(ABC):
    """
    Interfaz abstracta para sistemas de notificación.
    Define métodos comunes que deben implementar todos los notificadores.
    """

    @abstractmethod
    def notify_desvio(self, desvio_mm: float, tolerancia: float) -> str:
        """
        Notifica sobre un desvío detectado y genera un mensaje descriptivo.
        
        Args:
            desvio_mm: Valor del desvío en milímetros
            tolerancia: Valor de tolerancia para determinar si el desvío es significativo
            
        Returns:
            Mensaje descriptivo del desvío
        """
        pass
    
    @abstractmethod
    def notify_error(self, message: str, error: Optional[Exception] = None) -> None:
        """
        Notifica sobre un error ocurrido.
        
        Args:
            message: Mensaje descriptivo del error
            error: Excepción asociada al error (opcional)
        """
        pass
    
    @abstractmethod
    def notify_info(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Notifica información general.
        
        Args:
            message: Mensaje informativo
            data: Datos adicionales asociados a la notificación (opcional)
        """
        pass


class ConsoleNotifier(Notifier):
    """
    Implementación básica de Notifier que muestra las notificaciones en la consola.
    """
    
    def __init__(self, logger=None):
        """
        Inicializa el notificador de consola.
        
        Args:
            logger: Objeto logger opcional para registrar las notificaciones
        """
        self.logger = logger
    
    def notify_desvio(self, desvio_mm: float, tolerancia: float) -> str:
        """
        Genera y muestra una notificación sobre un desvío detectado.
        
        Args:
            desvio_mm: Valor del desvío en milímetros
            tolerancia: Valor de tolerancia para determinar si el desvío es significativo
            
        Returns:
            Mensaje descriptivo del desvío
        """
        if desvio_mm > tolerancia:
            mensaje = f"Desvio: {desvio_mm} mm ENG"
        elif desvio_mm < -tolerancia:
            mensaje = f"Desvio: {desvio_mm} mm OP"
        else:
            if desvio_mm > 0:
                mensaje = f"Desvio: {desvio_mm} mm - Centrado ENG"
            elif desvio_mm < 0:
                mensaje = f"Desvio: {desvio_mm} mm - Centrado OP"
            else:
                mensaje = f"Desvio: {desvio_mm} mm - Centrado"
                
        print(mensaje)
        if self.logger:
            self.logger.info(mensaje)
        
        return mensaje
    
    def notify_error(self, message: str, error: Optional[Exception] = None) -> None:
        """
        Muestra una notificación de error.
        
        Args:
            message: Mensaje descriptivo del error
            error: Excepción asociada al error (opcional)
        """
        error_msg = f"ERROR: {message}"
        if error:
            error_msg += f" - {str(error)}"
            
        print(error_msg)
        if self.logger:
            self.logger.error(error_msg)
    
    def notify_info(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Muestra una notificación informativa.
        
        Args:
            message: Mensaje informativo
            data: Datos adicionales asociados a la notificación (opcional)
        """
        info_msg = f"INFO: {message}"
        if data:
            info_msg += f" - {data}"
            
        print(info_msg)
        if self.logger:
            self.logger.info(info_msg)
