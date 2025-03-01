"""
Path: src/views/gui_view.py
Vista para manejar la interfaz gráfica de la aplicación.
Implementa la capa de presentación del patrón MVC.
"""

import tkinter as tk
import logging
from typing import Optional, Dict, Any
from src.video_stream import VideoStreamApp
from src.views.notifier import Notifier

# ...existing code...
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

class GUIView:
    """Clase responsable de la gestión de la interfaz gráfica."""

    def __init__(self, logger: logging.Logger):
        """
        Inicializa la vista gráfica.
        
        Args:
            logger: Logger configurado para registrar eventos
        """
        self.logger = logger
        self.root = None
        self.app = None
        self.thread = None
        self.is_running = False
        self.stats_label = None
        self.status_label = None
        self.update_interval = 500  # Actualizar estadísticas cada 500ms
        self.notifier = None

    def inicializar_ui(self, video_url, grados_rotacion, altura, horizontal, pixels_por_mm):
        """
        Inicializa la interfaz gráfica de la aplicación.
        
        Args:
            video_url: URL o índice de la fuente de video
            grados_rotacion: Grados de rotación para la imagen
            altura: Ajuste vertical para la imagen
            horizontal: Ajuste horizontal para la imagen
            pixels_por_mm: Relación de píxeles por milímetro
        """
        try:
            self.root = tk.Tk()
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

            # Crear frame para el video
            video_frame = tk.Frame(self.root)
            video_frame.pack(padx=10, pady=10)

            # Crear etiqueta para estadísticas
            self.stats_label = tk.Label(self.root, text="Iniciando procesamiento...",
                                       font=('Helvetica', 10))
            self.stats_label.pack(padx=5, pady=5)

            # Crear etiqueta para mostrar notificaciones de estado
            self.status_label = tk.Label(self.root, text="",
                                        font=('Helvetica', 11), fg="blue")
            self.status_label.pack(padx=5, pady=5)

            # Inicializar el notificador GUI con la etiqueta de estado
            self.notifier = GUINotifier(self.logger, self.status_label)

            self.app = VideoStreamApp(
                video_frame,  # Ahora pasamos el frame en lugar del root
                video_url,
                grados_rotacion,
                altura,
                horizontal,
                pixels_por_mm,
                self.logger,
                self.notifier  # Pasamos el notificador al VideoStreamApp
            )

            # Iniciar actualización periódica de estadísticas
            self.update_stats()

            self.logger.info("Interfaz gráfica inicializada correctamente.")
            self.notifier.notify_info("Interfaz gráfica iniciada")
        except (KeyError, AttributeError, TypeError) as e:
            self.logger.error(f"Error al inicializar la interfaz gráfica: {e}")
            raise

    def ejecutar(self):
        """Inicia el bucle principal de la interfaz gráfica de manera no bloqueante."""
        if self.app is not None:
            try:
                self.logger.info("Iniciando interfaz gráfica.")
                self.is_running = True
                # Iniciamos mainloop en el hilo principal
                self.root.mainloop()
                self.logger.info("Interfaz gráfica finalizada.")
            except (KeyError, AttributeError, TypeError) as e:
                self.logger.error(f"Error durante la ejecución de la interfaz gráfica: {e}")
                self.is_running = False
                raise
        else:
            self.logger.error("No se puede ejecutar la interfaz gráfica sin inicializar.")
            raise RuntimeError("La interfaz gráfica no está inicializada.")

    def on_closing(self):
        """Maneja el evento de cierre de la ventana"""
        self.logger.info("Cerrando la interfaz gráfica...")
        self.is_running = False

        # Detenemos el streaming de video
        if self.app:
            self.app.stop()

        # Destruimos la ventana
        if self.root:
            self.root.destroy()

    def update_stats(self):
        """Actualiza las estadísticas de procesamiento en la UI"""
        if self.is_running and self.app:
            try:
                stats = self.app.get_processing_stats()
                stats_text = (f"Frames procesados: {stats['frames_processed']} | "
                             f"FPS actual: {stats['fps_current']} | "
                             f"FPS promedio: {stats['fps_average']} | "
                             f"Tiempo: {stats['processing_time']}s")
                self.stats_label.config(text=stats_text)
            except (KeyError, AttributeError, TypeError) as e:
                self.logger.error(f"Error al actualizar estadísticas: {e}")

        # Programar próxima actualización si aún está en ejecución
        if self.is_running:
            self.root.after(self.update_interval, self.update_stats)
