"""
Path: src/views/display/main_display_view.py
Vista para manejar la pantalla principal y visualización de video.
Parte de la separación de responsabilidades del patrón MVC.
"""

# pylint: disable=too-many-instance-attributes, too-many-arguments, too-many-positional-arguments

import tkinter as tk
import logging
from src.controllers.video_stream_controller import VideoStreamController
from src.views.common.gui_notifier import GUINotifier
from src.views.common.interface_view_helpers import get_centered_geometry
from src.views.common.gui import create_main_window

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
        self.controller = None  # Ahora usamos el controlador
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

                # Usar helper para centrar la ventana
                self.root.geometry(get_centered_geometry(self.root, 1000, 800))

                self.main_frame = tk.Frame(self.root)
                self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            else:
                # Si tenemos un widget padre, usamos ese en lugar de crear una nueva ventana
                self.main_frame = tk.Frame(self.parent)
                self.main_frame.grid(row=0, column=0, sticky='nsew')
                
                # Configurar el grid para expansión
                self.parent.grid_rowconfigure(0, weight=1)
                self.parent.grid_columnconfigure(0, weight=1)

            # Frame para el video (sin título y con fondo negro)
            self.video_frame = tk.Frame(self.main_frame, bg='black')
            self.video_frame.grid(row=0, column=0, sticky='nsew')
            
            # Configurar el grid del main_frame
            self.main_frame.grid_rowconfigure(0, weight=1)
            self.main_frame.grid_columnconfigure(0, weight=1)

            # Inicializar el controlador
            self.controller = VideoStreamController(self.logger, self.notifier)
            
            # Inicializar y arrancar el controlador
            if not self.controller.initialize(
                self.video_frame,
                video_url,
                grados_rotacion,
                altura,
                horizontal,
                pixels_por_mm
            ):
                raise RuntimeError("No se pudo inicializar el controlador de video")

            if not self.controller.start():
                raise RuntimeError("No se pudo iniciar el controlador de video")

            self.is_running = True
            self.logger.info("Vista de visualización inicializada correctamente")
            if self.notifier:
                self.notifier.notify_info("Visualización de cámara iniciada")

        except Exception as e:
            self.logger.error(f"Error al inicializar vista: {str(e)}")
            raise

    def on_closing(self):
        """Maneja el evento de cierre de la ventana"""
        self.logger.info("Cerrando la vista de visualización...")
        self.is_running = False

        if self.controller:
            self.controller.stop()

        if self.on_closing_callback:
            self.on_closing_callback()

        # Destruimos la ventana solo si la creamos nosotros
        if self.root and self.parent is None:
            self.root.destroy()

    def start(self):
        """Inicia la visualización de video."""
        if self.controller:
            self.controller.start()
            self.is_running = True
            self.logger.info("Visualización de video iniciada.")
        else:
            self.logger.error("No se puede iniciar la visualización sin inicializar.")
            raise RuntimeError("La visualización no está inicializada.")

    def stop(self):
        """Detiene la visualización de video."""
        if self.controller:
            self.controller.stop()
            self.is_running = False
            self.logger.info("Visualización de video detenida.")

    def update_parameters(self, parameters):
        """
        Actualiza los parámetros de procesamiento de imagen.
        
        Args:
            parameters: Diccionario con los nuevos valores de parámetros
        """
        if not self.controller:
            self.logger.warning(
                "No se pueden actualizar parámetros: controlador no inicializado"
            )
            return

        self.logger.debug(f"Actualizando parámetros en MainDisplayView: {parameters}")

        try:
            # Delegamos la actualización de parámetros al controlador
            self.controller.update_parameters(parameters)

            # Registrar los parámetros actualizados
            param_names = ', '.join(parameters.keys())
            self.logger.info(f"Parámetros actualizados en el controlador: {param_names}")

            if self.notifier:
                self.notifier.notify_info("Parámetros aplicados al procesamiento")
        except Exception as e:
            self.logger.error(f"Error al actualizar parámetros: {str(e)}")

    def get_processing_stats(self):
        """
        Obtiene estadísticas del procesamiento de video.
        
        Returns:
            Dict con estadísticas de procesamiento
        """
        return self.controller.get_processing_stats() if self.controller else {}

    def run_main_loop(self):
        """Ejecuta el bucle principal de la interfaz gráfica si es una ventana independiente."""
        if self.root and self.parent is None:
            self.is_running = True
            self.root.mainloop()
