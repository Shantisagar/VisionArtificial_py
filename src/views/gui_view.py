"""
Path: src/views/gui_view.py
Vista para manejar la interfaz gráfica de la aplicación.
Implementa la capa de presentación del patrón MVC.
"""

import tkinter as tk
import logging
from typing import Dict, Callable
from src.views.common.gui_notifier import GUINotifier
from src.views.gui.control_panel_view import ControlPanelView
from src.views.gui.main_display_view import MainDisplayView
from src.views.common.interface_view_helpers import get_centered_geometry
from src.config.constants import (
    DEFAULT_WINDOW_WIDTH,
    DEFAULT_WINDOW_HEIGHT,
    WINDOW_STATE_MAXIMIZED,
    WINDOW_MAXIMIZE_DELAY_MS
)

class GUIView:
    """Clase responsable de la presentación de la interfaz gráfica."""

    def __init__(self, logger: logging.Logger):
        """
        Inicializa la vista gráfica.
        
        Args:
            logger: Logger configurado para registrar eventos.
        """
        self.logger = logger
        self.logger.debug("Inicializando GUIView")
        self.root = None
        self.is_running = False

        # Componente para notificaciones
        self.logger.debug("Creando instancia de GUINotifier")
        self.notifier = GUINotifier(logger)

        # Vistas específicas
        self.main_display = None
        self.control_panel = None

        # Callback para actualización de parámetros (delegado al controlador)
        self.on_parameters_update = None

        # Parámetros iniciales
        self.initial_params = {}
        self.logger.debug("GUIView inicializado")

    def set_parameters_update_callback(self, callback: Callable[[Dict[str, float]], None]) -> None:
        """
        Establece el callback que se llamará cuando se actualicen los parámetros.

        Args:
            callback (Callable): Función a llamar con los nuevos parámetros.
        """
        if not callable(callback):
            self.logger.error(f"El callback proporcionado no es callable: {type(callback)}")
            return
        callback_name = callback.__name__ if hasattr(callback, '__name__') else 'anónimo'
        self.logger.debug(f"Estableciendo callback de actualización de parámetros: {callback_name}")
        self.on_parameters_update = callback
        self._propagate_callback_to_control_panel(callback)

    def _propagate_callback_to_control_panel(self, callback: Callable) -> None:
        """
        Propaga el callback al panel de control si ya está inicializado.
        
        Args:
            callback: Callback a propagar.
        """
        if self.control_panel:
            self.logger.debug("Propagando callback al panel de control")
            try:
                self.control_panel.set_parameters_update_callback(callback)
                self.logger.debug("Callback propagado correctamente")
            except (AttributeError, TypeError) as e:
                self.logger.error(f"Error al propagar callback al panel de control: {e}")
        else:
            self.logger.debug(
                "Control panel no inicializado aún, se propagará durante la inicialización"
            )

    def inicializar_ui(self, video_url, grados_rotacion, altura, horizontal, pixels_por_mm):
        """
        Inicializa la interfaz gráfica de la aplicación.
        
        Args:
            video_url: URL o índice de la fuente de video.
            grados_rotacion: Grados de rotación para la imagen.
            altura: Ajuste vertical.
            horizontal: Ajuste horizontal.
            pixels_por_mm: Relación de píxeles por milímetro.
        """
        self.logger.debug(f"Inicializando UI: video={video_url}, rotación={grados_rotacion}, "
                          f"altura={altura}, horizontal={horizontal}, píxeles/mm={pixels_por_mm}")
        try:
            self._init_ui_with_params(video_url, grados_rotacion, altura, horizontal, pixels_por_mm)
            self.logger.info("Interfaz gráfica inicializada correctamente.")
            self.notifier.notify_info("Interfaz gráfica iniciada")
        except (tk.TclError, AttributeError) as e:
            self.logger.error(f"Error al inicializar la interfaz gráfica: {e}")
            raise

    def _init_ui_with_params(self, video_url, grados_rotacion, altura, horizontal, pixels_por_mm):
        """
        Configura todos los componentes de la interfaz con los parámetros proporcionados.
        """
        self._setup_main_window()
        _, video_column, control_column = self._create_layout()
        self._save_initial_parameters(video_url, grados_rotacion, altura, horizontal, pixels_por_mm)
        self._initialize_components(video_column, control_column, video_url,
                                    grados_rotacion, altura, horizontal, pixels_por_mm)

    def _save_initial_parameters(self, video_url, grados_rotacion, altura,
                                 horizontal, pixels_por_mm):
        """
        Guarda los parámetros iniciales.
        """
        self.initial_params = {
            "video_url": video_url,
            "grados_rotacion": grados_rotacion,
            "altura": altura,
            "horizontal": horizontal,
            "pixels_por_mm": pixels_por_mm
        }
        self.logger.debug(f"Parámetros iniciales guardados: {self.initial_params}")

    def _setup_main_window(self):
        """Configura la ventana principal."""
        self.logger.debug("Configurando ventana principal")
        self.root = tk.Tk()
        self.root.title("Control de Visión Artificial")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        geometry = get_centered_geometry(self.root, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        self.logger.debug(f"Geometría calculada: {geometry}")
        self.root.geometry(geometry)
        self.root.after(WINDOW_MAXIMIZE_DELAY_MS, self.maximizar_ventana)

    def _create_layout(self):
        """Crea la estructura básica de layouts."""
        self.logger.debug("Creando estructura básica de layouts")
        main_frame = self._create_main_frame()
        self._configure_column_weights(main_frame)
        control_column, video_column = self._create_content_columns(main_frame)
        return main_frame, video_column, control_column

    def _create_main_frame(self):
        """Crea y configura el frame principal."""
        self.logger.debug("Creando frame principal")
        main_frame = tk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky='nsew')
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        return main_frame

    def _configure_column_weights(self, main_frame):
        """Configura los pesos de las columnas en el frame principal."""
        self.logger.debug("Configurando pesos de columnas")
        main_frame.grid_columnconfigure(0, weight=2, minsize=250)  # Panel de control
        main_frame.grid_columnconfigure(1, weight=8)  # Área de video

    def _create_content_columns(self, main_frame):
        """Crea las columnas para controles y video."""
        self.logger.debug("Creando columnas de contenido")
        control_column = tk.Frame(main_frame)
        control_column.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        video_column = tk.Frame(main_frame)
        video_column.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        return control_column, video_column

    def _initialize_components(self, video_column, control_column, video_url,
                               grados_rotacion, altura, horizontal, pixels_por_mm):
        """Inicializa los componentes principales de la interfaz."""
        self.logger.debug("Iniciando inicialización de componentes")
        self._initialize_notifier()
        self._initialize_control_panel(
            control_column, grados_rotacion, pixels_por_mm, altura, horizontal
        )
        self._initialize_main_display(
            video_column, video_url, grados_rotacion, altura, horizontal, pixels_por_mm
        )
        self._configure_component_callbacks()

    def _initialize_notifier(self):
        """Inicializa el componente de notificación."""
        self.logger.debug("Inicializando GUINotifier")
        self.notifier = GUINotifier(self.logger)
        self.logger.debug("GUINotifier inicializado")

    def _initialize_control_panel(self, control_column, grados_rotacion,
                                  pixels_por_mm, altura, horizontal):
        """Inicializa el panel de control."""
        self.logger.debug("Creando instancia de ControlPanelView")
        self.control_panel = ControlPanelView(self.logger, control_column)
        self.control_panel.set_notifier(self.notifier)
        self.control_panel.initialize(None, grados_rotacion, pixels_por_mm, altura, horizontal)
        self.logger.debug("ControlPanelView inicializado")

    def _initialize_main_display(self, video_column, video_url, grados_rotacion,
                                 altura, horizontal, pixels_por_mm):
        """Inicializa la vista principal de video."""
        self.logger.debug("Creando instancia de MainDisplayView")
        self.main_display = MainDisplayView(self.logger, video_column)
        self.main_display.set_notifier(self.notifier)
        self.main_display.set_on_closing_callback(self.on_closing)
        self.main_display.initialize(video_url, grados_rotacion, altura, horizontal, pixels_por_mm)
        self.logger.debug("MainDisplayView inicializado")

    def _configure_component_callbacks(self):
        """Configura los callbacks entre componentes."""
        if self.on_parameters_update and self.control_panel:
            self.logger.debug(
                "Configurando callback de actualización de parámetros en panel de control"
            )
            self.control_panel.set_parameters_update_callback(self.on_parameters_update)
            self.logger.debug("Callback configurado")

    def maximizar_ventana(self):
        """Maximiza la ventana principal."""
        self.logger.debug("Maximizando ventana")
        self.root.state(WINDOW_STATE_MAXIMIZED)

    def ejecutar(self):
        """Inicia el bucle principal de la interfaz gráfica."""
        self.logger.debug("Ejecutando la interfaz gráfica")
        if self.main_display:
            try:
                self.is_running = True
                self.logger.debug("Iniciando mainloop de Tkinter")
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
        """Maneja el evento de cierre de la ventana."""
        self.logger.info("Cerrando la interfaz gráfica...")
        self.is_running = False
        if self.main_display:
            self.main_display.stop()
        if self.root:
            self.root.destroy()

    def update_parameters(self, parameters: Dict[str, float]) -> None:
        """
        Actualiza los parámetros en la interfaz, delegando en sus componentes.
        
        Args:
            parameters: Diccionario con los nuevos valores.
        """
        self.logger.info(f"Actualizando parámetros en GUI: {parameters}")
        if self.control_panel:
            self.control_panel.update_parameters(parameters)
        if self.main_display:
            self.main_display.update_parameters(parameters)
            self.notifier.notify_info("Parámetros aplicados al procesamiento de video")
        else:
            self.logger.warning(
                "No se pudo actualizar la vista de visualización - no está inicializada"
            )
