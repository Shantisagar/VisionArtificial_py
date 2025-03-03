"""
Path: src/views/gui_view.py
Vista para manejar la interfaz gráfica de la aplicación.
Implementa la capa de presentación del patrón MVC.
"""

import tkinter as tk
import logging
from typing import Dict, Callable
from src.views.common.gui_notifier import GUINotifier
from src.views.display.main_display_view import MainDisplayView
from src.views.controls.control_panel_view import ControlPanelView
from src.views.common.interface_view_helpers import get_centered_geometry
from src.config.constants import (
    DEFAULT_WINDOW_WIDTH,
    DEFAULT_WINDOW_HEIGHT,
    WINDOW_STATE_MAXIMIZED,
    STATS_UPDATE_INTERVAL,
    WINDOW_MAXIMIZE_DELAY_MS
)

class GUIView:
    """Clase responsable de la coordinación de componentes de la interfaz gráfica."""

    def __init__(self, logger: logging.Logger):
        """
        Inicializa la vista gráfica.
        
        Args:
            logger: Logger configurado para registrar eventos
        """
        self.logger = logger
        self.logger.debug("Inicializando GUIView")
        self.root = None
        self.is_running = False
        self.update_interval = STATS_UPDATE_INTERVAL  # Actualizar estadísticas cada 500ms

        # Componente para notificaciones compartido entre vistas
        self.logger.debug("Creando instancia de GUINotifier")
        self.notifier = GUINotifier(logger)

        # Vistas específicas
        self.main_display = None
        self.control_panel = None

        # Callback para cuando se actualicen los parámetros
        self.on_parameters_update = None

        # Lista para almacenar referencias a tooltips
        self.tooltips = []
        self.initial_params = {}
        self.logger.debug("GUIView inicializado")

    def set_parameters_update_callback(self, callback: Callable[[Dict[str, float]], None]) -> None:
        """
        Establece el callback que se llamará cuando los parámetros se actualicen desde la GUI.
        
        Args:
            callback: Función a llamar con los nuevos parámetros
        """
        # Validación más robusta para el callback
        if not callback:
            self.logger.warning("Se intentó establecer un callback nulo")
            return

        if not callable(callback):
            self.logger.error(f"El callback proporcionado no es callable: {type(callback)}")
            return

        callback_name = callback.__name__ if hasattr(callback, '__name__') else 'anónimo'
        self.logger.debug(f"Estableciendo callback de actualización de parámetros: {callback_name}")
        self.on_parameters_update = callback

        # Propagar el callback al panel de control si ya está inicializado
        self._propagate_callback_to_control_panel(callback)

    def _propagate_callback_to_control_panel(self, callback: Callable) -> None:
        """
        Propaga el callback al panel de control si está inicializado.
        
        Args:
            callback: Callback a propagar
        """
        if self.control_panel:
            self.logger.debug("Propagando callback al panel de control")
            try:
                self.control_panel.set_parameters_update_callback(callback)
                self.logger.debug("Callback propagado correctamente")
            except (AttributeError, TypeError) as e:
                self.logger.error(f"Error al propagar callback al panel de control: {e}")
        else:
            self.logger.debug(
                "Control panel no inicializado aún, el callback se propagará "
                "durante la inicialización"
            )

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
        self.logger.debug(f"Inicializando UI: video={video_url}, rotación={grados_rotacion}, "
                         f"altura={altura}, horizontal={horizontal}, píxeles/mm={pixels_por_mm}")
        try:
            # Iniciar el proceso de configuración de la UI
            self._init_ui_with_params(video_url, grados_rotacion, altura, horizontal, pixels_por_mm)

            # Registrar éxito en la inicialización
            self.logger.info("Interfaz gráfica inicializada correctamente.")
            self.notifier.notify_info("Interfaz gráfica iniciada")
        except (tk.TclError, AttributeError) as e:
            self.logger.debug(f"Excepción durante inicialización UI: {e}", exc_info=True)
            self.logger.error(f"Error al inicializar la interfaz gráfica: {e}")
            raise

    def _init_ui_with_params(self, video_url, grados_rotacion, altura, horizontal, pixels_por_mm):
        """
        Configura todos los componentes de la interfaz con los parámetros proporcionados.
        
        Args:
            video_url: URL o índice de la fuente de video
            grados_rotacion: Grados de rotación para la imagen
            altura: Ajuste vertical para la imagen
            horizontal: Ajuste horizontal para la imagen
            pixels_por_mm: Relación de píxeles por milímetro
        """
        # Configurar la ventana principal
        self._setup_main_window()

        # Crear estructura de layout básica
        _, video_column, control_column = self._create_layout()

        # Guardar los parámetros iniciales para posible uso futuro
        self._save_initial_parameters(
            video_url, grados_rotacion, altura, horizontal, pixels_por_mm
        )

        # Inicializar componentes
        self._initialize_components(
            video_column, control_column, video_url,
            grados_rotacion, altura, horizontal, pixels_por_mm
        )

        # Configurar actualizaciones periódicas
        self._schedule_updates()

    def _save_initial_parameters(
        self, video_url, grados_rotacion, altura, horizontal, pixels_por_mm
    ):
        """
        Guarda los parámetros iniciales para posible uso futuro.
        
        Args:
            video_url: URL o índice de la fuente de video
            grados_rotacion: Grados de rotación para la imagen
            altura: Ajuste vertical para la imagen
            horizontal: Ajuste horizontal para la imagen
            pixels_por_mm: Relación de píxeles por milímetro
        """
        self.initial_params = {
            "video_url": video_url,
            "grados_rotacion": grados_rotacion,
            "altura": altura,
            "horizontal": horizontal,
            "pixels_por_mm": pixels_por_mm
        }
        self.logger.debug(f"Parámetros iniciales guardados: {self.initial_params}")

    def _setup_main_window(self):
        """Configura la ventana principal de la aplicación."""
        self.logger.debug("Configurando ventana principal")

        # Crear y configurar ventana root
        self.logger.debug("Creando instancia de Tk")
        self.root = tk.Tk()
        self.root.title("Control de Visión Artificial")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Configurar geometría centrada
        self.logger.debug("Calculando geometría centrada")
        geometry = get_centered_geometry(
            self.root,
            DEFAULT_WINDOW_WIDTH,
            DEFAULT_WINDOW_HEIGHT
        )
        self.logger.debug(f"Geometría calculada: {geometry}")
        self.root.geometry(geometry)

        # Programar maximización de la ventana después de un tiempo de espera
        self.logger.debug("Programando maximización de ventana")
        self.root.after(WINDOW_MAXIMIZE_DELAY_MS, self.maximizar_ventana)

    def _create_layout(self):
        """
        Crea la estructura básica de layouts para la interfaz.
        """
        self.logger.debug("Creando estructura básica de layouts")

        # Crear el frame principal
        main_frame = self._create_main_frame()

        # Configurar las columnas para el layout
        self._configure_column_weights(main_frame)

        # Crear las columnas para controles y video
        control_column, video_column = self._create_content_columns(main_frame)

        return main_frame, video_column, control_column

    def _create_main_frame(self):
        """
        Crea y configura el frame principal que contiene toda la interfaz.
        """
        self.logger.debug("Creando frame principal")
        main_frame = tk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky='nsew')

        # Configurar el root y el frame principal para que se expandan
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        return main_frame

    def _configure_column_weights(self, main_frame):
        """
        Configura los pesos de las columnas en el frame principal.
        
        Args:
            main_frame: El frame principal donde configurar las columnas
        """
        self.logger.debug("Configurando pesos de columnas")
        # Dar un peso menor a la columna de controles y mayor al video
        main_frame.grid_columnconfigure(0, weight=2, minsize=250)  # Columna de controles
        main_frame.grid_columnconfigure(1, weight=8)  # Columna de video

    def _create_content_columns(self, main_frame):
        """
        Crea las columnas para controles y video en el frame principal.
        
        Args:
            main_frame: Frame principal donde crear las columnas
            
        Returns:
            Tupla con (control_column, video_column)
        """
        self.logger.debug("Creando columnas de contenido")

        # Columna izquierda para controles con ancho mínimo
        control_column = tk.Frame(main_frame)
        control_column.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Columna derecha para el video (expansible)
        video_column = tk.Frame(main_frame)
        video_column.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)

        return control_column, video_column

    def _initialize_components(self, video_column, control_column, video_url,
                              grados_rotacion, altura, horizontal, pixels_por_mm):
        """
        Inicializa los componentes principales de la interfaz.
        
        Args:
            video_column: Frame para la visualización de video
            control_column: Frame para los controles
            video_url: URL o índice de la fuente de video
            grados_rotacion: Grados de rotación para la imagen
            altura: Ajuste vertical para la imagen
            horizontal: Ajuste horizontal para la imagen
            pixels_por_mm: Relación de píxeles por milímetro
        """
        self.logger.debug("Iniciando inicialización de componentes")

        # Inicializar el notificador de la GUI
        self._initialize_notifier()

        # Inicializar el panel de control
        self._initialize_control_panel(control_column, grados_rotacion,
                                      pixels_por_mm, altura, horizontal)

        # Inicializar la vista de visualización principal
        self._initialize_main_display(video_column, video_url, grados_rotacion,
                                     altura, horizontal, pixels_por_mm)

        # Configurar callbacks entre componentes
        self._configure_component_callbacks()

    def _initialize_notifier(self):
        """Inicializa el componente de notificación compartido."""
        self.logger.debug("Inicializando GUINotifier")
        self.notifier = GUINotifier(self.logger)
        self.logger.debug("GUINotifier inicializado")

    def _initialize_control_panel(self, control_column, grados_rotacion,
                                 pixels_por_mm, altura, horizontal):
        """
        Inicializa el panel de control.
        
        Args:
            control_column: Frame donde se colocará el panel
            grados_rotacion: Valor inicial de rotación
            pixels_por_mm: Valor inicial de conversión píxeles/mm
            altura: Valor inicial de ajuste vertical
            horizontal: Valor inicial de ajuste horizontal
        """
        self.logger.debug("Creando instancia de ControlPanelView")
        self.control_panel = ControlPanelView(self.logger, control_column)
        self.control_panel.set_notifier(self.notifier)
        self.control_panel.initialize(None, grados_rotacion, pixels_por_mm, altura, horizontal)
        self.logger.debug("ControlPanelView inicializado")

    def _initialize_main_display(self, video_column, video_url, grados_rotacion,
                                altura, horizontal, pixels_por_mm):
        """
        Inicializa la vista de visualización principal.
        
        Args:
            video_column: Frame donde se colocará la vista
            video_url: URL o índice de la fuente de video
            grados_rotacion: Valor inicial de rotación
            altura: Valor inicial de ajuste vertical
            horizontal: Valor inicial de ajuste horizontal
            pixels_por_mm: Valor inicial de conversión píxeles/mm
        """
        self.logger.debug("Creando instancia de MainDisplayView")
        self.main_display = MainDisplayView(self.logger, video_column)
        self.main_display.set_notifier(self.notifier)
        self.main_display.set_on_closing_callback(self.on_closing)
        self.main_display.initialize(
            video_url, grados_rotacion, altura, horizontal, pixels_por_mm
        )
        self.logger.debug("MainDisplayView inicializado")

    def _configure_component_callbacks(self):
        """Configura los callbacks entre componentes de la interfaz."""
        # Si tenemos un callback de actualización de parámetros, configurarlo
        if self.on_parameters_update and self.control_panel:
            self.logger.debug(
                "Configurando callback de actualización de parámetros en panel de control"
            )
            self.control_panel.set_parameters_update_callback(self.on_parameters_update)
            self.logger.debug("Callback de actualización de parámetros configurado")

    def _schedule_updates(self):
        """Programa las actualizaciones periódicas de la interfaz."""
        # Iniciar actualización periódica de estadísticas
        self.logger.debug("Programando actualización periódica de estadísticas")
        self.update_stats()

    def maximizar_ventana(self):
        """Maximiza la ventana principal."""
        self.logger.debug("Maximizando ventana")
        self.root.state(WINDOW_STATE_MAXIMIZED)

    def ejecutar(self):
        """Inicia el bucle principal de la interfaz gráfica de manera no bloqueante."""
        self.logger.debug("Método ejecutar() llamado")
        if self.main_display:
            try:
                self.logger.info("Iniciando interfaz gráfica.")
                self.is_running = True
                self.logger.debug("Iniciando mainloop de Tkinter")
                # Iniciamos mainloop en el hilo principal
                self.root.mainloop()
                self.logger.debug("Mainloop de Tkinter finalizado")
                self.logger.info("Interfaz gráfica finalizada.")
            except (tk.TclError, RuntimeError) as e:
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

        # Detenemos el componente de visualización
        if self.main_display:
            self.main_display.stop()

        # Destruimos la ventana
        if self.root:
            self.root.destroy()

    def update_stats(self):
        """Actualiza las estadísticas de procesamiento en la UI"""
        self.logger.debug("Actualizando estadísticas de procesamiento")
        if self.is_running and self.main_display and self.control_panel:
            try:
                stats = self.main_display.get_processing_stats()
                self.control_panel.update_stats(stats)
                self.logger.debug(f"Estadísticas actualizadas: {stats}")
            except Exception as e:  # pylint: disable=broad-exception-caught
                self.logger.error(f"Error al actualizar estadísticas: {e}")
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
        if self.control_panel:
            self.control_panel.update_parameters(parameters)

        # Si el procesamiento de video está activo, actualizarlo también
        if self.main_display:
            self.main_display.update_parameters(parameters)
            self.logger.info(f"Parámetros enviados a la vista de visualización: {parameters}")
            self.notifier.notify_info("Parámetros aplicados al procesamiento de video")
        else:
            self.logger.warning(
                "No se pudo actualizar la vista de visualización - no está inicializada"
            )
