#VisionArtificial\src\video_stream.py
import cv2
import tkinter as tk
from PIL import Image, ImageTk
import image_processing
import requests
import numpy as np
from io import BytesIO

from logs.config_logger import configurar_logging

# Configuración del logger
logger = configurar_logging()

class VideoStreamApp:
    def __init__(self, root, default_video_url, grados_rotacion, altura, horizontal):
        """
        Inicializa la aplicación de transmisión de video.
        """
        self.root = root
        self.default_video_url = default_video_url
        self.cap = None
        self.grados_rotacion = -1 * grados_rotacion
        self.altura = altura
        self.horizontal = horizontal
        self.setup_ui()

    def setup_ui(self):
        """
        Configura la interfaz de usuario.
        """
        self.panel = tk.Label(self.root)
        self.panel.pack(padx=10, pady=10)
        self.start_video_stream()

    def start_video_stream(self):
        """
        Inicia la transmisión de video o la carga de la imagen desde la URL HTTP.
        """
        try:
            if self.default_video_url.startswith('http'):
                self.reload_http_image()
            else:
                self.cap = cv2.VideoCapture(self.default_video_url)
                if not self.cap.isOpened():
                    logger.error("No se pudo abrir el flujo de video.")
                self.show_frame()
        except Exception as e:
            logger.error(f"Error al iniciar la transmisión de video: {e}")

    def reload_http_image(self):
        """
        Carga y muestra una imagen desde una URL HTTP cada segundo.
        """
        response = requests.get(self.default_video_url)
        if response.status_code == 200:
            image_bytes = np.asarray(bytearray(response.content), dtype=np.uint8)
            frame = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

            if frame is not None:
                self.process_and_display_frame(frame, testing=True)
            else:
                logger.error("No se pudo cargar la imagen.")
        else:
            logger.error(f"Fallo al cargar la imagen desde HTTP: Estado {response.status_code}")

        # Vuelve a invocar reload_http_image después de 3000ms (3 segundo)
        self.panel.after(5000, self.reload_http_image)

    def show_frame(self, testing=False):
        """
        Muestra un frame del video o de la imagen.
        Si es un video, lee el siguiente frame y lo muestra.
        """
        try:
            if not self.default_video_url.startswith('http'):
                ret, frame = self.cap.read()
                if not ret:
                    logger.warning("Reconectando...")
                    self.cap.release()
                    self.cap = cv2.VideoCapture(self.default_video_url)
                    return
                self.process_and_display_frame(frame)
        except Exception as e:
            logger.error(f"Error al mostrar el frame: {e}")


    def scale_frame_to_monitor(self, frame, monitor_width, monitor_height):
        """
        Ajusta el tamaño de la imagen para que se adapte al monitor.
        """
        try:
            image_height, image_width = frame.shape[:2]
            scale_width = monitor_width / image_width
            scale_height = monitor_height / image_height
            scale = min(scale_width, scale_height)
            new_width = int(image_width * scale)
            new_height = int(image_height * scale)
            resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
            return cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        except Exception as e:
            logger.error("Error al escalar la imagen al tamaño del monitor: %s", e)
            return None

    def process_and_display_frame(self, frame, testing=False):
        """
        Procesa y muestra el frame actual.
        """
        try:
            monitor_width = self.root.winfo_screenwidth()
            monitor_height = self.root.winfo_screenheight()
            frame_scaled = self.scale_frame_to_monitor(frame, monitor_width, monitor_height)
            if frame_scaled is not None:
                processed_frame = image_processing.process_image(frame_scaled, self.grados_rotacion, self.altura, self.horizontal)
                img = Image.fromarray(processed_frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.panel.imgtk = imgtk
                self.panel.config(image=imgtk)
                if not testing:
                    self.panel.after(10, self.show_frame)
            else:
                logger.error("No se pudo escalar la imagen.")
        except Exception as e:
            logger.error(f"Error al procesar y mostrar el frame: {e}")

    def run(self):
        """
        Ejecuta la aplicación.
        """
        self.root.mainloop()
