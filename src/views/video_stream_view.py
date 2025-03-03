"""
Path: src/views/video_stream_view.py
Vista dedicada a la visualización del stream de video.
"""

import tkinter as tk
from typing import Callable
from PIL import Image, ImageTk

class VideoStreamView:
    "Vista dedicada a la visualización del stream de video."
    def __init__(self, parent: tk.Widget, logger=None):
        self.parent = parent
        self.logger = logger
        self.panel = None
        self.container = None
        self.frame_update_callback = None
        self.frame_update_interval = 50  # ms entre actualizaciones
        self.resize_cooldown = 500  # ms para throttling de resize
        self.resize_timer = None
        self.last_width = 0
        self.last_height = 0
        self.on_size_changed = None

    def setup_ui(self):
        """Configura los elementos visuales."""
        # Contenedor principal con fondo negro
        self.container = tk.Frame(self.parent, bg='black')
        self.container.grid(row=0, column=0, sticky='nsew')

        # Configurar grid weights
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Panel de video con fondo negro
        self.panel = tk.Label(self.container, bg='black')
        self.panel.grid(row=0, column=0, sticky='nsew')

        # Configurar eventos
        self.container.bind('<Configure>', self.on_resize)

    def update_frame(self, frame) -> None:
        """Actualiza el frame mostrado en la UI."""
        try:
            if frame is not None:
                #self.logger.debug(f"Actualizando frame en UI: shape={frame.shape}")
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.panel.imgtk = imgtk
                self.panel.config(image=imgtk)
            else:
                self.logger.debug("Frame recibido es None")
        except (AttributeError, TypeError, ValueError) as e:
            if self.logger:
                self.logger.error(f"Error al actualizar frame: {e}")

    def set_frame_update_callback(self, callback: Callable) -> None:
        """Establece el callback para actualización de frames."""
        self.frame_update_callback = callback

    def on_resize(self, event):
        """Maneja el evento de redimensionamiento."""
        if event.widget == self.container:
            if self.resize_timer:
                self.container.after_cancel(self.resize_timer)
            self.resize_timer = self.container.after(
                self.resize_cooldown,
                lambda: self._handle_resize(event.width, event.height)
            )

    def _handle_resize(self, width, height):
        """Procesa el cambio de tamaño después del cooldown."""
        if (abs(width - self.last_width) > 10 or
            abs(height - self.last_height) > 10):
            if width > 100 and height > 100:
                self.last_width = width
                self.last_height = height
                if self.frame_update_callback:
                    self.frame_update_callback()
                    if hasattr(self, 'on_size_changed'):
                        self.on_size_changed(width, height)

    def set_size_changed_callback(self, callback):
        """Establece el callback para cambios de tamaño."""
        self.on_size_changed = callback

    def start_updates(self):
        """Inicia las actualizaciones periódicas."""
        if self.frame_update_callback:
            self.schedule_next_update()

    def schedule_next_update(self):
        """Programa la siguiente actualización de frame."""
        if self.panel and self.frame_update_callback:
            self.panel.after(self.frame_update_interval, self.update_cycle)

    def update_cycle(self):
        """Ciclo de actualización de frame."""
        if self.frame_update_callback:
            #self.logger.debug("Llamando a frame_update_callback")
            self.frame_update_callback()
            self.schedule_next_update()
        else:
            self.logger.warning("frame_update_callback no está configurado")

    def stop(self):
        """Detiene las actualizaciones."""
        self.frame_update_callback = None
