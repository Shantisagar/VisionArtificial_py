"""
Path: src/views/common/interface_view_helpers.py
Helper functions for common UI operations.
"""

import tkinter as tk
from src.config.constants import (
    DEFAULT_WINDOW_WIDTH,
    DEFAULT_WINDOW_HEIGHT,
    SLIDER_RANGE_GRADOS_ROTACION,
    SLIDER_RANGE_PIXELS_POR_MM,
    SLIDER_RANGE_ALTURA,
    SLIDER_RANGE_HORIZONTAL,
    SLIDER_RANGE_ZOOM,
    DEFAULT_ZOOM_RESOLUTION,
    PAPER_COLOR_OPTIONS
)

def get_centered_geometry(
    root,
    window_width=DEFAULT_WINDOW_WIDTH,
    window_height=DEFAULT_WINDOW_HEIGHT
):
    """Calculates centered window geometry for a given root Tk widget."""
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    return f"{window_width}x{window_height}+{x_position}+{y_position}"

def get_slider_ranges():
    """Returns the range definitions for various sliders."""
    return {
        'grados_rotacion': SLIDER_RANGE_GRADOS_ROTACION,
        'pixels_por_mm': SLIDER_RANGE_PIXELS_POR_MM,
        'altura': SLIDER_RANGE_ALTURA,
        'horizontal': SLIDER_RANGE_HORIZONTAL,
        'zoom': SLIDER_RANGE_ZOOM
    }

def create_color_selector(parent, variable, options=PAPER_COLOR_OPTIONS, command=None):
    """Crea y retorna un OptionMenu para la selección del color de papel."""
    menu = tk.OptionMenu(parent, variable, *options)

    # Configurar callback si se proporciona
    if command:
        variable.trace_add("write", command)

    return menu

def create_zoom_scale(parent, variable, from_=SLIDER_RANGE_ZOOM[0], to=SLIDER_RANGE_ZOOM[1],
                     resolution=DEFAULT_ZOOM_RESOLUTION, command=None):
    """
    Crea y retorna un control de escala para el zoom.
    
    Args:
        parent: Widget padre
        variable: Variable Tkinter para almacenar el valor
        from_: Valor mínimo de la escala
        to: Valor máximo de la escala
        resolution: Incremento de la escala
        command: Función a llamar cuando cambie el valor (opcional)
        
    Returns:
        tk.Scale: Control de escala configurado
    """
    scale = tk.Scale(
        parent,
        variable=variable,
        from_=from_,
        to=to,
        resolution=resolution,
        orient=tk.HORIZONTAL,
        label="Factor de Zoom",
        command=command
    )
    return scale
