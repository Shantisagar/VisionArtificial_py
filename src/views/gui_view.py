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
        self.thread = None
        self.is_running = False
        self.stats_label = None
        self.update_interval = 500  # Actualizar estadísticas cada 500ms

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
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Crear frame para el video
            video_frame = tk.Frame(self.root)
            video_frame.pack(padx=10, pady=10)
            
            # Crear etiqueta para estadísticas
            self.stats_label = tk.Label(self.root, text="Iniciando procesamiento...", 
                                       font=('Helvetica', 10))
            self.stats_label.pack(padx=5, pady=5)

            self.app = VideoStreamApp(
                video_frame,  # Ahora pasamos el frame en lugar del root
                video_url,
                grados_rotacion,
                altura,
                horizontal,
                pixels_por_mm,
                self.logger
            )
            
            # Iniciar actualización periódica de estadísticas
            self.update_stats()
            
            self.logger.info("Interfaz gráfica inicializada correctamente.")
        except Exception as e:
            self.logger.error(f"Error al inicializar la interfaz gráfica: {e}")
            raise

    def ejecutar(self):
        """Inicia el bucle principal de la interfaz gráfica de manera no bloqueante."""
        if self.app is not None:
            try:
                self.logger.info("Iniciando interfaz gráfica.")
                self.is_running = True
                # Iniciamos mainloop en el hilo principal
                self.root.mainloop()
                self.logger.info("Interfaz gráfica finalizada.")
            except Exception as e:
                self.logger.error(f"Error durante la ejecución de la interfaz gráfica: {e}")
                self.is_running = False
                raise
        else:
            self.logger.error("No se puede ejecutar la interfaz gráfica sin inicializar.")
            raise RuntimeError("La interfaz gráfica no está inicializada.")

    def on_closing(self):
        """Maneja el evento de cierre de la ventana"""
        self.logger.info("Cerrando la interfaz gráfica...")
        self.is_running = False

        # Detenemos el streaming de video
        if self.app:
            self.app.stop()

        # Destruimos la ventana
        if self.root:
            self.root.destroy()

    def update_stats(self):
        """Actualiza las estadísticas de procesamiento en la UI"""
        if self.is_running and self.app:
            try:
                stats = self.app.get_processing_stats()
                stats_text = (f"Frames procesados: {stats['frames_processed']} | "
                             f"FPS actual: {stats['fps_current']} | "
                             f"FPS promedio: {stats['fps_average']} | "
                             f"Tiempo: {stats['processing_time']}s")
                self.stats_label.config(text=stats_text)
            except Exception as e:
                self.logger.error(f"Error al actualizar estadísticas: {e}")
        
        # Programar próxima actualización si aún está en ejecución
        if self.is_running:
            self.root.after(self.update_interval, self.update_stats)
