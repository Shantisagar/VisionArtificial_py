#VisionArtificial\src\video_stream.py
import cv2
import tkinter as tk
import logging
from PIL import Image, ImageTk
import image_processing

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoStreamApp:
    def __init__(self, root, default_video_url, grados_rotacion, altura,perspectiva_default):
        self.root = root
        self.default_video_url = default_video_url
        self.cap = None
        self.grados_rotacion = grados_rotacion
        self.altura = altura  
        self.perspectiva_default = perspectiva_default
        self.setup_ui()

    def setup_ui(self):
        self.panel = tk.Label(self.root)
        self.panel.pack(padx=10, pady=10)
        self.start_video_stream()

    def start_video_stream(self):
        if self.default_video_url.endswith('.jpg'):
            self.cap = cv2.imread(self.default_video_url)
            if self.cap is not None:
                # Imprime el tamaño de la imagen
                height, width = self.cap.shape[:2]
                print(f"Tamaño de la imagen: Ancho = {width}, Alto = {height}")
                self.show_frame(testing=True)
            else:
                self.cap = cv2.VideoCapture(self.default_video_url)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)  # Ajusta el tamaño del buffer si es necesario.
                self.show_frame()
        else:
            self.cap = cv2.VideoCapture(self.default_video_url)
            self.show_frame()

    def show_frame(self, testing=False):
        if testing:
            frame = self.cap
            self.process_and_display_frame(frame, testing=True)
        else:
            ret, frame = self.cap.read()
            if not ret:
                print("Reconectando...")
                self.cap.release()
                self.cap = cv2.VideoCapture(self.default_video_url)
                return
            self.process_and_display_frame(frame)

    def scale_frame_to_monitor(self, frame, monitor_width, monitor_height):
        """Ajusta el tamaño de la imagen para que se adapte al monitor."""
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
        try:
            monitor_width = self.root.winfo_screenwidth()
            monitor_height = self.root.winfo_screenheight()
            frame_scaled = self.scale_frame_to_monitor(frame, monitor_width, monitor_height)
            if frame_scaled is not None:
                processed_frame = image_processing.process_image(frame_scaled, self.grados_rotacion, self.altura, self.perspectiva_default)
                img = Image.fromarray(processed_frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.panel.imgtk = imgtk
                self.panel.config(image=imgtk)
                if not testing:
                    self.panel.after(10, self.show_frame)
            else:
                logger.error("No se pudo escalar la imagen.")
        except Exception as e:
            logger.error("Error al procesar y mostrar el frame: %s", e)


    def run(self):
        self.root.mainloop()
