"""
Path: src/views/common_gui.py
Este script contiene una función para crear una ventana principal en tkinter.
"""

import tkinter as tk
from src.views.interface_view_helpers import get_centered_geometry  # nuevo import

def create_main_window(on_closing_callback) -> tk.Tk:
    "Crear una ventana principal configurada"
    root = tk.Tk()
    root.title("Control de Visión Artificial")
    root.protocol("WM_DELETE_WINDOW", on_closing_callback)
    # Configurar geometría centrada usando helper
    geometry = get_centered_geometry(root, window_width=1000, window_height=800)
    root.geometry(geometry)
    return root
