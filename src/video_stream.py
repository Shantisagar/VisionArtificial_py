"""
Path: src/video_stream.py

Versión modificada para separar el procesamiento de imágenes del hilo de la UI.
Se utiliza un hilo de trabajo que captura y procesa frames y luego los envía a la interfaz a través de una cola.
"""

import cv2
import tkinter as tk
from PIL import Image, ImageTk
import threading
import queue
import time
import requests
import numpy as np
from io import BytesIO
from src.image_processing import ProcessingController
from src.logs.config_logger import configurar_logging

# Configuración del logger
logger = configurar_logging()

class VideoStreamApp:
    def __init__(self, root, default_video_url, grados_rotacion, altura, horizontal, pixels_por_mm):
        """
        Inicializa la aplicación de transmisión de video.
        """
        self.root = root
        self.default_video_url = default_video_url
        self.grados_rotacion = -1 * grados_rotacion
        self.altura = altura
        self.horizontal = horizontal
        self.pixels_por_mm = pixels_por_mm
        self.controller = ProcessingController()  # instancia del controlador de procesamiento
        self.frame_queue = queue.Queue()
        self.running = True
        self.cap = None  # Solo se utilizará cuando el origen no sea HTTP

        self.setup_ui()
        self.start_worker_thread()

    def setup_ui(self):
        """
        Configura la interfaz de usuario.
        """
        self.panel = tk.Label(self.root)
        self.panel.pack(padx=10, pady=10)
        # Inicia el proceso de actualización de la UI basado en la cola de frames procesados
        self.root.after(50, self.update_frame_from_queue)

    def start_worker_thread(self):
        """
        Inicia el hilo de trabajo para capturar y procesar frames.
        Se diferencia el modo HTTP del modo cámara.
        """
        if self.default_video_url.startswith('http'):
            # Para origen HTTP: iniciar hilo que haga peticiones periódicas
            threading.Thread(target=self.http_capture_loop, daemon=True).start()
        else:
            # Para videostream local: abrir el VideoCapture y lanzar hilo de procesamiento
            self.cap = cv2.VideoCapture(self.default_video_url)
            if not self.cap.isOpened():
                logger.error("No se pudo abrir el flujo de video.")
                return
            threading.Thread(target=self.video_capture_loop, daemon=True).start()

    def video_capture_loop(self):
        """
        Bucle de captura y procesamiento para fuentes de video locales.
        """
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                logger.warning("Frame no recibido. Reintentando captura...")
                time.sleep(0.1)
                continue
            self.process_and_enqueue(frame)
            # Ajustar la tasa de captura según la capacidad de la cámara
            time.sleep(0.03)

    def http_capture_loop(self):
        """
        Bucle de captura y procesamiento para imágenes provenientes de un URL HTTP.
        """
        while self.running:
            try:
                response = requests.get(self.default_video_url, timeout=5)
                if response.status_code == 200:
                    image_bytes = np.asarray(bytearray(response.content), dtype=np.uint8)
                    frame = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
                    if frame is not None:
                        self.process_and_enqueue(frame)
                    else:
                        logger.error("No se pudo decodificar la imagen HTTP.")
                else:
                    logger.error(f"Fallo al cargar la imagen desde HTTP: Estado {response.status_code}")
            except Exception as e:
                logger.error(f"Error en http_capture_loop: {e}")
            time.sleep(2.5)  # Retraso configurable para HTTP

    def process_and_enqueue(self, frame):
        """
        Realiza el procesamiento del frame y lo coloca en la cola
        para que la UI lo actualice.
        """
        try:
            # Escalamos el frame antes de procesar para adaptarlo al monitor.
            monitor_width = self.root.winfo_screenwidth()
            monitor_height = self.root.winfo_screenheight()
            frame_scaled = self.scale_frame_to_monitor(frame, monitor_width, monitor_height)
            if frame_scaled is not None:
                # Se realiza el procesamiento intensivo en el hilo de trabajo.
                processed_frame = self.controller.process(
                    frame_scaled,
                    self.grados_rotacion,
                    self.altura,
                    self.horizontal,
                    self.pixels_por_mm
                )
                self.frame_queue.put(processed_frame)
            else:
                logger.error("No se pudo escalar el frame.")
        except Exception as e:
            logger.error(f"Error en process_and_enqueue: {e}")

    def update_frame_from_queue(self):
        """
        Método programado en el hilo principal para actualizar la UI
        con el frame procesado más reciente de la cola.
        """
        try:
            if not self.frame_queue.empty():
                processed_frame = self.frame_queue.get_nowait()
                img = Image.fromarray(processed_frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.panel.imgtk = imgtk  # referenciar para evitar recolección de basura
                self.panel.config(image=imgtk)
        except Exception as e:
            logger.error(f"Error al actualizar la UI: {e}")
        finally:
            # Vuelve a programar la actualización de la UI
            if self.running:
                self.root.after(50, self.update_frame_from_queue)

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

    def stop(self):
        """
        Detiene el hilo de trabajo y libera recursos.
        """
        self.running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()

    def run(self):
        """
        Ejecuta la aplicación.
        """
        try:
            self.root.mainloop()
        finally:
            self.stop()
