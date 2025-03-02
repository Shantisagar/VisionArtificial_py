"""
Path: src/views/main_display_view.py
Vista para manejar la pantalla principal y visualización de video.
Parte de la separación de responsabilidades del patrón MVC.
"""

# pylint: disable=too-many-instance-attributes, too-many-arguments, too-many-positional-arguments

import tkinter as tk
import logging
from src.video_stream import VideoStreamApp
from src.views.gui_notifier import GUINotifier
from src.views.common_gui import create_main_window

class MainDisplayView:
    """Clase responsable de la gestión de la ventana principal y visualización de video."""

    def __init__(self, logger: logging.Logger, parent=None):
        """
        Inicializa la vista de visualización principal.
        
        Args:
            logger: Logger configurado para registrar eventos
            parent: Widget padre (opcional, si se integra en otra ventana)
        """
        self.logger = logger
        self.parent = parent
        self.root = None
        self.main_frame = None
        self.video_frame = None
        self.app = None
        self.is_running = False
        self.on_closing_callback = None

        # Referencia a la clase notificadora
        self.notifier = None

    def set_notifier(self, notifier: GUINotifier) -> None:
        """
        Establece el notificador para esta vista.
        
        Args:
            notifier: Instancia de GUINotifier
        """
        self.notifier = notifier

    def set_on_closing_callback(self, callback):
        """
        Establece el callback que se llamará cuando se cierre la ventana.
        
        Args:
            callback: Función sin argumentos a llamar al cerrar
        """
        self.on_closing_callback = callback

    def initialize(self, video_url, grados_rotacion, altura, horizontal, pixels_por_mm):
        """
        Inicializa la interfaz de visualización de video.
        
        Args:
            video_url: URL o índice de la fuente de video
            grados_rotacion: Grados de rotación para la imagen
            altura: Ajuste vertical para la imagen
            horizontal: Ajuste horizontal para la imagen
            pixels_por_mm: Relación de píxeles por milímetro
        """
        try:
            # Si no tenemos un widget padre, creamos nuestra propia ventana
            if self.parent is None:
                self.root = create_main_window(self.on_closing)

                # Crear una ventana de tamaño adecuado
                window_width = 1000
                window_height = 800
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                x_position = (screen_width - window_width) // 2
                y_position = (screen_height - window_height) // 2
                self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

                self.main_frame = tk.Frame(self.root)
                self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            else:
                # Si tenemos un widget padre, usamos ese en lugar de crear una nueva ventana
                self.main_frame = tk.Frame(self.parent)
                self.main_frame.pack(fill=tk.BOTH, expand=True)

            # Frame para el video
            self.video_frame = tk.LabelFrame(self.main_frame, text="Vista de cámara")
            self.video_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Inicializar la aplicación de streaming de video
            self.app = VideoStreamApp(
                self.video_frame,
                video_url,
                grados_rotacion,
                altura,
                horizontal,
                pixels_por_mm,
                self.logger,
                self.notifier
            )

            self.logger.info("Interfaz de visualización inicializada correctamente.")
            if self.notifier:
                self.notifier.notify_info("Visualización de cámara iniciada")
        except Exception as e:
            self.logger.error(f"Error al inicializar la interfaz de visualización: {str(e)}")
            raise

    def on_closing(self):
        """Maneja el evento de cierre de la ventana"""
        self.logger.info("Cerrando la vista de visualización...")
        self.is_running = False

        # Detenemos el streaming de video
        if self.app:
            self.app.stop()

        # Si tenemos un callback de cierre, lo llamamos
        if self.on_closing_callback:
            self.on_closing_callback()

        # Destruimos la ventana solo si la creamos nosotros
        if self.root and self.parent is None:
            self.root.destroy()

    def start(self):
        """Inicia la visualización de video."""
        if self.app:
            self.app.start()
            self.is_running = True
            self.logger.info("Visualización de video iniciada.")
        else:
            self.logger.error("No se puede iniciar la visualización sin inicializar.")
            raise RuntimeError("La visualización no está inicializada.")

    def stop(self):
        """Detiene la visualización de video."""
        if self.app:
            self.app.stop()
            self.is_running = False
            self.logger.info("Visualización de video detenida.")

    def update_parameters(self, parameters):
        """
        Actualiza los parámetros de procesamiento de video.
        
        Args:
            parameters: Diccionario con los parámetros a actualizar
        """
        if self.app:
            self.app.update_parameters(parameters)
            self.logger.info(f"Parámetros de visualización actualizados: {parameters}")

    def get_processing_stats(self):
        """
        Obtiene estadísticas del procesamiento de video.
        
        Returns:
            Dict con estadísticas de procesamiento
        """
        if self.app:
            return self.app.get_processing_stats()
        return {}

    def run_main_loop(self):
        """Ejecuta el bucle principal de la interfaz gráfica si es una ventana independiente."""
        if self.root and self.parent is None:
            self.is_running = True
            self.root.mainloop()
