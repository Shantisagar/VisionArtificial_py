import cv2
import tkinter as tk
from PIL import Image, ImageTk
import image_processing

class VideoStreamApp:
    def __init__(self, root, default_video_url, grados_rotacion,):  # Asegúrate de que este parámetro esté aquí
        self.root = root
        self.root.title("Visualización de la imagen procesada")
        self.default_video_url = default_video_url
        self.cap = None
        self.grados_rotacion = grados_rotacion  # Asegúrate de asignarlo aquí
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
            if not ret:  # Intento de reconexión si falla la lectura.
                print("Reconectando...")
                self.cap.release()
                self.cap = cv2.VideoCapture(self.default_video_url)
                return
            self.process_and_display_frame(frame)

    def process_and_display_frame(self, frame, testing=False):
        # Obtiene el tamaño del monitor (usando el primer monitor como referencia)
        monitor_width = self.root.winfo_screenwidth()
        monitor_height = self.root.winfo_screenheight()
        processed_frame = image_processing.process_image(frame, self.grados_rotacion)

        # Obtiene el tamaño de la imagen
        image_height, image_width = frame.shape[:2]

        # Calcula el factor de escala para ajustar la imagen al tamaño del monitor
        scale_width = monitor_width / image_width
        scale_height = monitor_height / image_height
        scale = min(scale_width, scale_height)

        # Asegura que la imagen no sea más grande que el monitor
        new_width = int(image_width * scale)
        new_height = int(image_height * scale)

        # Ajusta el tamaño de la imagen
        frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

        # Continúa con el procesamiento y muestra la imagen ajustada...
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        processed_frame = image_processing.process_image(frame,self.grados_rotacion)

        img = Image.fromarray(processed_frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.panel.imgtk = imgtk
        self.panel.config(image=imgtk)
        if not testing:
            self.panel.after(10, self.show_frame)

    def run(self):
        self.root.mainloop()
