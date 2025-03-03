"""
Path: src/views/common/gui_notifier.py
Clase para manejar notificaciones en la interfaz gráfica.
"""

import logging
import tkinter as tk
import time
from enum import Enum, auto
from typing import Optional

class NotificationType(Enum):
    """Tipos de notificaciones para la interfaz gráfica."""
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    SUCCESS = auto()

class GUINotifier:
    """Clase para mostrar notificaciones en la interfaz gráfica."""

    def __init__(self, logger: logging.Logger, status_label: Optional[tk.Label] = None):
        """
        Inicializa el notificador de la GUI.
        
        Args:
            logger: Logger para registrar los mensajes
            status_label: Etiqueta donde mostrar los mensajes (opcional)
        """
        self.logger = logger
        self.status_label = status_label

        # Colores para diferentes tipos de notificaciones
        self.colors = {
            NotificationType.INFO: "blue",
            NotificationType.WARNING: "orange",
            NotificationType.ERROR: "red",
            NotificationType.SUCCESS: "green"
        }

        # Control de notificaciones duplicadas mejorado
        self.last_notifications = {}
        self.notification_threshold = 2.5  # segundos para evitar duplicados

        # Configuración del umbral de duplicación (usado en notify_desvio)
        self.desvio_notification_threshold = 2.5  # segundos entre notificaciones similares

    def set_status_label(self, status_label: tk.Label) -> None:
        """
        Establece la etiqueta donde se mostrarán los mensajes.
        
        Args:
            status_label: Etiqueta de Tkinter para mostrar mensajes
        """
        self.status_label = status_label
        self.logger.debug("Etiqueta de estado configurada en el notificador")

    def set_desvio_threshold(self, seconds: float) -> None:
        """
        Configura el umbral de tiempo para considerar notificaciones de desvío como duplicadas.
        
        Args:
            seconds: Tiempo en segundos entre notificaciones similares
        """
        self.desvio_notification_threshold = seconds
        self.logger.debug(f"Umbral de notificación de desvío configurado a {seconds} segundos")

    def notify(
        self,
        message: str,
        notification_type: NotificationType = NotificationType.INFO
    ) -> None:
        """
        Muestra una notificación en la interfaz gráfica y registra el mensaje.
        
        Args:
            message: Mensaje a mostrar
            notification_type: Tipo de notificación (determina color y nivel de log)
        """
        # Registrar en el log según el tipo
        if notification_type == NotificationType.ERROR:
            self.logger.error(message)
        elif notification_type == NotificationType.WARNING:
            self.logger.warning(message)
        elif notification_type == NotificationType.SUCCESS:
            self.logger.info(f"[SUCCESS] {message}")
        else:  # INFO
            self.logger.info(message)

        # Actualizar la etiqueta de estado si existe
        if self.status_label:
            try:
                color = self.colors.get(notification_type, "black")
                self.status_label.config(text=message, fg=color)
            except Exception as e:  # pylint: disable=broad-exception-caught
                self.logger.error(f"Error al actualizar la etiqueta de estado: {e}")

    def notify_info(self, message: str) -> None:
        """Muestra una notificación informativa."""
        self.notify(message, NotificationType.INFO)

    def notify_warning(self, message: str) -> None:
        """Muestra una notificación de advertencia."""
        self.notify(message, NotificationType.WARNING)

    def notify_error(self, message: str, context: str = None) -> None:
        """
        Muestra una notificación de error.
        
        Args:
            message: Mensaje de error
            context: Contexto adicional del error (opcional)
        """
        # Si se proporciona contexto, añadirlo al mensaje
        if context:
            full_message = f"{message} [{context}]"
        else:
            full_message = message

        self.notify(full_message, NotificationType.ERROR)

    def notify_success(self, message: str) -> None:
        """Muestra una notificación de éxito."""
        self.notify(message, NotificationType.SUCCESS)

    def notify_desvio(self, message: str, contexto: str = None) -> None:
        """
        Muestra una notificación de desviación (caso especial para procesamiento visual).
        Evita mostrar notificaciones duplicadas en un corto periodo de tiempo.
        
        Args:
            message: Mensaje sobre la desviación detectada
            contexto: Información adicional sobre la desviación (opcional)
        """
        # Preparar el mensaje completo
        if contexto:
            full_message = f"{message} [{contexto}]"
        else:
            full_message = message

        # Generar una clave única para esta combinación de mensaje y contexto
        notification_key = f"desvio:{message}|{contexto}"
        current_time = time.time()

        # Verificar si esta notificación ya se mostró recientemente
        if notification_key in self.last_notifications:
            last_time = self.last_notifications[notification_key]
            if (current_time - last_time) < self.desvio_notification_threshold:
                # Si se mostró recientemente, no mostrar de nuevo
                return

        # Actualizar registro de última notificación
        self.last_notifications[notification_key] = current_time

        # Limpiar notificaciones antiguas (más de 10 segundos)
        self._clean_old_notifications(current_time, 10)

        # Actualizar la UI con el mensaje, sin generar un segundo log
        if self.status_label:
            try:
                self.status_label.config(
                    text=full_message,
                    fg=self.colors[NotificationType.WARNING]
                )
            except Exception as e:  # pylint: disable=broad-exception-caught
                self.logger.error(f"Error al actualizar etiqueta de estado: {e}")

    def _clean_old_notifications(self, current_time: float, max_age: float) -> None:
        """
        Limpia las notificaciones antiguas del registro.
        
        Args:
            current_time: Tiempo actual en segundos
            max_age: Edad máxima de notificación en segundos
        """
        keys_to_remove = []

        for key, timestamp in self.last_notifications.items():
            if (current_time - timestamp) > max_age:
                keys_to_remove.append(key)

        # Eliminar las notificaciones antiguas
        for key in keys_to_remove:
            del self.last_notifications[key]
