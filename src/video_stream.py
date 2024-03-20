# video_stream.py
import cv2
import tkinter as tk
from PIL import Image, ImageTk
import image_processing

class VideoStreamApp:
    def __init__(self, root, default_video_url):
        self.root = root
        self.root.title("Visualización de la imagen procesada")
        self.default_video_url = default_video_url
        self.cap = None
        self.setup_ui()

    def setup_ui(self):
        self.panel = tk.Label(self.root)
        self.panel.pack(padx=10, pady=10)
        self.start_video_stream()

    def start_video_stream(self):
        if self.default_video_url.endswith('.jpg'):
            self.cap = cv2.imread(self.default_video_url)
            self.show_frame(testing=True)
        else:
            self.cap = cv2.VideoCapture(self.default_video_url)
            self.show_frame()

    def show_frame(self, testing=False):
        if testing:
            frame = self.cap
            self.process_and_display_frame(frame, testing=True)
        else:
            ret, frame = self.cap.read()
            if ret:
                self.process_and_display_frame(frame)
            else:
                self.cap.release()

    def process_and_display_frame(self, frame, testing=False):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        processed_frame = image_processing.process_image(frame)

        img = Image.fromarray(processed_frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.panel.imgtk = imgtk
        self.panel.config(image=imgtk)
        if not testing:
            self.panel.after(10, self.show_frame)

    def run(self):
        self.root.mainloop()
