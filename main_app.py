import cv2
import tkinter as tk
from PIL import Image, ImageTk
import image_processing  # Importa el archivo image_processing.py

# Declarar cap como una variable global
cap = None

def start_video_stream():
    global cap, video_url
    video_url = entry.get()
    cap = cv2.VideoCapture(video_url)
    show_frame()

def show_frame():
    global cap  # Acceder a la variable cap global
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Llama a la función de procesamiento de imágenes desde el archivo image_processing.py
        processed_frame = image_processing.process_image(frame)

        img = Image.fromarray(processed_frame)
        img = ImageTk.PhotoImage(image=img)
        panel.img = img
        panel.config(image=img)
        panel.after(10, show_frame)

root = tk.Tk()
root.title("Visualización de la imagen procesada")

# Crea una entrada de texto para la URL con valor predeterminado
default_video_url = "rtsp://192.168.0.14:8080/h264.sdp"
#default_video_url = "rtsp://10.176.61.0:8080/h264.sdp"
entry = tk.Entry(root)
entry.insert(0, default_video_url)
entry.pack(padx=10, pady=10)

# Botón para iniciar la visualización
start_button = tk.Button(root, text="Iniciar visualización", command=start_video_stream)
start_button.pack(padx=10, pady=10)

# Crea un panel para mostrar la imagen
panel = tk.Label(root)
panel.pack(padx=10, pady=10)

start_video_stream()


root.mainloop()