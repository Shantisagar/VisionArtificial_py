"""
Implementación experimental de una versión del procesador de video 
utilizando multiprocessing en lugar de threading para evaluar rendimiento y complejidad.
"""

import multiprocessing as mp
import time
import queue
import tkinter as tk
import logging
import numpy as np
import cv2
from PIL import Image, ImageTk

class VideoStreamProcessApp:
    """
    Versión experimental que usa multiprocessing para el procesamiento de video.
    Esta implementación es mínima para permitir pruebas comparativas.
    """

    def __init__(self, root, video_source=0, logger=None):
        """
        Inicializa la aplicación de procesamiento de video basada en procesos.
        
        Args:
            root: Widget de Tkinter donde se mostrará el video
            video_source: Índice de cámara o ruta de archivo
            logger: Logger para registrar mensajes
        """
        self.root = root
        self.video_source = video_source
        self.logger = logger or logging.getLogger(__name__)

        # Cola para comunicación entre procesos
        self.frame_queue = mp.Queue(maxsize=2)
        self.command_queue = mp.Queue()
        self.stats_queue = mp.Queue()

        # Control de estado
        self.running = mp.Value('b', True)

        # Configurar UI
        self.setup_ui()

        # Iniciar proceso de captura
        self.capture_process = mp.Process(
            target=self._capture_process_func,
            args=(
                self.frame_queue,
                self.command_queue,
                self.stats_queue,
                self.running,
                self.video_source
            )
        )
        self.capture_process.daemon = True
        self.capture_process.start()

        # Iniciar actualización de frames
        self.root.after(100, self.update_frame)

    def setup_ui(self):
        """Configura la interfaz de usuario básica."""
        self.panel = tk.Label(self.root)
        self.panel.pack(side="top", padx=10, pady=10)

        self.status_label = tk.Label(self.root, text="Iniciando procesamiento...")
        self.status_label.pack(side="bottom", padx=10, pady=10)

    @staticmethod
    def _capture_process_func(frame_queue, command_queue, stats_queue, running, video_source):
        """
        Función que ejecuta el proceso de captura y procesamiento.
        
        Args:
            frame_queue: Cola para enviar frames procesados
            command_queue: Cola para recibir comandos
            stats_queue: Cola para enviar estadísticas
            running: Flag compartido para controlar ejecución
            video_source: Fuente de video
        """
        # Inicializar captura
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            stats_queue.put({'error': f"No se pudo abrir la fuente de video {video_source}"})
            return

        # Variables para estadísticas
        frames_processed = 0
        start_time = time.time()
        last_frame_time = start_time

        try:
            while running.value:
                # Verificar comandos
                try:
                    cmd = command_queue.get_nowait()
                    if cmd == "STOP":
                        break
                except queue.Empty:
                    pass

                # Capturar frame
                ret, frame = cap.read()
                if not ret:
                    time.sleep(0.1)
                    continue

                # Procesar frame (conversión simple de color como ejemplo)
                processed = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Enviar frame si hay espacio en la cola
                try:
                    if not frame_queue.full():
                        frame_queue.put(processed, block=False)

                        # Actualizar estadísticas
                        now = time.time()
                        frames_processed += 1

                        # Enviar estadísticas ocasionalmente
                        if frames_processed % 10 == 0:
                            stats = {
                                'frames_processed': frames_processed,
                                'fps_current': (
                                    1.0 / (now - last_frame_time)
                                    if now > last_frame_time
                                    else 0
                                ),
                                'fps_average': frames_processed / (now - start_time),
                                'processing_time': now - start_time
                            }

                            try:
                                if not stats_queue.full():
                                    stats_queue.put(stats, block=False)
                            except:
                                pass

                        last_frame_time = now
                except queue.Full:
                    pass

                time.sleep(0.01)  # Pequeña pausa para evitar consumo excesivo de CPU
        finally:
            # Limpieza
            if cap and cap.isOpened():
                cap.release()

    def update_frame(self):
        """Actualiza el frame mostrado desde la cola de frames."""
        try:
            # Actualizar frame si hay disponible
            try:
                frame_array = self.frame_queue.get_nowait()
                img = Image.fromarray(frame_array)
                img_tk = ImageTk.PhotoImage(image=img)
                self.panel.img_tk = img_tk  # Evitar garbage collection
                self.panel.config(image=img_tk)
            except queue.Empty:
                pass

            # Actualizar estadísticas si hay disponibles
            try:
                stats = self.stats_queue.get_nowait()
                if 'error' in stats:
                    self.status_label.config(text=f"Error: {stats['error']}")
                else:
                    status_text = (f"Frames: {stats['frames_processed']} | "
                                  f"FPS actual: {stats['fps_current']:.1f} | "
                                  f"FPS promedio: {stats['fps_average']:.1f}")
                    self.status_label.config(text=status_text)
            except queue.Empty:
                pass

            # Programar próxima actualización
            if self.running.value:
                self.root.after(50, self.update_frame)

        except Exception as e:
            self.logger.error(f"Error al actualizar frame: {e}")
            if self.running.value:
                self.root.after(100, self.update_frame)

    def stop(self):
        """Detiene el procesamiento y libera recursos."""
        if hasattr(self, 'running'):
            self.running.value = False

        if hasattr(self, 'command_queue'):
            try:
                self.command_queue.put("STOP", block=False)
            except:
                pass

        if hasattr(self, 'capture_process'):
            self.capture_process.join(timeout=1.0)
            if self.capture_process.is_alive():
                self.capture_process.terminate()
