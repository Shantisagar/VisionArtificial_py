"""
Vista para manejar la interfaz gráfica de la aplicación.
Implementa la capa de presentación del patrón MVC.
"""

import tkinter as tk
import logging
from src.video_stream import VideoStreamApp

class GUIView:
    """Clase responsable de la gestión de la interfaz gráfica."""
    
    def __init__(self, logger: logging.Logger):
        """
        Inicializa la vista gráfica.
        
        Args:
            logger: Logger configurado para registrar eventos
        """
        self.logger = logger
        self.root = None
        self.app = None
    
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
            self.app = VideoStreamApp(
                self.root,
                video_url,
                grados_rotacion,
                altura,
                horizontal,
                pixels_por_mm
            )
            self.logger.info("Interfaz gráfica inicializada correctamente.")
        except Exception as e:
            self.logger.error(f"Error al inicializar la interfaz gráfica: {e}")
            raise
    
    def ejecutar(self):
        """Inicia el bucle principal de la interfaz gráfica."""
        if self.app is not None:
            try:
                self.logger.info("Iniciando interfaz gráfica.")
                self.app.run()
            except Exception as e:
                self.logger.error(f"Error durante la ejecución de la interfaz gráfica: {e}")
                raise
        else:
            self.logger.error("No se puede ejecutar la interfaz gráfica sin inicializar.")
            raise RuntimeError("La interfaz gráfica no está inicializada.")
