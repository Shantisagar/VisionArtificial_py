"""
Path: src/views/parameter_panel_layout.py
Clase para manejar la construcción del layout del panel de parámetros.
Se encarga de la creación y organización de widgets UI.
"""

# pylint: disable=too-many-arguments, too-many-locals, too-many-positional-arguments

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Callable, Tuple, List

from .tool_tip import ToolTip
from .parameter_row_factory import ParameterRowFactory

class ParameterPanelLayout:
    """
    Clase responsable de la construcción y organización 
    de los widgets del panel de parámetros.
    """

    def __init__(self, parent_frame: tk.Frame, logger: logging.Logger):
        """
        Inicializa el gestor de layout para el panel de parámetros.
        
        Args:
            parent_frame: Frame padre donde se crearán los controles
            logger: Logger configurado para registrar eventos
        """
        self.parent_frame = parent_frame
        self.logger = logger
        self.logger.debug("Inicializando ParameterPanelLayout")

        # Lista para almacenar referencias a tooltips
        self.tooltips: List[ToolTip] = []

        # Rangos para los sliders (configuración por defecto)
        self.slider_ranges = {
            'grados_rotacion': (-180, 180),
            'pixels_por_mm': (0.1, 50),
            'altura': (-500, 500),
            'horizontal': (-500, 500)
        }

        # Inicializar el factory para la creación de filas de parámetros
        self.row_factory = ParameterRowFactory(logger)

        self.logger.debug(f"Configuración por defecto - Rangos: {self.slider_ranges}")

    def set_slider_ranges(self, ranges: Dict[str, Tuple[float, float]]) -> None:
        """
        Establece los rangos para los sliders.
        
        Args:
            ranges: Diccionario con los rangos para cada parámetro
        """
        self.logger.debug(f"Actualizando rangos de sliders: {ranges}")
        self.slider_ranges.update(ranges)

    def set_parameter_help(self, help_texts: Dict[str, str]) -> None:
        """
        Establece los textos de ayuda para los parámetros.
        
        Args:
            help_texts: Diccionario con los textos de ayuda para cada parámetro
        """
        self.logger.debug(
            f"Actualizando textos de ayuda para parámetros: {list(help_texts.keys())}"
        )
        # Delegar al row_factory
        self.row_factory.set_parameter_help(help_texts)

    def create_parameter_inputs(self,
                              var_dict: Dict[str, tk.StringVar],
                              on_slider_change: Callable[[str, float], None],
                              on_update_parameters: Callable[[], None],
                              on_reset_parameters: Callable[[], None],
                              on_save_as_default: Callable[[], None],
                              on_entry_validate: Callable[[str, str], None]) -> Dict[str, tk.Scale]:
        """
        Crea los controles de parámetros en la interfaz.
        
        Args:
            var_dict: Diccionario de variables tkinter para cada parámetro
            on_slider_change: Callback para cambios en sliders
            on_update_parameters: Callback para actualizar parámetros
            on_reset_parameters: Callback para restaurar valores predeterminados
            on_save_as_default: Callback para guardar como valores predeterminados
            on_entry_validate: Callback para validar entradas
            
        Returns:
            Diccionario de sliders creados
        """
        self.logger.debug("Creando controles de parámetros en la interfaz")
        self.logger.debug(f"Valores iniciales: {[(k, v.get()) for k, v in var_dict.items()]}")

        # Frame para instrucciones
        help_frame = tk.Frame(self.parent_frame)
        help_frame.pack(fill="x", padx=10, pady=5)

        help_text = (
            "Ajuste los parámetros usando los controles deslizantes o "
            "ingresando valores directamente. Pase el cursor sobre cada "
            "elemento para ver más información."
        )
        help_label = tk.Label(help_frame, text=help_text, justify=tk.LEFT, wraplength=400,
                              font=('Helvetica', 9, 'italic'))
        help_label.pack(pady=5, anchor=tk.W)

        # Diccionario para almacenar referencias a los sliders
        sliders = {}

        # Utilizar el factory para crear cada fila de parámetros
        # Sección para Grados de rotación
        _, rotation_slider = self.row_factory.create_parameter_row(
            self.parent_frame,
            'grados_rotacion', 
            'Grados de rotación:', 
            lambda v: on_slider_change('grados_rotacion', v),
            var_dict['grados_rotacion'],
            on_entry_validate,
            self.slider_ranges['grados_rotacion']
        )
        sliders['grados_rotacion'] = rotation_slider

        # Sección para Píxeles por mm
        _, pixels_slider = self.row_factory.create_parameter_row(
            self.parent_frame,
            'pixels_por_mm', 
            'Píxeles por mm:', 
            lambda v: on_slider_change('pixels_por_mm', v),
            var_dict['pixels_por_mm'],
            on_entry_validate,
            self.slider_ranges['pixels_por_mm']
        )
        sliders['pixels_por_mm'] = pixels_slider

        # Sección para Altura (ajuste vertical)
        _, altura_slider = self.row_factory.create_parameter_row(
            self.parent_frame,
            'altura', 
            'Altura (ajuste vertical):', 
            lambda v: on_slider_change('altura', v),
            var_dict['altura'],
            on_entry_validate,
            self.slider_ranges['altura']
        )
        sliders['altura'] = altura_slider

        # Sección para desplazamiento horizontal
        _, horizontal_slider = self.row_factory.create_parameter_row(
            self.parent_frame,
            'horizontal', 
            'Ajuste horizontal:', 
            lambda v: on_slider_change('horizontal', v),
            var_dict['horizontal'],
            on_entry_validate,
            self.slider_ranges['horizontal']
        )
        sliders['horizontal'] = horizontal_slider

        # Frame para botones de acción
        buttons_frame = tk.Frame(self.parent_frame)
        buttons_frame.pack(fill="x", padx=10, pady=10)

        # Botón para actualizar todos los parámetros
        update_button = ttk.Button(
            buttons_frame,
            text="Aplicar cambios",
            command=on_update_parameters,
            style="Accent.TButton"
        )
        update_button.pack(side=tk.LEFT, padx=5, pady=5, fill="x", expand=True)
        self.tooltips.append(
            ToolTip(
                update_button,
                "Aplica todos los cambios de parámetros al procesamiento de video"
            )
        )

        # Botón para restaurar valores predeterminados
        reset_button = ttk.Button(
            buttons_frame,
            text="Restaurar valores predeterminados",
            command=on_reset_parameters,
            style="Default.TButton"
        )
        reset_button.pack(side=tk.LEFT, padx=5, pady=5, fill="x", expand=True)
        self.tooltips.append(
            ToolTip(
                reset_button,
                "Restaura los valores originales de los parámetros"
            )
        )

        # Segundo frame para botones adicionales
        buttons_frame2 = tk.Frame(self.parent_frame)
        buttons_frame2.pack(fill="x", padx=10, pady=(0,10))

        # Botón para guardar como valores predeterminados
        save_default_button = ttk.Button(
            buttons_frame2,
            text="Guardar como valores predeterminados",
            command=on_save_as_default,
            style="Save.TButton"
        )
        save_default_button.pack(padx=5, pady=5, fill="x")
        self.tooltips.append(ToolTip(
            save_default_button,
            "Guarda los valores actuales como nuevos valores "
            "predeterminados para futuras sesiones"
        ))

        # Agregar los tooltips creados por el factory
        self.tooltips.extend(self.row_factory.get_tooltips())

        self.logger.debug(f"Creados {len(sliders)} controles de parámetros")
        return sliders
