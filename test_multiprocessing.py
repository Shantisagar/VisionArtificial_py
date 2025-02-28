"""
Path: test_multiprocessing.py
Script para probar la versión experimental con multiprocessing.
"""

import tkinter as tk
import logging
from src.experimental.video_stream_process import VideoStreamProcessApp

def main():
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('test_multiprocessing')
    
    # Crear ventana
    root = tk.Tk()
    root.title("Prueba Multiprocessing")
    
    # Crear aplicación
    app = VideoStreamProcessApp(root, video_source=0, logger=logger)
    
    # Manejar cierre
    def on_closing():
        app.stop()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Iniciar loop
    root.mainloop()

if __name__ == "__main__":
    main()
