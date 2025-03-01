"""
Path: src/video_stream.py
Módulo de transmisión de video que separa la captura y el procesamiento
de imágenes del hilo de la interfaz. Se implementa la sincronización y control
de calidad de frames mediante una cola, y se agrega una gestión robusta de
errores y backoff en la captura HTTP.
"""

import tkinter as tk
import threading
import queue
import time
from PIL import Image, ImageTk
import requests
import numpy as np
import cv2
from src.image_processing import ProcessingController
from utils.logging.logger_configurator import get_logger
from src.views.notifier import ConsoleNotifier

class VideoStreamApp:
    "Esta clase se encarga de la transmisión de video y la actualización de la interfaz gráfica."
    def __init__(self, root, default_video_url, grados_rotacion, altura,
                 horizontal, pixels_por_mm, logger=None, notifier=None):
        """
        Inicializa la aplicación de transmisión de video.
        Se inyectan las dependencias y se separan la captura y actualización de UI.
        
        Args:
            root: Raíz de la interfaz Tkinter
            default_video_url: URL o índice de la fuente de video
            grados_rotacion: Grados de rotación para la imagen
            altura: Ajuste vertical para la imagen
            horizontal: Ajuste horizontal para la imagen
            pixels_por_mm: Relación de píxeles por milímetro
            logger: Logger configurado (opcional, se usa el global si es None)
            notifier: Notificador para comunicar mensajes al usuario (opcional)
        """
        self.root = root
        self.default_video_url = default_video_url
        self.grados_rotacion = -1 * grados_rotacion
        self.altura = altura
        self.horizontal = horizontal
        self.pixels_por_mm = pixels_por_mm
        self.logger = logger or get_logger()
        self.notifier = notifier or ConsoleNotifier(self.logger)
        self.controller = ProcessingController(notifier=self.notifier)
        self.frame_queue = queue.Queue(maxsize=10)
        self.running = True
        self.cap = None
        self.threads = []  # Lista para mantener referencia a todos los hilos activos
        self.capture_lock = threading.Lock()  # Lock para proteger operaciones de captura
        self.frames_processed = 0  # Contador de frames procesados
        self.last_frame_time = time.time()  # Tiempo del último frame procesado
        self.fps_stats = {'current': 0, 'average': 0, 'total_frames': 0, 'start_time': time.time()}

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
        try:
            if isinstance(self.default_video_url, str) and \
               self.default_video_url.startswith('http'):
                capture_thread = threading.Thread(target=self.http_capture_loop, daemon=True)
                capture_thread.start()
                self.threads.append(capture_thread)
            else:
                with self.capture_lock:
                    self.cap = cv2.VideoCapture(self.default_video_url)
                    if not self.cap.isOpened():
                        self.logger.error("No se pudo abrir el flujo de video.")
                        return
                capture_thread = threading.Thread(target=self.video_capture_loop, daemon=True)
                capture_thread.start()
                self.threads.append(capture_thread)
            self.logger.info("Hilo de captura de video iniciado correctamente")
        except (cv2.error.CvError, ValueError) as e:
            self.logger.error(f"Error al configurar la fuente de video: {e}")
        except (threading.ThreadError, RuntimeError) as e:
            self.logger.error(f"Error al iniciar hilo de captura: {e}")
        except OSError as e:
            self.logger.error(f"Error de sistema al acceder al dispositivo de video: {e}")

    def video_capture_loop(self):
        """
        Bucle para captura y procesamiento continuo en fuentes de video locales.
        """
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                self.logger.warning("Frame no recibido. Reintentando captura...")
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
                        self.logger.error("No se pudo decodificar la imagen HTTP.")
                else:
                    self.logger.error(
                        f"Fallo al cargar la imagen desde HTTP: Estado {response.status_code}"
                    )
                # Espera fija para HTTP tras una petición exitosa o fallida sin excepción
                time.sleep(2.5)
            except requests.exceptions.RequestException as e:
                error_count += 1
                wait_time = min(2.5 * error_count, 10)
                self.logger.error(
                    f"Error en http_capture_loop: {e} (Intento {error_count}). "
                    f"Esperando {wait_time} s."
                )
                time.sleep(wait_time)
            except (ValueError, TypeError) as e:
                error_count += 1
                wait_time = min(2.5 * error_count, 10)
                self.logger.error(
                    f"Error de datos en http_capture_loop: {e} (Intento {error_count}). "
                    f"Esperando {wait_time} s."
                )
                time.sleep(wait_time)
            except cv2.error.CvError as e:
                error_count += 1
                wait_time = min(2.5 * error_count, 10)
                self.logger.error(
                    f"Error de OpenCV en http_capture_loop: {e} (Intento {error_count}). "
                    f"Esperando {wait_time} s."
                )
                time.sleep(wait_time)
            except (IOError, OSError) as e:
                error_count += 1
                wait_time = min(2.5 * error_count, 10)
                self.logger.error(
                    f"Error de E/S en http_capture_loop: {e} (Intento {error_count}). "
                    f"Esperando {wait_time} s."
                )
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
                # Actualizar estadísticas
                current_time = time.time()
                self.frames_processed += 1
                self.fps_stats['total_frames'] += 1

                # Calcular FPS actual (basado en el tiempo entre este frame y el anterior)
                time_diff = current_time - self.last_frame_time
                if time_diff > 0:
                    self.fps_stats['current'] = 1.0 / time_diff

                # Calcular FPS promedio (basado en todos los frames desde el inicio)
                total_time = current_time - self.fps_stats['start_time']
                if total_time > 0:
                    self.fps_stats['average'] = self.fps_stats['total_frames'] / total_time

                self.last_frame_time = current_time

                # Vaciar la cola para descartar frames viejos
                with self.frame_queue.mutex:
                    self.frame_queue.queue.clear()
                self.frame_queue.put(processed_frame)
            else:
                self.logger.error("No se pudo escalar el frame.")
                if self.notifier:
                    self.notifier.notify_error("No se pudo escalar el frame")
        except (cv2.error.CvError, ValueError, TypeError) as e:
            self.logger.error(f"Error de procesamiento de imagen: {e}")
            if self.notifier:
                self.notifier.notify_error("Error de procesamiento de imagen", e)

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
        except tk.TclError as e:
            self.logger.error(f"Error de interfaz Tkinter: {e}")
        except (ValueError, TypeError) as e:
            self.logger.error(f"Error en conversión de datos de imagen: {e}")
        except queue.Empty as e:
            self.logger.warning(f"Cola de frames vacía al intentar actualizar: {e}")
        except AttributeError as e:
            self.logger.error(f"Error de atributo al actualizar frame: {e}")
        except RuntimeError as e:
            self.logger.error(f"Error de runtime al actualizar UI: {e}")
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
        except cv2.error.CvError as e:
            self.logger.error("Error de OpenCV al escalar la imagen: %s", e)
            return None
        except (ValueError, TypeError) as e:
            self.logger.error("Error al escalar la imagen: %s", e)
            return None

    def stop(self):
        """
        Finaliza la ejecución y libera recursos.
        """
        self.logger.info("Deteniendo streaming de video...")
        self.running = False

        # Esperar a que los hilos terminen (con timeout)
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=1.0)

        # Liberar recursos de captura
        with self.capture_lock:
            if self.cap and hasattr(self.cap, 'release'):
                self.cap.release()

        self.logger.info("Streaming de video detenido correctamente")

    def run(self):
        """
        Ejecuta el loop principal de la UI.
        """
        try:
            self.root.mainloop()
        except tk.TclError as e:
            self.logger.error(f"Error de Tkinter en el bucle principal: {e}")
        except RuntimeError as e:
            self.logger.error(f"Error de runtime en el bucle principal: {e}")
        finally:
            self.stop()

    def get_processing_stats(self):
        """
        Obtiene estadísticas del procesamiento de video.
        
        Returns:
            dict: Diccionario con estadísticas (frames procesados, FPS actual, FPS promedio)
        """
        return {
            'frames_processed': self.frames_processed,
            'fps_current': round(self.fps_stats['current'], 1),
            'fps_average': round(self.fps_stats['average'], 1),
            'processing_time': round(time.time() - self.fps_stats['start_time'], 1)
        }

    def update_parameters(self, parameters: dict) -> None:
        """
        Actualiza los parámetros de procesamiento en tiempo real.
        
        Args:
            parameters: Diccionario con los nuevos valores de los parámetros
        """
        try:
            if 'grados_rotacion' in parameters:
                self.grados_rotacion = -1 * parameters['grados_rotacion']  # Invertir como en el constructor
            
            if 'altura' in parameters:
                self.altura = parameters['altura']
                
            if 'horizontal' in parameters:
                self.horizontal = parameters['horizontal']
                
            if 'pixels_por_mm' in parameters:
                self.pixels_por_mm = parameters['pixels_por_mm']
                
            # Actualizar controlador para que afecte al procesamiento en tiempo real
            if hasattr(self, 'controller') and self.controller:
                self.controller.update_parameters(
                    self.grados_rotacion,
                    self.altura,
                    self.horizontal,
                    self.pixels_por_mm
                )
                    
            self.logger.info(f"Parámetros de procesamiento actualizados: {parameters}")
        except Exception as e:
            self.logger.error(f"Error al actualizar parámetros: {str(e)}")
            # Notificar al usuario a través del notifier si está disponible
            if hasattr(self, 'notifier') and self.notifier:
                self.notifier.notify_error("Error al actualizar parámetros", e)
