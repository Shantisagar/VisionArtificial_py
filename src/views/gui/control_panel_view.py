"""
Path: src/views/controls/control_panel_view.py
Vista para manejar el panel de control con estadísticas y estado.
Parte de la separación de responsabilidades del patrón MVC.
"""

# pylint: disable=too-many-instance-attributes, too-many-arguments, too-many-positional-arguments

import tkinter as tk
import logging
from typing import Dict, Callable
from src.views.gui_parameter_panel import GUIParameterPanel
from src.views.common.gui_notifier import GUINotifier
from src.views.common.interface_view_helpers import create_color_selector, create_zoom_scale
from src.config.constants import (
    DEFAULT_ZOOM,
    DEFAULT_PAPER_COLOR,
    STATS_UPDATE_INTERVAL,
    STATUS_LABEL_FONT,
    STATUS_LABEL_COLOR,
    STATUS_LABEL_WRAP_LENGTH,
    STATS_LABEL_FONT,
    ZOOM_FORMAT
)

class ControlPanelView:
    """Clase responsable de la gestión del panel de control de la aplicación."""

    def __init__(self, logger: logging.Logger, parent=None):
        """
        Inicializa la vista del panel de control.
        
        Args:
            logger: Logger configurado para registrar eventos
            parent: Widget padre (opcional)
        """
        self.logger = logger
        self.parent = parent
        self.control_frame = None
        self.stats_label = None
        self.status_label = None
        self.parameter_panel = None
        self.update_interval = STATS_UPDATE_INTERVAL
        self.on_parameters_update = None
        self.notifier = None
        self.zoom_var = tk.DoubleVar(value=DEFAULT_ZOOM)
        self.paper_color_var = tk.StringVar(value=DEFAULT_PAPER_COLOR)
        self.apply_button = None
        # Predefine attributes to avoid warnings:
        self.zoom_scale = None
        self.paper_color_menu = None

    def set_notifier(self, notifier: GUINotifier) -> None:
        """
        Establece el notificador para esta vista.
        
        Args:
            notifier: Instancia de GUINotifier
        """
        self.notifier = notifier
        # Si el panel de parámetros ya está creado, pasarle el notificador también
        if self.parameter_panel:
            self.parameter_panel.set_notifier(notifier)

    def set_parameters_update_callback(self, callback: Callable[[Dict[str, float]], None]) -> None:
        """
        Establece el callback para actualizaciones de parámetros.
        
        Args:
            callback: Función a llamar con los nuevos parámetros
        """
        self.on_parameters_update = callback
        # Si el panel de parámetros ya está creado, pasarle el callback
        if self.parameter_panel:
            self.parameter_panel.set_parameters_update_callback(callback)

    def initialize(self, parent_frame, grados_rotacion, pixels_por_mm, altura, horizontal):
        """
        Inicializa el panel de control.
        
        Args:
            parent_frame: Frame padre donde se ubicará el panel
            grados_rotacion: Valor inicial para rotación
            pixels_por_mm: Valor inicial para píxeles por mm
            altura: Valor inicial para ajuste vertical
            horizontal: Valor inicial para ajuste horizontal
        """
        try:
            # Configurar el frame principal
            self._setup_main_frame(parent_frame)

            # Crear y configurar los componentes de la UI
            self._setup_status_panel()
            self._setup_parameter_panel(grados_rotacion, pixels_por_mm, altura, horizontal)
            self._setup_additional_controls()
            self._setup_stats_panel()

            self.logger.info("Panel de control inicializado correctamente.")
            if self.notifier:
                self.notifier.notify_info("Panel de control iniciado")
        except Exception as e:
            self.logger.error(f"Error al inicializar el panel de control: {str(e)}")
            raise

    def _setup_main_frame(self, parent_frame):
        """
        Configura el frame principal del panel de control.
        
        Args:
            parent_frame: Frame padre donde se ubicará el panel
        """
        # Crear el frame del panel de control si no se proporcionó
        if not parent_frame:
            if self.parent:
                self.control_frame = tk.Frame(self.parent)
                self.control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
            else:
                raise ValueError(
                    "Se debe proporcionar un frame padre o inicializar con un padre"
                )
        else:
            self.control_frame = parent_frame

    def _setup_status_panel(self):
        """Crea y configura el panel de estado."""
        # Crear etiqueta para mostrar notificaciones de estado
        status_frame = tk.LabelFrame(self.control_frame, text="Estado")
        status_frame.pack(fill="x", padx=5, pady=5)

        self.status_label = tk.Label(status_frame, text="",
                                    font=STATUS_LABEL_FONT,
                                    fg=STATUS_LABEL_COLOR,
                                    wraplength=STATUS_LABEL_WRAP_LENGTH)
        self.status_label.pack(padx=5, pady=5, fill="x")

        # Configurar notificador con la etiqueta de estado
        if self.notifier:
            # Usamos el nuevo método set_status_label para configurar la etiqueta
            self.notifier.set_status_label(self.status_label)

    def _setup_parameter_panel(self, grados_rotacion, pixels_por_mm, altura, horizontal):
        """
        Configura el panel de parámetros.
        
        Args:
            grados_rotacion: Valor inicial para rotación
            pixels_por_mm: Valor inicial para píxeles por mm
            altura: Valor inicial para ajuste vertical
            horizontal: Valor inicial para ajuste horizontal
        """
        # Crear panel de control para los parámetros
        control_frame = tk.LabelFrame(self.control_frame, text="Parámetros de configuración")
        control_frame.pack(fill="x", padx=5, pady=5)

        # Inicializar el panel de parámetros
        self.parameter_panel = GUIParameterPanel(control_frame, self.logger)
        if self.notifier:
            self.parameter_panel.set_notifier(self.notifier)
        self.parameter_panel.initialize(grados_rotacion, pixels_por_mm, altura, horizontal)

        # Establecer el callback para actualizaciones de parámetros
        if self.on_parameters_update:
            self.parameter_panel.set_parameters_update_callback(self.on_parameters_update)

    def _setup_additional_controls(self):
        """Crea y configura los controles adicionales (zoom, color de papel)."""
        # Frame para controles adicionales
        additional_frame = tk.LabelFrame(self.control_frame, text="Controles Adicionales")
        additional_frame.pack(fill="x", padx=5, pady=5)

        # Barra de zoom utilizando el helper, añadiendo comando para actualización automática
        self.zoom_scale = create_zoom_scale(additional_frame, self.zoom_var,
                                          command=self.on_zoom_change)
        self.zoom_scale.pack(fill="x", padx=5, pady=5)

        # Selector de color de papel
        color_frame = tk.Frame(additional_frame)
        color_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(color_frame, text="Color de Papel").pack(side=tk.LEFT)
        self.paper_color_menu = create_color_selector(color_frame, self.paper_color_var,
                                                    command=self.on_color_change)
        self.paper_color_menu.pack(side=tk.RIGHT)

        # Botón para aplicar cambios (opcional ahora, ya que los cambios son automáticos)
        self.apply_button = tk.Button(
            additional_frame,
            text="Aplicar Cambios",
            command=self.apply_changes
        )
        self.apply_button.pack(pady=10)

    def on_zoom_change(self, *args):
        """Maneja cambios en el slider de zoom."""
        if not self.on_parameters_update:
            return

        zoom = self.zoom_var.get()
        parameters = {'zoom': zoom}
        self.logger.debug(f"Zoom cambiado automáticamente: {zoom}")
        self.on_parameters_update(parameters)

    def on_color_change(self, *args):
        """Maneja cambios en la selección de color."""
        if not self.on_parameters_update:
            return

        paper_color = self.paper_color_var.get()
        parameters = {'paper_color': paper_color}
        self.logger.debug(f"Color cambiado automáticamente: {paper_color}")
        self.on_parameters_update(parameters)

    def _setup_stats_panel(self):
        """Crea y configura el panel de estadísticas."""
        # Crear etiqueta para estadísticas
        stats_frame = tk.LabelFrame(self.control_frame, text="Estadísticas")
        stats_frame.pack(fill="x", padx=5, pady=5)

        self.stats_label = tk.Label(stats_frame, text="Iniciando procesamiento...",
                                   font=STATS_LABEL_FONT)
        self.stats_label.pack(padx=5, pady=5)

    def update_stats(self, stats):
        """
        Actualiza las estadísticas mostradas en el panel.
        
        Args:
            stats: Diccionario con estadísticas a mostrar
        """
        try:
            if not self.stats_label:
                return

            stats_text = (f"Frames procesados: {stats.get('frames_processed', 0)} | "
                         f"FPS actual: {stats.get('fps_current', 0)} | "
                         f"FPS promedio: {stats.get('fps_average', 0)} | "
                         f"Tiempo: {stats.get('processing_time', 0)}s")
            self.stats_label.config(text=stats_text)
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.logger.error(f"Error al actualizar estadísticas: {str(e)}")

    def update_parameters(self, parameters: Dict[str, float]) -> None:
        """
        Actualiza los valores de los parámetros en el panel de control.
        
        Args:
            parameters: Diccionario con los nuevos valores
        """
        if self.parameter_panel:
            self.parameter_panel.update_parameters(parameters)
            self.logger.info(f"Parámetros actualizados en el panel: {parameters}")

    def apply_changes(self):
        """
        Aplica los cambios de zoom y color de papel.
        """
        # Obtener valores actuales
        zoom = self.zoom_var.get()
        paper_color = self.paper_color_var.get()

        # Crear diccionario de parámetros
        parameters = {
            'zoom': zoom,
            'paper_color': paper_color
        }

        # Registrar la acción
        self.logger.info(f"Aplicando cambios: zoom={zoom}, color={paper_color}")

        # Notificar cambio si hay un callback registrado
        if self.on_parameters_update:
            self.on_parameters_update(parameters)
            if self.notifier:
                self.notifier.notify_info(
                    f"Aplicados: zoom={zoom:{ZOOM_FORMAT}}x, color={paper_color}"
                )
        else:
            self.logger.warning("No hay callback registrado para actualizar parámetros")
