"""
Módulo de transmisión de video que separa la captura y el procesamiento
de imágenes del hilo de la interfaz. Se implementa la sincronización y control
de calidad de frames mediante una cola, y se agrega una gestión robusta de
errores y backoff en la captura HTTP.
"""

import cv2
import tkinter as tk
from PIL import Image, ImageTk
import threading
import queue
import time
import requests
import numpy as np
from src.image_processing import ProcessingController
from src.logs.config_logger import configurar_logging

logger = configurar_logging()

class VideoStreamApp:
    def __init__(self, root, default_video_url, grados_rotacion, altura, horizontal, pixels_por_mm):
        """
        Inicializa la aplicación de transmisión de video.
        Se inyectan las dependencias y se separan la captura y actualización de UI.
        """
        self.root = root
        self.default_video_url = default_video_url
        self.grados_rotacion = -1 * grados_rotacion
        self.altura = altura
        self.horizontal = horizontal
        self.pixels_por_mm = pixels_por_mm
        self.controller = ProcessingController()  # Lógica de procesamiento
        self.frame_queue = queue.Queue(maxsize=10)  # Control de frames
        self.running = True
        self.cap = None  # Fuente de video local

        self.setup_ui()
        self.start_worker_thread()

    def setup_ui(self):
        """
        Configura la UI; se crea el componente gráfico que mostrará los frames.
        """
        self.panel = tk.Label(self.root)
        self.panel.pack(padx=10, pady=10)
        self.root.after(50, self.update_frame_from_queue)

    def start_worker_thread(self):
        """
        Crea y lanza el hilo dedicado a la captura y procesamiento de video.
        Se distingue entre fuentes HTTP y locales.
        """
        if self.default_video_url.startswith('http'):
            threading.Thread(target=self.http_capture_loop, daemon=True).start()
        else:
            self.cap = cv2.VideoCapture(self.default_video_url)
            if not self.cap.isOpened():
                logger.error("No se pudo abrir el flujo de video.")
                return
            threading.Thread(target=self.video_capture_loop, daemon=True).start()

    def video_capture_loop(self):
        """
        Bucle para captura y procesamiento continuo en fuentes de video locales.
        """
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                logger.warning("Frame no recibido. Reintentando captura...")
                time.sleep(0.1)
                continue
            self.process_and_enqueue(frame)
            time.sleep(0.03)

    def http_capture_loop(self):
        """
        Bucle para captura y procesamiento de imágenes recibidas vía HTTP.
        Implementa un backoff progresivo en caso de errores de conexión,
        para evitar saturar la petición en situaciones de red inestable.
        """
        error_count = 0
        while self.running:
            try:
                response = requests.get(self.default_video_url, timeout=5)
                if response.status_code == 200:
                    image_bytes = np.asarray(bytearray(response.content), dtype=np.uint8)
                    frame = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
                    if frame is not None:
                        self.process_and_enqueue(frame)
                        error_count = 0  # Reiniciar el contador tras una conexión exitosa
                    else:
                        logger.error("No se pudo decodificar la imagen HTTP.")
                else:
                    logger.error(f"Fallo al cargar la imagen desde HTTP: Estado {response.status_code}")
                # Espera fija para HTTP tras una petición exitosa o fallida sin excepción
                time.sleep(2.5)
            except requests.exceptions.RequestException as e:
                error_count += 1
                wait_time = min(2.5 * error_count, 10)
                logger.error(f"Error en http_capture_loop: {e} (Intento {error_count}). Esperando {wait_time} s.")
                time.sleep(wait_time)
            except Exception as e:
                error_count += 1
                wait_time = min(2.5 * error_count, 10)
                logger.error(f"Error inesperado en http_capture_loop: {e} (Intento {error_count}). Esperando {wait_time} s.")
                time.sleep(wait_time)

    def process_and_enqueue(self, frame):
        """
        Procesa el frame y lo coloca en la cola sincronizada.
        Se vacía la cola previamente para asegurar que solo se muestra el frame más reciente.
        """
        try:
            monitor_width = self.root.winfo_screenwidth()
            monitor_height = self.root.winfo_screenheight()
            frame_scaled = self.scale_frame_to_monitor(frame, monitor_width, monitor_height)
            if frame_scaled is not None:
                processed_frame = self.controller.process(
                    frame_scaled,
                    self.grados_rotacion,
                    self.altura,
                    self.horizontal,
                    self.pixels_por_mm
                )
                # Vaciar la cola para descartar frames viejos
                with self.frame_queue.mutex:
                    self.frame_queue.queue.clear()
                self.frame_queue.put(processed_frame)
            else:
                logger.error("No se pudo escalar el frame.")
        except Exception as e:
            logger.error("Error en process_and_enqueue: %s", e)

    def update_frame_from_queue(self):
        """
        Extrae el último frame procesado y actualiza la UI.
        La actualización se agenda en el hilo principal utilizando root.after().
        """
        try:
            if not self.frame_queue.empty():
                latest_frame = None
                while not self.frame_queue.empty():
                    latest_frame = self.frame_queue.get_nowait()
                if latest_frame is not None:
                    img = Image.fromarray(latest_frame)
                    imgtk = ImageTk.PhotoImage(image=img)
                    self.panel.imgtk = imgtk  # Previene recolección de basura
                    self.panel.config(image=imgtk)
        except Exception as e:
            logger.error("Error al actualizar la UI: %s", e)
        finally:
            if self.running:
                self.root.after(50, self.update_frame_from_queue)

    def scale_frame_to_monitor(self, frame, monitor_width, monitor_height):
        """
        Ajusta la imagen para que se adapte al tamaño del monitor.
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
            logger.error("Error al escalar la imagen: %s", e)
            return None

    def stop(self):
        """
        Finaliza la ejecución y libera recursos.
        """
        self.running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()

    def run(self):
        """
        Ejecuta el loop principal de la UI.
        """
        try:
            self.root.mainloop()
        finally:
            self.stop()
