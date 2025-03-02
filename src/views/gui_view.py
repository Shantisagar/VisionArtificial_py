"""
Path: src/views/gui_view.py
Vista para manejar la interfaz gráfica de la aplicación.
Implementa la capa de presentación del patrón MVC.
"""

import tkinter as tk
import logging
from typing import Dict, Callable
from src.views.gui_notifier import GUINotifier
from src.views.main_display_view import MainDisplayView
from src.views.control_panel_view import ControlPanelView

class GUIView:
    """Clase responsable de la coordinación de componentes de la interfaz gráfica."""

    def __init__(self, logger: logging.Logger):
        """
        Inicializa la vista gráfica.
        
        Args:
            logger: Logger configurado para registrar eventos
        """
        self.logger = logger
        self.root = None
        self.is_running = False
        self.update_interval = 500  # Actualizar estadísticas cada 500ms

        # Componente para notificaciones compartido entre vistas
        self.notifier = GUINotifier(logger)

        # Vistas específicas
        self.main_display = None
        self.control_panel = None

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
        if self.control_panel:
            self.control_panel.set_parameters_update_callback(callback)

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

            # Inicializar el notificador de la GUI sin etiqueta por ahora
            self.notifier = GUINotifier(self.logger)

            # Inicializar el panel de control primero para obtener la etiqueta de estado
            self.control_panel = ControlPanelView(self.logger, control_column)
            self.control_panel.set_notifier(self.notifier)
            self.control_panel.initialize(None, grados_rotacion, pixels_por_mm, altura, horizontal)

            # Inicializar la vista de visualización principal
            self.main_display = MainDisplayView(self.logger, video_column)
            self.main_display.set_notifier(self.notifier)
            self.main_display.set_on_closing_callback(self.on_closing)
            self.main_display.initialize(
                video_url, grados_rotacion, altura, horizontal, pixels_por_mm
            )

            # Si tenemos un callback de actualización de parámetros, configurarlo
            if self.on_parameters_update:
                self.control_panel.set_parameters_update_callback(self.on_parameters_update)

            # Iniciar actualización periódica de estadísticas
            self.update_stats()

            # Programar maximización de la ventana después de 2 segundos
            self.root.after(2000, self.maximizar_ventana)

            self.logger.info("Interfaz gráfica inicializada correctamente.")
            self.notifier.notify_info("Interfaz gráfica iniciada")
        except (tk.TclError, AttributeError) as e:
            self.logger.error(f"Error al inicializar la interfaz gráfica: {e}")
            raise

    def maximizar_ventana(self):
        """Maximiza la ventana principal."""
        self.root.state('zoomed')

    def ejecutar(self):
        """Inicia el bucle principal de la interfaz gráfica de manera no bloqueante."""
        if self.main_display:
            try:
                self.logger.info("Iniciando interfaz gráfica.")
                self.is_running = True
                # Iniciamos mainloop en el hilo principal
                self.root.mainloop()
                self.logger.info("Interfaz gráfica finalizada.")
            except (tk.TclError, RuntimeError) as e:
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

        # Detenemos el componente de visualización
        if self.main_display:
            self.main_display.stop()

        # Destruimos la ventana
        if self.root:
            self.root.destroy()

    def update_stats(self):
        """Actualiza las estadísticas de procesamiento en la UI"""
        if self.is_running and self.main_display and self.control_panel:
            try:
                stats = self.main_display.get_processing_stats()
                self.control_panel.update_stats(stats)
            except Exception as e:  # pylint: disable=broad-exception-caught
                self.logger.error(f"Error al actualizar estadísticas: {e}")
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
        if self.control_panel:
            self.control_panel.update_parameters(parameters)

        # Si el procesamiento de video está activo, actualizarlo también
        if self.main_display:
            self.main_display.update_parameters(parameters)
            self.logger.info(f"Parámetros enviados a la vista de visualización: {parameters}")
            self.notifier.notify_info("Parámetros aplicados al procesamiento de video")
        else:
            self.logger.warning(
                "No se pudo actualizar la vista de visualización - no está inicializada"
            )
