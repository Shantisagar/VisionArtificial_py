"""
Path: src/views/gui_view.py
Vista para manejar la interfaz gráfica de la aplicación.
Implementa la capa de presentación del patrón MVC.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Callable
from src.video_stream import VideoStreamApp
from src.views.tool_tip import ToolTip
from src.views.gui_notifier import GUINotifier
from src.views.gui_parameter_panel import GUIParameterPanel

class GUIView:
    """Clase responsable de la gestión de la interfaz gráfica."""

    def __init__(self, logger: logging.Logger):
        """
        Inicializa la vista gráfica.
        
        Args:
            logger: Logger configurado para registrar eventos
        """
        self.logger = logger
        self.root = None
        self.app = None
        self.thread = None
        self.is_running = False
        self.stats_label = None
        self.status_label = None
        self.update_interval = 500  # Actualizar estadísticas cada 500ms
        self.notifier = None
        
        # Nuevo: referencia al panel de parámetros
        self.parameter_panel = None

        # Callback para cuando se actualicen los parámetros
        self.on_parameters_update = None

        # Lista para almacenar referencias a tooltips
        self.tooltips = []

    def set_parameters_update_callback(self, callback: Callable[[Dict[str, float]], None]) -> None:
        """
        Establece el callback que se llamará cuando los parámetros se actualicen desde la GUI.
        
        Args:
            callback: Función a llamar con los nuevos parámetros
        """
        self.on_parameters_update = callback
        # Si el panel de parámetros ya está creado, pasarle el callback
        if self.parameter_panel:
            self.parameter_panel.set_parameters_update_callback(callback)

    def inicializar_ui(self, video_url, grados_rotacion, altura, horizontal, pixels_por_mm):
        """
        Inicializa la interfaz gráfica de la aplicación.
        
        Args:
            video_url: URL o índice de la fuente de video
            grados_rotacion: Grados de rotación para la imagen
            altura: Ajuste vertical para la imagen
            horizontal: Ajuste horizontal para la imagen
            pixels_por_mm: Relación de píxeles por milímetro
        """
        try:
            self.root = tk.Tk()
            self.root.title("Control de Visión Artificial")
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

            # Crear una ventana de tamaño adecuado
            window_width = 1000
            window_height = 800
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x_position = (screen_width - window_width) // 2
            y_position = (screen_height - window_height) // 2
            self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

            # Crear frame principal con dos columnas
            main_frame = tk.Frame(self.root)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Columna izquierda para el video
            video_column = tk.Frame(main_frame)
            video_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Columna derecha para controles
            control_column = tk.Frame(main_frame)
            control_column.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

            # Frame para el video
            video_frame = tk.LabelFrame(video_column, text="Vista de cámara")
            video_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Crear etiqueta para mostrar notificaciones de estado
            status_frame = tk.LabelFrame(control_column, text="Estado")
            status_frame.pack(fill="x", padx=5, pady=5)

            self.status_label = tk.Label(status_frame, text="",
                                        font=('Helvetica', 11), fg="blue", wraplength=250)
            self.status_label.pack(padx=5, pady=5, fill="x")

            # Inicializar el notificador GUI con la etiqueta de estado
            self.notifier = GUINotifier(self.logger, self.status_label)

            # Crear panel de control para los parámetros
            control_frame = tk.LabelFrame(control_column, text="Parámetros de configuración")
            control_frame.pack(fill="x", padx=5, pady=5)

            # Inicializar correctamente el panel de parámetros
            self.parameter_panel = GUIParameterPanel(control_frame, self.logger)
            self.parameter_panel.set_notifier(self.notifier)
            self.parameter_panel.initialize(grados_rotacion, pixels_por_mm, altura, horizontal)
            
            # Establecer el callback para actualizaciones de parámetros
            if self.on_parameters_update:
                self.parameter_panel.set_parameters_update_callback(self.on_parameters_update)

            # Crear etiqueta para estadísticas
            stats_frame = tk.LabelFrame(control_column, text="Estadísticas")
            stats_frame.pack(fill="x", padx=5, pady=5)

            self.stats_label = tk.Label(stats_frame, text="Iniciando procesamiento...",
                                       font=('Helvetica', 10))
            self.stats_label.pack(padx=5, pady=5)

            self.app = VideoStreamApp(
                video_frame,
                video_url,
                grados_rotacion,
                altura,
                horizontal,
                pixels_por_mm,
                self.logger,
                self.notifier
            )

            # Iniciar actualización periódica de estadísticas
            self.update_stats()

            self.logger.info("Interfaz gráfica inicializada correctamente.")
            self.notifier.notify_info("Interfaz gráfica iniciada")
        except (KeyError, AttributeError, TypeError) as e:
            self.logger.error(f"Error al inicializar la interfaz gráfica: {e}")
            raise

    def ejecutar(self):
        """Inicia el bucle principal de la interfaz gráfica de manera no bloqueante."""
        if self.app is not None:
            try:
                self.logger.info("Iniciando interfaz gráfica.")
                self.is_running = True
                # Iniciamos mainloop en el hilo principal
                self.root.mainloop()
                self.logger.info("Interfaz gráfica finalizada.")
            except (KeyError, AttributeError, TypeError) as e:
                self.logger.error(f"Error durante la ejecución de la interfaz gráfica: {e}")
                self.is_running = False
                raise
        else:
            self.logger.error("No se puede ejecutar la interfaz gráfica sin inicializar.")
            raise RuntimeError("La interfaz gráfica no está inicializada.")

    def on_closing(self):
        """Maneja el evento de cierre de la ventana"""
        self.logger.info("Cerrando la interfaz gráfica...")
        self.is_running = False

        # Detenemos el streaming de video
        if self.app:
            self.app.stop()

        # Destruimos la ventana
        if self.root:
            self.root.destroy()

    def update_stats(self):
        """Actualiza las estadísticas de procesamiento en la UI"""
        if self.is_running and self.app:
            try:
                stats = self.app.get_processing_stats()
                stats_text = (f"Frames procesados: {stats['frames_processed']} | "
                             f"FPS actual: {stats['fps_current']} | "
                             f"FPS promedio: {stats['fps_average']} | "
                             f"Tiempo: {stats['processing_time']}s")
                self.stats_label.config(text=stats_text)
            except (KeyError, AttributeError, TypeError) as e:
                self.logger.error(f"Error al actualizar estadísticas: {e}")

        # Programar próxima actualización si aún está en ejecución
        if self.is_running:
            self.root.after(self.update_interval, self.update_stats)

    def update_parameters(self, parameters: Dict[str, float]) -> None:
        """
        Actualiza los valores de los parámetros en la interfaz y en el procesamiento.
        
        Args:
            parameters: Diccionario con los nuevos valores
        """
        self.logger.info(f"Actualizando parámetros en GUI: {parameters}")
        
        # Actualizar los controles de la UI a través del panel de parámetros
        if self.parameter_panel:
            self.parameter_panel.update_parameters(parameters)
            
        # Si el procesamiento de video está activo, actualizarlo también
        if self.app:
            # Esta es la línea clave - asegurarse de que los parámetros llegan a la app de video
            self.app.update_parameters(parameters)
            self.logger.info(f"Parámetros enviados a VideoStreamApp: {parameters}")
            self.notifier.notify_info("Parámetros aplicados al procesamiento de video")
        else:
            self.logger.warning("No se pudo actualizar VideoStreamApp - no está inicializado")

    def refresh_parameters(self):
        """Actualiza los controles con los valores actuales del procesador."""
        if hasattr(self, 'parameter_panel') and self.parameter_panel:
            parameters = {
                'grados_rotacion': self.video_processor.get_rotation(),
                'pixels_por_mm': self.video_processor.get_pixels_per_mm(),
                'altura': self.video_processor.get_height_adjustment(),
                'horizontal': self.video_processor.get_horizontal_adjustment()
            }
            self.parameter_panel.update_parameters(parameters)

    def _create_parameter_controls(self):
        """Crea los controles para ajustar parámetros de procesamiento."""
        # Frame principal para parámetros de configuración
        self.parameter_frame = ttk.LabelFrame(self.main_frame, text="Parámetros de configuración")
        self.parameter_frame.pack(fill="both", expand=False, padx=10, pady=5)
        
        # Crear el panel de parámetros y configurarlo
        self.parameter_panel = GUIParameterPanel(self.parameter_frame, self.logger)
        self.parameter_panel.set_notifier(self)
        self.parameter_panel.set_parameters_update_callback(self._on_parameters_update)
        
        # Inicializar con los valores actuales del modelo
        self.parameter_panel.initialize(
            grados_rotacion=self.video_processor.get_rotation(),
            pixels_por_mm=self.video_processor.get_pixels_per_mm(),
            altura=self.video_processor.get_height_adjustment(),
            horizontal=self.video_processor.get_horizontal_adjustment()
        )

    def _on_parameters_update(self, parameters: dict):
        """
        Callback que se invoca cuando se actualizan los parámetros desde GUIParameterPanel.
        """
        try:
            # Verificar si es una solicitud de reset
            if 'reset' in parameters:
                # Restaurar valores predeterminados del procesador
                default_params = self.video_processor.get_default_parameters()
                
                # Actualizar la UI con esos valores
                if self.parameter_panel:
                    self.parameter_panel.update_parameters(default_params)
                
                # Actualizar el procesador
                self._update_processor_parameters(default_params)
                return
                
            # Verificar si es una solicitud para guardar como predeterminados
            if 'save_as_default' in parameters:
                # Eliminar la flag especial
                params_to_save = parameters.copy()
                params_to_save.pop('save_as_default')
                
                # Guardar como predeterminados
                success = self.video_processor.save_as_default_parameters(params_to_save)
                
                if success:
                    self.notify_info("Parámetros guardados como predeterminados")
                else:
                    self.notify_error("Error al guardar parámetros predeterminados")
                
                return
            
            # Actualizar los parámetros en el procesador
            self._update_processor_parameters(parameters)
            
        except Exception as e:
            self.logger.error(f"Error al actualizar parámetros: {str(e)}")
            self.notify_error(f"Error al actualizar parámetros: {str(e)}")

    def _update_processor_parameters(self, parameters):
        """Actualiza los parámetros en el procesador de video."""
        try:
            if 'grados_rotacion' in parameters:
                self.video_processor.set_rotation(parameters['grados_rotacion'])
            
            if 'pixels_por_mm' in parameters:  
                self.video_processor.set_pixels_per_mm(parameters['pixels_por_mm'])
                
            if 'altura' in parameters:
                self.video_processor.set_height_adjustment(parameters['altura'])
                
            if 'horizontal' in parameters:
                self.video_processor.set_horizontal_adjustment(parameters['horizontal'])
                
            # Actualizar el procesamiento si el video está activo
            if self.video_processor.is_processing():
                self.video_processor.refresh_processing()
                
        except Exception as e:
            self.logger.error(f"Error al actualizar parámetros en el procesador: {str(e)}")
            raise
