"""
Path: src/views/notifier.py
Define la interfaz abstracta para sistemas de notificación.
Permite desacoplar la lógica de notificación de la lógica de negocio.

Estrategia de Notificaciones:
----------------------------
Este módulo implementa una clara separación de responsabilidades:
1. Logging: Para registro permanente de eventos y depuración (archivo/consola)
2. Notificaciones: Para presentar información al usuario final (UI/consola)

Esta separación permite:
- Personalizar la experiencia del usuario sin afectar el registro técnico
- Mantener registros detallados para depuración sin saturar al usuario
- Implementar múltiples canales de notificación (GUI, correo, SMS, etc.)
  manteniendo una única fuente de verdad para el registro de eventos
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class Notifier(ABC):
    """
    Interfaz abstracta para sistemas de notificación.
    Define métodos comunes que deben implementar todos los notificadores.
    
    Nota sobre Logging vs. Notificaciones:
    Los notificadores NO reemplazan el sistema de logging. Mientras que el logging
    se enfoca en registrar información técnica para desarrollo/depuración,
    los notificadores se enfocan en presentar información significativa al usuario final.
    Los notificadores pueden utilizar el sistema de logging como un canal adicional
    para registrar las notificaciones emitidas.
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
            
        Nota: Este método debe generar una notificación para el usuario final,
        y opcionalmente registrar el evento en el sistema de logging.
        """

    @abstractmethod
    def notify_error(self, message: str, error: Optional[Exception] = None) -> None:
        """
        Notifica sobre un error ocurrido.
        
        Args:
            message: Mensaje descriptivo del error
            error: Excepción asociada al error (opcional)
            
        Nota: Los errores críticos siempre deberían registrarse en el sistema de logging,
        independientemente de si se notifican al usuario o no.
        """

    @abstractmethod
    def notify_info(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Notifica información general.

        Args:
            message: Mensaje informativo
            data: Datos adicionales asociados a la notificación (opcional)

        Nota: La información contextual o de menor relevancia puede registrarse
        solo en el sistema de logging y no necesariamente notificarse al usuario.
        """



class ConsoleNotifier(Notifier):
    """
    Implementación básica de Notifier que muestra las notificaciones en la consola.
    Esta clase ejemplifica la distinción entre logging y notificaciones:
    - Muestra mensajes en la consola (notificación al usuario)
    - Opcionalmente registra los mismos mensajes en el sistema de logging (registro técnico)
    """

    def __init__(self, logger=None):
        """
        Inicializa el notificador de consola.

        Args:
            logger: Objeto logger opcional para registrar las notificaciones.
                   Si se proporciona, cada notificación también se registrará
                   con el nivel de log apropiado.
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
