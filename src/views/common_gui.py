"""
Path: src/views/common_gui.py
Este script contiene una función para crear una ventana principal en tkinter.
"""

import tkinter as tk

def create_main_window(on_closing_callback) -> tk.Tk:
    "Crear una ventana principal configurada"
    root = tk.Tk()
    root.title("Control de Visión Artificial")
    root.protocol("WM_DELETE_WINDOW", on_closing_callback)
    # Configurar geometría centrada
    window_width = 1000
    window_height = 800
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    return root
