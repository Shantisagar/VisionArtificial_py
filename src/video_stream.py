# pylint: disable=broad-exception-caught, wrong-import-order, too-many-instance-attributes, too-many-arguments, too-many-positional-arguments
"""
Path: src/video_stream.py
Módulo de transmisión de video que separa la captura y el procesamiento
de imágenes del hilo de la interfaz. Se implementa la sincronización y control
de calidad de frames mediante una cola, y se agrega una gestión robusta de
errores y backoff en la captura HTTP.
"""

# Standard library imports
import tkinter as tk
import threading
import queue

# Third-party imports
from PIL import Image, ImageTk

# Local application imports
from src.controllers.video_processor import VideoProcessor
from src.capture.video_capture_factory import VideoCaptureFactory
from src.views.notifier import ConsoleNotifier
from utils.logging.logger_configurator import get_logger

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

        # Inicializar el procesador de video (separación de responsabilidades)
        self.video_processor = VideoProcessor(
            grados_rotacion=self.grados_rotacion,
            altura=self.altura,
            horizontal=self.horizontal,
            pixels_por_mm=self.pixels_por_mm,
            notifier=self.notifier,
            logger=self.logger
        )

        self.frame_queue = queue.Queue(maxsize=10)
        self.running = True
        self.video_capture = None  # Instancia de VideoCapture
        self.capture_lock = threading.Lock()  # Lock para proteger operaciones de captura

        self.setup_ui()
        self.start_video_capture()

    def setup_ui(self):
        """
        Configura la UI; se crea el componente gráfico que mostrará los frames.
        """
        self.panel = tk.Label(self.root)
        self.panel.pack(padx=10, pady=10)
        self.root.after(50, self.update_frame_from_queue)

    def start_video_capture(self):
        """
        Inicializa y arranca la captura de video usando la fábrica.
        """
        try:
            # Crear la instancia adecuada de captura usando la fábrica
            with self.capture_lock:
                self.video_capture = VideoCaptureFactory.create_capture(
                    source=self.default_video_url,
                    fps_limit=30,  # Limitar a 30 fps para fuentes locales
                    logger=self.logger
                )

                # Establecer callback para procesar frames
                self.video_capture.set_frame_callback(self.process_and_enqueue)

                # Iniciar la captura
                if not self.video_capture.start():
                    self.logger.error("No se pudo iniciar la captura de video.")
                    self.notifier.notify_error("No se pudo iniciar la captura de video")
                    return

            self.logger.info("Captura de video iniciada correctamente")
            self.notifier.notify_info("Captura de video iniciada")

        except Exception as e:
            self.logger.error(f"Error al iniciar la captura de video: {e}")
            self.notifier.notify_error("Error al iniciar la captura de video", e)

    def process_and_enqueue(self, frame):
        """
        Procesa el frame y lo coloca en la cola sincronizada.
        Este método es llamado desde el hilo de captura.
        
        Args:
            frame: Frame capturado a procesar
        """
        try:
            if not self.running:
                return

            monitor_width = self.root.winfo_screenwidth()
            monitor_height = self.root.winfo_screenheight()

            # Escalar el frame usando el procesador de video
            frame_scaled = self.video_processor.scale_frame_to_size(
                frame, monitor_width, monitor_height
            )

            if frame_scaled is not None:
                # Usar el procesador de video para procesar el frame
                processed_frame = self.video_processor.process_frame(frame_scaled)

                if processed_frame is not None:
                    # Vaciar la cola para descartar frames viejos
                    with self.frame_queue.mutex:
                        self.frame_queue.queue.clear()
                    self.frame_queue.put(processed_frame)
                else:
                    self.logger.error("Error al procesar el frame.")
            else:
                self.logger.error("No se pudo escalar el frame.")
        except Exception as e:
            self.logger.error(f"Error de procesamiento de imagen: {e}")

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
        except queue.Empty:
            pass  # Cola vacía, no es un error crítico
        except Exception as e:
            self.logger.error(f"Error al actualizar frame: {e}")
        finally:
            if self.running:
                self.root.after(50, self.update_frame_from_queue)

    def stop(self):
        """
        Finaliza la ejecución y libera recursos.
        """
        self.logger.info("Deteniendo streaming de video...")
        self.running = False

        # Detener la captura de video
        with self.capture_lock:
            if self.video_capture:
                self.video_capture.stop()

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

    def start(self):
        """Nuevo método start para iniciar el run()."""
        self.run()

    def get_processing_stats(self):
        """
        Obtiene estadísticas del procesamiento de video.
        
        Returns:
            dict: Diccionario con estadísticas (frames procesados, FPS actual, FPS promedio)
        """
        # Delegar la obtención de estadísticas al procesador de video
        stats = self.video_processor.get_processing_stats()

        # Añadir información de la fuente de video si está disponible
        if self.video_capture and self.video_capture.is_running():
            source_info = self.video_capture.source_info
            stats['source_type'] = source_info.get('type', 'unknown')

            if 'width' in source_info and 'height' in source_info:
                if source_info['width'] and source_info['height']:
                    stats['resolution'] = f"{source_info['width']}x{source_info['height']}"

        return stats

    def update_parameters(self, parameters: dict) -> None:
        """
        Actualiza los parámetros de procesamiento en tiempo real.
        
        Args:
            parameters: Diccionario con los nuevos valores de los parámetros
        """
        try:
            # Actualizar los parámetros internos
            if 'grados_rotacion' in parameters:
                self.grados_rotacion = -1 * parameters['grados_rotacion']

            if 'altura' in parameters:
                self.altura = parameters['altura']

            if 'horizontal' in parameters:
                self.horizontal = parameters['horizontal']

            if 'pixels_por_mm' in parameters:
                self.pixels_por_mm = parameters['pixels_por_mm']

            # Delegar la actualización de parámetros al procesador de video
            self.video_processor.update_parameters(parameters)

            self.logger.info(f"Parámetros de procesamiento actualizados: {parameters}")
        except Exception as e:
            self.logger.error(f"Error al actualizar parámetros: {str(e)}")
            # Notificar al usuario a través del notifier si está disponible
            if self.notifier:
                self.notifier.notify_error("Error al actualizar parámetros", e)

    def _process_frame(self, frame):
        """
        Procesa un frame de video.
        
        Args:
            frame: Frame a procesar
            
        Returns:
            Frame procesado
        """
        try:
            # Delegamos el procesamiento al procesador de video
            if frame is not None and self.video_processor is not None:
                return self.video_processor.process_frame(frame)
            return frame
        except Exception as e:
            self.logger.error(f"Error al procesar frame: {str(e)}")

            # Verificar si el notificador está disponible y usar el método modificado
            if self.notifier:
                # Usar correctamente el método con dos argumentos
                self.notifier.notify_error(f"Error al procesar frame: {str(e)}")

            return frame
