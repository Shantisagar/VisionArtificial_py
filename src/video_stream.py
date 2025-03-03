"""
Path: src/video_stream.py
Módulo de transmisión de video que utiliza VideoStreamModel.
"""

import tkinter as tk
from PIL import Image, ImageTk
from src.models.video_stream_model import VideoStreamModel

class VideoStreamApp:
    "Aplicación de transmisión de video."
    def __init__(self, root, default_video_url, grados_rotacion, altura,
                 horizontal, pixels_por_mm, logger=None, notifier=None):
        """Inicializa la aplicación de transmisión de video."""
        self.root = root
        self.logger = logger
        self.running = False
        self.last_resize_time = 0
        self.resize_throttle = 0.5  # segundos entre actualizaciones de tamaño
        self.last_width = 0
        self.last_height = 0
        self.resize_cooldown = 500  # milisegundos
        self.resize_timer = None

        # Crear modelo de video
        self.model = VideoStreamModel(logger=logger, notifier=notifier)

        # Inicializar modelo y empezar la captura
        if not self.model.initialize(
            default_video_url,
            grados_rotacion,
            altura,
            horizontal,
            pixels_por_mm
        ):
            raise RuntimeError("No se pudo inicializar el modelo de video")

        self.setup_ui()

        # Iniciar captura de video automáticamente
        if not self.model.start():
            raise RuntimeError("No se pudo iniciar la captura de video")

        self.running = True

    def setup_ui(self):
        """Configura la UI."""
        # Crear frame contenedor principal usando grid
        self.container = tk.Frame(self.root)
        self.container.grid(row=0, column=0, sticky='nsew')
        
        # Configurar grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # El panel de video usa grid en lugar de pack
        self.panel = tk.Label(self.container, bg='black')
        self.panel.grid(row=0, column=0, sticky='nsew')
        
        # Configurar eventos de redimensionamiento
        self.root.bind('<Configure>', self.on_resize)
        self.root.after(50, self.update_frame_from_queue)

    def on_resize(self, event):
        """Maneja el evento de redimensionamiento de la ventana."""
        if event.widget == self.root:
            # Cancelar el timer anterior si existe
            if self.resize_timer:
                self.root.after_cancel(self.resize_timer)
            # Programar nueva actualización
            self.resize_timer = self.root.after(self.resize_cooldown, self.update_size)

    def on_container_resize(self, event):
        """Maneja el evento de redimensionamiento del contenedor."""
        if event.widget == self.container:
            # Cancelar el timer anterior si existe
            if self.resize_timer:
                self.root.after_cancel(self.resize_timer)
            # Programar nueva actualización
            self.resize_timer = self.root.after(self.resize_cooldown, self.update_size)

    def update_size(self):
        """Actualiza el tamaño objetivo después del cooldown."""
        width = self.container.winfo_width()
        height = self.container.winfo_height()

        # Solo actualizar si hay un cambio significativo
        if (abs(width - self.last_width) > 10 or 
            abs(height - self.last_height) > 10):
            
            if width > 100 and height > 100:
                self.model.set_target_size(width, height)
                self.last_width = width
                self.last_height = height

    def update_frame_from_queue(self):
        """Actualiza el frame en la UI desde la cola del modelo."""
        try:
            frame = self.model.get_latest_frame()
            if frame is not None:
                # Ya no necesitamos convertir el frame aquí porque ya viene en RGB
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.panel.imgtk = imgtk
                self.panel.config(image=imgtk)
        except RuntimeError as e:
            self.logger.error(f"Error al actualizar frame: {e}")
        finally:
            if self.model.running:
                self.root.after(50, self.update_frame_from_queue)

    def start(self):
        """Inicia el bucle principal de la aplicación."""
        if not self.running:
            if not self.model.start():
                raise RuntimeError("No se pudo iniciar la captura de video")
            self.running = True
        self.root.mainloop()

    def stop(self):
        """Detiene la captura y visualización de video."""
        self.running = False
        self.model.stop()

    def get_processing_stats(self):
        """Obtiene estadísticas del procesamiento de video."""
        return self.model.get_processing_stats()

    def update_parameters(self, parameters):
        """Actualiza los parámetros de procesamiento."""
        self.model.update_parameters(parameters)
