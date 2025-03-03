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
        self.logger.debug("GUIView inicializado")

    def set_parameters_update_callback(self, callback: Callable[[Dict[str, float]], None]) -> None:
        """
        Establece el callback que se llamará cuando los parámetros se actualicen desde la GUI.
        
        Args:
            callback: Función a llamar con los nuevos parámetros
        """
        if not callback:
            self.logger.warning("Se intentó establecer un callback nulo")
            return

        callback_name = callback.__name__ if hasattr(callback, '__name__') else 'anónimo'
        self.logger.debug(f"Estableciendo callback de actualización de parámetros: {callback_name}")
        self.on_parameters_update = callback
        
        # Propagar el callback al panel de control si ya está inicializado
        if self.control_panel:
            self.logger.debug("Propagando callback al panel de control")
            self.control_panel.set_parameters_update_callback(callback)
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
            # Configurar la ventana principal
            self._setup_main_window()

            # Crear estructura de layout básica
            main_frame, video_column, control_column = self._create_layout()

            # Inicializar componentes
            self._initialize_components(
                video_column, control_column, video_url,
                grados_rotacion, altura, horizontal, pixels_por_mm
            )

            # Configurar actualizaciones periódicas
            self._schedule_updates()

            self.logger.info("Interfaz gráfica inicializada correctamente.")
            self.notifier.notify_info("Interfaz gráfica iniciada")
        except (tk.TclError, AttributeError) as e:
            self.logger.debug(f"Excepción durante inicialización UI: {e}", exc_info=True)
            self.logger.error(f"Error al inicializar la interfaz gráfica: {e}")
            raise

    def _setup_main_window(self):
        """Configura la ventana principal de la aplicación."""
        self.logger.debug("Creando instancia de Tk")
        self.root = tk.Tk()
        self.root.title("Control de Visión Artificial")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Usar helper para calcular la geometría centrada
        self.logger.debug("Calculando geometría centrada")
        geometry = get_centered_geometry(
            self.root,
            DEFAULT_WINDOW_WIDTH,
            DEFAULT_WINDOW_HEIGHT
        )
        self.logger.debug(f"Geometría calculada: {geometry}")
        self.root.geometry(geometry)

        # Programar maximización de la ventana después de 2 segundos
        self.logger.debug("Programando maximización de ventana")
        self.root.after(WINDOW_MAXIMIZE_DELAY_MS, self.maximizar_ventana)

    def _create_layout(self):
        """
        Crea la estructura básica de layouts para la interfaz.
        
        Returns:
            tuple: (main_frame, video_column, control_column)
        """
        # Crear frame principal con dos columnas
        self.logger.debug("Creando frames para UI")
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Columna izquierda para el video
        self.logger.debug("Creando columna para video")
        video_column = tk.Frame(main_frame)
        video_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Columna derecha para controles
        self.logger.debug("Creando columna para controles")
        control_column = tk.Frame(main_frame)
        control_column.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        return main_frame, video_column, control_column

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
        # Inicializar el notificador de la GUI
        self.logger.debug("Inicializando GUINotifier")
        self.notifier = GUINotifier(self.logger)

        # Inicializar el panel de control primero para obtener la etiqueta de estado
        self.logger.debug("Creando instancia de ControlPanelView")
        self.control_panel = ControlPanelView(self.logger, control_column)
        self.control_panel.set_notifier(self.notifier)
        self.control_panel.initialize(None, grados_rotacion, pixels_por_mm, altura, horizontal)
        self.logger.debug("ControlPanelView inicializado")

        # Inicializar la vista de visualización principal
        self.logger.debug("Creando instancia de MainDisplayView")
        self.main_display = MainDisplayView(self.logger, video_column)
        self.main_display.set_notifier(self.notifier)
        self.main_display.set_on_closing_callback(self.on_closing)
        self.main_display.initialize(
            video_url, grados_rotacion, altura, horizontal, pixels_por_mm
        )
        self.logger.debug("MainDisplayView inicializado")

        # Si tenemos un callback de actualización de parámetros, configurarlo
        if self.on_parameters_update:
            self.logger.debug(
                "Configurando callback de actualización de parámetros en panel de control"
            )
            self.control_panel.set_parameters_update_callback(self.on_parameters_update)

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
