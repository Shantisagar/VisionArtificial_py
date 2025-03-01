"""
Path: src/views/gui_view.py
Vista para manejar la interfaz gráfica de la aplicación.
Implementa la capa de presentación del patrón MVC.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Callable
from src.video_stream import VideoStreamApp
from src.views.tool_tip import ToolTip
from src.views.gui_notifier import GUINotifier
from src.views.gui_parameter_panel import GUIParameterPanel

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
        
        # Nuevo: referencia al panel de parámetros
        self.parameter_panel = None

        # Callback para cuando se actualicen los parámetros
        self.on_parameters_update = None

        # Lista para almacenar referencias a tooltips
        self.tooltips = []

    def set_parameters_update_callback(self, callback: Callable[[Dict[str, float]], None]) -> None:
        """
        Establece el callback que se llamará cuando los parámetros se actualicen desde la GUI.
        
        Args:
            callback: Función a llamar con los nuevos parámetros
        """
        self.on_parameters_update = callback
        # Si el panel de parámetros ya está creado, pasarle el callback
        if self.parameter_panel:
            self.parameter_panel.set_parameters_update_callback(callback)

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
            self.root.title("Control de Visión Artificial")
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

            # Crear una ventana de tamaño adecuado
            window_width = 1000
            window_height = 800
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x_position = (screen_width - window_width) // 2
            y_position = (screen_height - window_height) // 2
            self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

            # Crear frame principal con dos columnas
            main_frame = tk.Frame(self.root)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Columna izquierda para el video
            video_column = tk.Frame(main_frame)
            video_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Columna derecha para controles
            control_column = tk.Frame(main_frame)
            control_column.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

            # Frame para el video
            video_frame = tk.LabelFrame(video_column, text="Vista de cámara")
            video_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Crear etiqueta para mostrar notificaciones de estado
            status_frame = tk.LabelFrame(control_column, text="Estado")
            status_frame.pack(fill="x", padx=5, pady=5)

            self.status_label = tk.Label(status_frame, text="",
                                        font=('Helvetica', 11), fg="blue", wraplength=250)
            self.status_label.pack(padx=5, pady=5, fill="x")

            # Inicializar el notificador GUI con la etiqueta de estado
            self.notifier = GUINotifier(self.logger, self.status_label)

            # Crear panel de control para los parámetros
            control_frame = tk.LabelFrame(control_column, text="Parámetros de configuración")
            control_frame.pack(fill="x", padx=5, pady=5)

            # Inicializar correctamente el panel de parámetros
            self.parameter_panel = GUIParameterPanel(control_frame, self.logger)
            self.parameter_panel.set_notifier(self.notifier)
            self.parameter_panel.initialize(grados_rotacion, pixels_por_mm, altura, horizontal)
            
            # Establecer el callback para actualizaciones de parámetros
            if self.on_parameters_update:
                self.parameter_panel.set_parameters_update_callback(self.on_parameters_update)

            # Crear etiqueta para estadísticas
            stats_frame = tk.LabelFrame(control_column, text="Estadísticas")
            stats_frame.pack(fill="x", padx=5, pady=5)

            self.stats_label = tk.Label(stats_frame, text="Iniciando procesamiento...",
                                       font=('Helvetica', 10))
            self.stats_label.pack(padx=5, pady=5)

            self.app = VideoStreamApp(
                video_frame,
                video_url,
                grados_rotacion,
                altura,
                horizontal,
                pixels_por_mm,
                self.logger,
                self.notifier
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

    def update_parameters(self, parameters: Dict[str, float]) -> None:
        """
        Actualiza los valores de los parámetros en la interfaz y en el procesamiento.
        
        Args:
            parameters: Diccionario con los nuevos valores
        """
        self.logger.info(f"Actualizando parámetros en GUI: {parameters}")
        
        # Actualizar los controles de la UI a través del panel de parámetros
        if self.parameter_panel:
            self.parameter_panel.update_parameters(parameters)
            
        # Si el procesamiento de video está activo, actualizarlo también
        if self.app:
            # Esta es la línea clave - asegurarse de que los parámetros llegan a la app de video
            self.app.update_parameters(parameters)
            self.logger.info(f"Parámetros enviados a VideoStreamApp: {parameters}")
            self.notifier.notify_info("Parámetros aplicados al procesamiento de video")
        else:
            self.logger.warning("No se pudo actualizar VideoStreamApp - no está inicializado")
