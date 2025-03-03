"""
Path: src/views/common/gui.py
Funciones de utilidad compartidas para la interfaz gráfica.
"""

import tkinter as tk

def create_main_window(on_closing_callback=None):
    """
    Crea y configura una ventana principal con las configuraciones básicas.
    
    Args:
        on_closing_callback: Función a llamar cuando se cierre la ventana
        
    Returns:
        tk.Tk: Instancia de ventana principal de Tkinter
    """
    root = tk.Tk()
    root.title("Visión Artificial - Sistema de Control")

    if on_closing_callback:
        root.protocol("WM_DELETE_WINDOW", on_closing_callback)

    return root
