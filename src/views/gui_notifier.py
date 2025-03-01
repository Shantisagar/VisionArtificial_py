"""
Path: src/views/gui_notifier.py
Este módulo implementa un notificador para la interfaz gráfica.
"""

from typing import Optional, Dict, Any
from src.views.notifier import Notifier

class GUINotifier(Notifier):
    """Implementación del notificador para la interfaz gráfica."""

    def __init__(self, logger, status_label=None):
        """
        Inicializa el notificador GUI.
        
        Args:
            logger: Logger configurado para registrar eventos
            status_label: Label de Tkinter donde se mostrarán las notificaciones (opcional)
        """
        self.logger = logger
        self.status_label = status_label
        self.notifications = []  # Almacena las últimas notificaciones

    def notify_desvio(self, desvio_mm: float, tolerancia: float) -> str:
        """
        Genera una notificación sobre un desvío detectado.
        
        Args:
            desvio_mm: Valor del desvío en milímetros
            tolerancia: Valor de tolerancia para determinar si el desvío es significativo
            
        Returns:
            Mensaje descriptivo del desvío
        """
        if desvio_mm > tolerancia:
            mensaje = f"Desvío a la derecha: {desvio_mm} mm"
        elif desvio_mm < -tolerancia:
            mensaje = f"Desvío a la izquierda: {desvio_mm} mm"
        else:
            mensaje = f"Desvío dentro de la tolerancia: {desvio_mm} mm"

        # Se elimina el log que mostraba "Desvío registrado" en la consola.
        # En su lugar, si hay un label definido en la UI, se actualiza el texto:
        if self.status_label:
            self.status_label.config(text=mensaje)

        # Almacenar la notificación para posible consulta posterior
        self.notifications.append(mensaje)
        if len(self.notifications) > 10:
            self.notifications.pop(0)

        return mensaje

    def notify_error(self, message: str, error: Optional[Exception] = None) -> None:
        """
        Muestra una notificación de error en la UI.
        
        Args:
            message: Mensaje descriptivo del error
            error: Excepción asociada al error (opcional)
        """
        error_msg = f"ERROR: {message}"
        if error:
            error_msg += f" - {str(error)}"

        self.logger.error(error_msg)

        if self.status_label:
            self.status_label.config(text=error_msg, fg="red")

    def notify_info(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Muestra una notificación informativa en la UI.
        
        Args:
            message: Mensaje informativo
            data: Datos adicionales asociados a la notificación (opcional)
        """
        info_msg = f"INFO: {message}"

        self.logger.info(info_msg)

        if self.status_label:
            self.status_label.config(text=info_msg, fg="blue")
