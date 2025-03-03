"""
Path: src/views/controls/gui_parameter_panel.py
Clase para manejar el panel de parámetros ajustables en la interfaz.
"""

import tkinter as tk
import logging
from typing import Dict, Callable
from src.config.constants import (
    SLIDER_RANGE_GRADOS_ROTACION,
    SLIDER_RANGE_PIXELS_POR_MM,
    SLIDER_RANGE_ALTURA,
    SLIDER_RANGE_HORIZONTAL
)
from src.views.common.gui_notifier import GUINotifier

# Constantes locales si no están en el archivo de configuración
SLIDER_FORMAT = ".2f"
SLIDER_RESOLUTION = 0.1

class GUIParameterPanel:
    """Panel de control para manejar los parámetros ajustables de la aplicación."""

    def __init__(self, parent, logger):
        """
        Inicializa el panel de parámetros.
        
        Args:
            parent: Widget padre para este panel
            logger: Logger configurado para registrar eventos
        """
        self.parent = parent
        self.logger = logger

        # Variables para los sliders
        self.grados_rotacion_var = tk.DoubleVar()
        self.pixels_por_mm_var = tk.DoubleVar()
        self.altura_var = tk.DoubleVar()
        self.horizontal_var = tk.DoubleVar()

        # Widgets de los sliders
        self.grados_rotacion_scale = None
        self.pixels_por_mm_scale = None
        self.altura_scale = None
        self.horizontal_scale = None
        self.apply_button = None

        # Callback para cuando se actualicen los parámetros
        self.on_parameters_update = None

        # Instancia de notificador
        self.notifier = None

    def set_notifier(self, notifier: GUINotifier) -> None:
        """
        Establece el notificador para este panel.
        
        Args:
            notifier: Instancia de GUINotifier
        """
        self.notifier = notifier

    def set_parameters_update_callback(self, callback: Callable[[Dict[str, float]], None]) -> None:
        """
        Establece el callback que se llamará cuando los parámetros se actualicen desde la GUI.
        
        Args:
            callback: Función a llamar con los nuevos parámetros
        """
        self.logger.debug(f"Establecido callback de actualización en GUIParameterPanel")
        self.on_parameters_update = callback

    def initialize(self, grados_rotacion, pixels_por_mm, altura, horizontal):
        """
        Inicializa el panel de parámetros con los valores iniciales.
        
        Args:
            grados_rotacion: Valor inicial para rotación
            pixels_por_mm: Valor inicial para píxeles por mm
            altura: Valor inicial para ajuste vertical
            horizontal: Valor inicial para ajuste horizontal
        """
        try:
            self.grados_rotacion_var.set(grados_rotacion)
            self.pixels_por_mm_var.set(pixels_por_mm)
            self.altura_var.set(altura)
            self.horizontal_var.set(horizontal)

            self._setup_ui()

            self.logger.info("Panel de parámetros inicializado correctamente.")
            if self.notifier:
                self.notifier.notify_info("Panel de parámetros configurado")
        except Exception as e:
            self.logger.error(f"Error al inicializar panel de parámetros: {str(e)}")
            raise

    def _setup_ui(self):
        """Configura los elementos de la interfaz de este panel."""
        # Slider para grados de rotación
        rotacion_frame = tk.Frame(self.parent)
        rotacion_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(rotacion_frame, text="Grados Rotación:").pack(side=tk.LEFT)
        self.grados_rotacion_scale = tk.Scale(
            rotacion_frame,
            from_=SLIDER_RANGE_GRADOS_ROTACION[0],
            to=SLIDER_RANGE_GRADOS_ROTACION[1],
            orient=tk.HORIZONTAL,
            variable=self.grados_rotacion_var,
            resolution=SLIDER_RESOLUTION
        )
        self.grados_rotacion_scale.pack(side=tk.RIGHT, fill="x", expand=True)

        # Slider para píxeles por mm
        pixels_frame = tk.Frame(self.parent)
        pixels_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(pixels_frame, text="Píxeles/mm:").pack(side=tk.LEFT)
        self.pixels_por_mm_scale = tk.Scale(
            pixels_frame,
            from_=SLIDER_RANGE_PIXELS_POR_MM[0],
            to=SLIDER_RANGE_PIXELS_POR_MM[1],
            orient=tk.HORIZONTAL,
            variable=self.pixels_por_mm_var,
            resolution=SLIDER_RESOLUTION
        )
        self.pixels_por_mm_scale.pack(side=tk.RIGHT, fill="x", expand=True)

        # Slider para ajuste vertical
        altura_frame = tk.Frame(self.parent)
        altura_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(altura_frame, text="Ajuste Vertical:").pack(side=tk.LEFT)
        self.altura_scale = tk.Scale(
            altura_frame,
            from_=SLIDER_RANGE_ALTURA[0],
            to=SLIDER_RANGE_ALTURA[1],
            orient=tk.HORIZONTAL,
            variable=self.altura_var,
            resolution=SLIDER_RESOLUTION
        )
        self.altura_scale.pack(side=tk.RIGHT, fill="x", expand=True)

        # Slider para ajuste horizontal
        horizontal_frame = tk.Frame(self.parent)
        horizontal_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(horizontal_frame, text="Ajuste Horizontal:").pack(side=tk.LEFT)
        self.horizontal_scale = tk.Scale(
            horizontal_frame,
            from_=SLIDER_RANGE_HORIZONTAL[0],
            to=SLIDER_RANGE_HORIZONTAL[1],
            orient=tk.HORIZONTAL,
            variable=self.horizontal_var,
            resolution=SLIDER_RESOLUTION
        )
        self.horizontal_scale.pack(side=tk.RIGHT, fill="x", expand=True)

        # Botón para aplicar cambios
        self.apply_button = tk.Button(
            self.parent,
            text="Actualizar Parámetros",
            command=self.apply_changes
        )
        self.apply_button.pack(pady=10)

    def apply_changes(self):
        """Aplica los cambios de parámetros."""
        # Obtener valores actuales
        grados_rotacion = self.grados_rotacion_var.get()
        pixels_por_mm = self.pixels_por_mm_var.get()
        altura = self.altura_var.get()
        horizontal = self.horizontal_var.get()

        # Crear diccionario de parámetros
        parameters = {
            'grados_rotacion': grados_rotacion,
            'pixels_por_mm': pixels_por_mm,
            'altura': altura,
            'horizontal': horizontal
        }

        # Registrar la acción
        self.logger.info(f"Aplicando parámetros: rotación={grados_rotacion:{SLIDER_FORMAT}}, "
                        f"píxeles/mm={pixels_por_mm:{SLIDER_FORMAT}}, "
                        f"altura={altura:{SLIDER_FORMAT}}, "
                        f"horizontal={horizontal:{SLIDER_FORMAT}}")

        # Notificar cambio si hay un callback registrado
        if self.on_parameters_update:
            self.on_parameters_update(parameters)
            if self.notifier:
                self.notifier.notify_success("Parámetros actualizados correctamente")
        else:
            self.logger.warning("No hay callback registrado para actualizar parámetros")
            if self.notifier:
                self.notifier.notify_warning("No se pudo aplicar los cambios")

    def update_parameters(self, parameters: Dict[str, float]) -> None:
        """
        Actualiza los valores de los controles con los nuevos parámetros.
        
        Args:
            parameters: Diccionario con los nuevos valores
        """
        try:
            # Actualizar las variables de los sliders si están en el diccionario
            if 'grados_rotacion' in parameters:
                self.grados_rotacion_var.set(parameters['grados_rotacion'])

            if 'pixels_por_mm' in parameters:
                self.pixels_por_mm_var.set(parameters['pixels_por_mm'])

            if 'altura' in parameters:
                self.altura_var.set(parameters['altura'])

            if 'horizontal' in parameters:
                self.horizontal_var.set(parameters['horizontal'])

            self.logger.info(f"Valores de parámetros actualizados en la GUI: {parameters}")
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.logger.error(f"Error al actualizar los valores de parámetros en la GUI: {e}")
