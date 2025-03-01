"""
Path: src/views/gui_view.py
Vista para manejar la interfaz gráfica de la aplicación.
Implementa la capa de presentación del patrón MVC.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional, Dict, Any, Callable
from src.video_stream import VideoStreamApp
from src.views.notifier import Notifier

class ToolTip:
    """
    Crea un tooltip para un widget dado.
    """
    def __init__(self, widget, text=None, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.delay, self.showtip)

    def unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def showtip(self):
        if self.tipwindow or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"), wraplength=250)
        label.pack(padx=3, pady=3)

    def hidetip(self):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

class GUINotifier(Notifier):
    """Implementación del notificador para la interfaz gráfica."""

    def __init__(self, logger, status_label=None):
        """
        Inicializa el notificador GUI.
        
        Args:
            logger: Logger configurado para registrar eventos
            status_label: Label de Tkinter donde se mostrarán las notificaciones (opcional)
        """
        self.logger = logger
        self.status_label = status_label
        self.notifications = []  # Almacena las últimas notificaciones

    def notify_desvio(self, desvio_mm: float, tolerancia: float) -> str:
        """
        Genera una notificación sobre un desvío detectado.
        
        Args:
            desvio_mm: Valor del desvío en milímetros
            tolerancia: Valor de tolerancia para determinar si el desvío es significativo
            
        Returns:
            Mensaje descriptivo del desvío
        """
        if desvio_mm > tolerancia:
            mensaje = f"Desvío a la derecha: {desvio_mm} mm"
        elif desvio_mm < -tolerancia:
            mensaje = f"Desvío a la izquierda: {desvio_mm} mm"
        else:
            mensaje = f"Desvío dentro de la tolerancia: {desvio_mm} mm"

        # Se elimina el log que mostraba "Desvío registrado" en la consola.
        # En su lugar, si hay un label definido en la UI, se actualiza el texto:
        if self.status_label:
            self.status_label.config(text=mensaje)

        # Almacenar la notificación para posible consulta posterior
        self.notifications.append(mensaje)
        if len(self.notifications) > 10:
            self.notifications.pop(0)

        return mensaje

    def notify_error(self, message: str, error: Optional[Exception] = None) -> None:
        """
        Muestra una notificación de error en la UI.
        
        Args:
            message: Mensaje descriptivo del error
            error: Excepción asociada al error (opcional)
        """
        error_msg = f"ERROR: {message}"
        if error:
            error_msg += f" - {str(error)}"

        self.logger.error(error_msg)

        if self.status_label:
            self.status_label.config(text=error_msg, fg="red")

    def notify_info(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Muestra una notificación informativa en la UI.
        
        Args:
            message: Mensaje informativo
            data: Datos adicionales asociados a la notificación (opcional)
        """
        info_msg = f"INFO: {message}"

        self.logger.info(info_msg)

        if self.status_label:
            self.status_label.config(text=info_msg, fg="blue")

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
        
        # Campos para los parámetros de configuración
        self.grados_rotacion_var = None
        self.pixels_por_mm_var = None
        self.altura_var = None
        self.horizontal_var = None
        
        # Callback para cuando se actualicen los parámetros
        self.on_parameters_update = None
        
        # Rangos para los sliders
        self.slider_ranges = {
            'grados_rotacion': (-180, 180),
            'pixels_por_mm': (0.1, 50),
            'altura': (-500, 500),
            'horizontal': (-500, 500)
        }
        
        # Variables para controlar si el cambio viene del slider o del campo de texto
        self.updating_from_slider = False
        self.updating_from_entry = False
        
        # Descripciones de ayuda para los parámetros
        self.parameter_help = {
            'grados_rotacion': "Ajusta la rotación de la imagen en grados. Valores positivos rotan en sentido horario, negativos en sentido antihorario.",
            'pixels_por_mm': "Define la escala de conversión de píxeles a milímetros. A mayor valor, mayor precisión en la medición de distancias.",
            'altura': "Ajusta la posición vertical de la línea de referencia en la imagen. Valores positivos mueven hacia abajo, negativos hacia arriba.",
            'horizontal': "Ajusta la posición horizontal de la línea de referencia en la imagen. Valores positivos mueven hacia la derecha, negativos hacia la izquierda."
        }
        
        # Lista para almacenar referencias a tooltips
        self.tooltips = []
        
    def set_parameters_update_callback(self, callback: Callable[[Dict[str, float]], None]) -> None:
        """
        Establece el callback que se llamará cuando los parámetros se actualicen desde la GUI.
        
        Args:
            callback: Función a llamar con los nuevos parámetros
        """
        self.on_parameters_update = callback

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

            # Crear panel de control para los parámetros
            control_frame = tk.LabelFrame(control_column, text="Parámetros de configuración")
            control_frame.pack(fill="x", padx=5, pady=5)
            
            # Inicializar variables para los campos de entrada
            self.grados_rotacion_var = tk.StringVar(value=str(grados_rotacion))
            self.pixels_por_mm_var = tk.StringVar(value=str(pixels_por_mm))
            self.altura_var = tk.StringVar(value=str(altura))
            self.horizontal_var = tk.StringVar(value=str(horizontal))
            
            # Crear campos de entrada y sliders para cada parámetro
            self._create_parameter_inputs(control_frame)

            # Crear etiqueta para estadísticas
            stats_frame = tk.LabelFrame(control_column, text="Estadísticas")
            stats_frame.pack(fill="x", padx=5, pady=5)
            
            self.stats_label = tk.Label(stats_frame, text="Iniciando procesamiento...",
                                       font=('Helvetica', 10))
            self.stats_label.pack(padx=5, pady=5)

            # Crear etiqueta para mostrar notificaciones de estado
            status_frame = tk.LabelFrame(control_column, text="Estado")
            status_frame.pack(fill="x", padx=5, pady=5)
            
            self.status_label = tk.Label(status_frame, text="",
                                        font=('Helvetica', 11), fg="blue", wraplength=250)
            self.status_label.pack(padx=5, pady=5, fill="x")

            # Inicializar el notificador GUI con la etiqueta de estado
            self.notifier = GUINotifier(self.logger, self.status_label)

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
            
    def _create_parameter_inputs(self, parent_frame):
        """
        Crea los campos de entrada y sliders para los parámetros en el frame especificado.
        
        Args:
            parent_frame: Frame donde se crearán los controles
        """
        # Frame para instrucciones
        help_frame = tk.Frame(parent_frame)
        help_frame.pack(fill="x", padx=10, pady=5)
        
        help_text = "Ajuste los parámetros usando los controles deslizantes o ingresando valores directamente. " + \
                    "Pase el cursor sobre cada elemento para ver más información."
        help_label = tk.Label(help_frame, text=help_text, justify=tk.LEFT, wraplength=400, 
                              font=('Helvetica', 9, 'italic'))
        help_label.pack(pady=5, anchor=tk.W)

        # Sección para Grados de rotación
        rotation_frame = tk.Frame(parent_frame)
        rotation_frame.pack(fill="x", padx=10, pady=5)
        
        rotation_label = tk.Label(rotation_frame, text="Grados de rotación:")
        rotation_label.grid(row=0, column=0, sticky="w", pady=2)
        self.tooltips.append(ToolTip(rotation_label, self.parameter_help['grados_rotacion']))
        
        rotation_entry = tk.Entry(rotation_frame, textvariable=self.grados_rotacion_var, width=10)
        rotation_entry.grid(row=0, column=1, padx=5, pady=2)
        self.tooltips.append(ToolTip(rotation_entry, "Ingrese un valor entre -180 y 180 grados"))
        
        # Slider para grados de rotación
        rotation_slider = tk.Scale(
            rotation_frame, 
            from_=self.slider_ranges['grados_rotacion'][0], 
            to=self.slider_ranges['grados_rotacion'][1],
            orient=tk.HORIZONTAL,
            length=200,
            command=self._on_rotation_slider_change
        )
        rotation_slider.set(float(self.grados_rotacion_var.get()))
        rotation_slider.grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.rotation_slider = rotation_slider
        self.tooltips.append(ToolTip(rotation_slider, "Deslice para ajustar la rotación de la imagen"))
        
        # Icono de ayuda para grados de rotación
        help_icon = self._create_help_button(rotation_frame, self.parameter_help['grados_rotacion'])
        help_icon.grid(row=0, column=3, padx=5, pady=2)
        
        # Validación y actualización para el campo de entrada
        rotation_entry.bind('<FocusOut>', lambda e: self._validate_and_update_from_entry('grados_rotacion'))
        rotation_entry.bind('<Return>', lambda e: self._validate_and_update_from_entry('grados_rotacion'))
        
        # Sección para Píxeles por mm
        pixels_frame = tk.Frame(parent_frame)
        pixels_frame.pack(fill="x", padx=10, pady=5)
        
        pixels_label = tk.Label(pixels_frame, text="Píxeles por mm:")
        pixels_label.grid(row=0, column=0, sticky="w", pady=2)
        self.tooltips.append(ToolTip(pixels_label, self.parameter_help['pixels_por_mm']))
        
        pixels_entry = tk.Entry(pixels_frame, textvariable=self.pixels_por_mm_var, width=10)
        pixels_entry.grid(row=0, column=1, padx=5, pady=2)
        self.tooltips.append(ToolTip(pixels_entry, "Ingrese un valor positivo mayor a 0.1"))
        
        # Slider para píxeles por mm
        pixels_slider = tk.Scale(
            pixels_frame, 
            from_=self.slider_ranges['pixels_por_mm'][0], 
            to=self.slider_ranges['pixels_por_mm'][1],
            orient=tk.HORIZONTAL,
            length=200,
            resolution=0.1,
            command=self._on_pixels_slider_change
        )
        pixels_slider.set(float(self.pixels_por_mm_var.get()))
        pixels_slider.grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.pixels_slider = pixels_slider
        self.tooltips.append(ToolTip(pixels_slider, "Deslice para ajustar la escala de medición"))
        
        # Icono de ayuda para píxeles por mm
        help_icon = self._create_help_button(pixels_frame, self.parameter_help['pixels_por_mm'])
        help_icon.grid(row=0, column=3, padx=5, pady=2)
        
        # Validación y actualización para el campo de entrada
        pixels_entry.bind('<FocusOut>', lambda e: self._validate_and_update_from_entry('pixels_por_mm'))
        pixels_entry.bind('<Return>', lambda e: self._validate_and_update_from_entry('pixels_por_mm'))
        
        # Sección para Altura (ajuste vertical)
        altura_frame = tk.Frame(parent_frame)
        altura_frame.pack(fill="x", padx=10, pady=5)
        
        altura_label = tk.Label(altura_frame, text="Altura (ajuste vertical):")
        altura_label.grid(row=0, column=0, sticky="w", pady=2)
        self.tooltips.append(ToolTip(altura_label, self.parameter_help['altura']))
        
        altura_entry = tk.Entry(altura_frame, textvariable=self.altura_var, width=10)
        altura_entry.grid(row=0, column=1, padx=5, pady=2)
        self.tooltips.append(ToolTip(altura_entry, "Ingrese un valor entre -500 y 500"))
        
        # Slider para altura
        altura_slider = tk.Scale(
            altura_frame, 
            from_=self.slider_ranges['altura'][0], 
            to=self.slider_ranges['altura'][1],
            orient=tk.HORIZONTAL,
            length=200,
            command=self._on_altura_slider_change
        )
        altura_slider.set(float(self.altura_var.get()))
        altura_slider.grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.altura_slider = altura_slider
        self.tooltips.append(ToolTip(altura_slider, "Deslice para ajustar la posición vertical de la línea de referencia"))
        
        # Icono de ayuda para altura
        help_icon = self._create_help_button(altura_frame, self.parameter_help['altura'])
        help_icon.grid(row=0, column=3, padx=5, pady=2)
        
        # Validación y actualización para el campo de entrada
        altura_entry.bind('<FocusOut>', lambda e: self._validate_and_update_from_entry('altura'))
        altura_entry.bind('<Return>', lambda e: self._validate_and_update_from_entry('altura'))
        
        # Sección para desplazamiento horizontal
        horizontal_frame = tk.Frame(parent_frame)
        horizontal_frame.pack(fill="x", padx=10, pady=5)
        
        horizontal_label = tk.Label(horizontal_frame, text="Ajuste horizontal:")
        horizontal_label.grid(row=0, column=0, sticky="w", pady=2)
        self.tooltips.append(ToolTip(horizontal_label, self.parameter_help['horizontal']))
        
        horizontal_entry = tk.Entry(horizontal_frame, textvariable=self.horizontal_var, width=10)
        horizontal_entry.grid(row=0, column=1, padx=5, pady=2)
        self.tooltips.append(ToolTip(horizontal_entry, "Ingrese un valor entre -500 y 500"))
        
        # Slider para horizontal
        horizontal_slider = tk.Scale(
            horizontal_frame, 
            from_=self.slider_ranges['horizontal'][0], 
            to=self.slider_ranges['horizontal'][1],
            orient=tk.HORIZONTAL,
            length=200,
            command=self._on_horizontal_slider_change
        )
        horizontal_slider.set(float(self.horizontal_var.get()))
        horizontal_slider.grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.horizontal_slider = horizontal_slider
        self.tooltips.append(ToolTip(horizontal_slider, "Deslice para ajustar la posición horizontal de la línea de referencia"))
        
        # Icono de ayuda para horizontal
        help_icon = self._create_help_button(horizontal_frame, self.parameter_help['horizontal'])
        help_icon.grid(row=0, column=3, padx=5, pady=2)
        
        # Validación y actualización para el campo de entrada
        horizontal_entry.bind('<FocusOut>', lambda e: self._validate_and_update_from_entry('horizontal'))
        horizontal_entry.bind('<Return>', lambda e: self._validate_and_update_from_entry('horizontal'))
        
        # Frame para botones de acción
        buttons_frame = tk.Frame(parent_frame)
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        # Botón para actualizar todos los parámetros
        update_button = ttk.Button(
            buttons_frame, 
            text="Aplicar cambios", 
            command=self._on_update_parameters,
            style="Accent.TButton"
        )
        update_button.pack(side=tk.LEFT, padx=5, pady=5, fill="x", expand=True)
        self.tooltips.append(ToolTip(update_button, "Aplica todos los cambios de parámetros al procesamiento de video"))
        
        # Botón para restaurar valores predeterminados
        reset_button = ttk.Button(
            buttons_frame,
            text="Restaurar valores predeterminados",
            command=self._on_reset_parameters,
            style="Default.TButton"
        )
        reset_button.pack(side=tk.LEFT, padx=5, pady=5, fill="x", expand=True)
        self.tooltips.append(ToolTip(reset_button, "Restaura los valores originales de los parámetros"))
        
        # Segundo frame para botones adicionales
        buttons_frame2 = tk.Frame(parent_frame)
        buttons_frame2.pack(fill="x", padx=10, pady=(0,10))
        
        # Botón para guardar como valores predeterminados
        save_default_button = ttk.Button(
            buttons_frame2,
            text="Guardar como valores predeterminados",
            command=self._on_save_as_default,
            style="Save.TButton"
        )
        save_default_button.pack(padx=5, pady=5, fill="x")
        self.tooltips.append(ToolTip(save_default_button, 
                                    "Guarda los valores actuales como nuevos valores predeterminados para futuras sesiones"))
        
        # Estilo para los botones
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="black", background="blue", font=('Helvetica', 10, 'bold'))
        style.configure("Default.TButton", foreground="black", background="gray", font=('Helvetica', 10))
        style.configure("Save.TButton", foreground="white", background="green", font=('Helvetica', 10, 'bold'))
        
    def _create_help_button(self, parent, help_text):
        """
        Crea un botón de ayuda que muestra información al hacer clic.
        
        Args:
            parent: Widget padre
            help_text: Texto de ayuda a mostrar
            
        Returns:
            Botón de ayuda configurado
        """
        help_button = tk.Label(parent, text="?", font=("Arial", 8, "bold"),
                              width=2, height=1, relief=tk.RAISED, bg="#f0f0f0")
        
        # Crear tooltip para el botón de ayuda
        self.tooltips.append(ToolTip(help_button, "Haga clic para ver información de ayuda"))
        
        # Configurar el comportamiento del botón
        help_button.bind("<Button-1>", lambda e: self._show_help_window(help_text))
        
        return help_button
        
    def _show_help_window(self, help_text):
        """
        Muestra una ventana emergente con información de ayuda.
        
        Args:
            help_text: Texto de ayuda a mostrar
        """
        help_window = tk.Toplevel(self.root)
        help_window.title("Ayuda")
        help_window.geometry("300x150")
        help_window.resizable(False, False)
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Texto de ayuda
        help_label = tk.Label(help_window, text=help_text, wraplength=280, justify=tk.LEFT, padx=10, pady=10)
        help_label.pack(fill=tk.BOTH, expand=True)
        
        # Botón para cerrar
        close_button = ttk.Button(help_window, text="Cerrar", command=help_window.destroy)
        close_button.pack(pady=10)
        
    def _on_reset_parameters(self):
        """Restaura los valores predeterminados de los parámetros"""
        try:
            # Obtener valores predeterminados de la configuración
            if self.on_parameters_update:
                # Solicitar valores predeterminados al controlador
                self.notifier.notify_info("Restaurando valores predeterminados...")
                
                # Simular evento para forzar la recarga de valores predeterminados
                self.on_parameters_update({'reset': True})
                
        except Exception as e:
            self.notifier.notify_error(f"Error al restaurar valores predeterminados: {str(e)}")

    def _on_rotation_slider_change(self, value):
        """Maneja el cambio en el slider de rotación"""
        if not self.updating_from_entry:
            self.updating_from_slider = True
            self.grados_rotacion_var.set(value)
            self.updating_from_slider = False
            self._update_parameter('grados_rotacion', float(value))
            
    def _on_pixels_slider_change(self, value):
        """Maneja el cambio en el slider de píxeles por mm"""
        if not self.updating_from_entry:
            self.updating_from_slider = True
            self.pixels_por_mm_var.set(value)
            self.updating_from_slider = False
            self._update_parameter('pixels_por_mm', float(value))
            
    def _on_altura_slider_change(self, value):
        """Maneja el cambio en el slider de altura"""
        if not self.updating_from_entry:
            self.updating_from_slider = True
            self.altura_var.set(value)
            self.updating_from_slider = False
            self._update_parameter('altura', float(value))
            
    def _on_horizontal_slider_change(self, value):
        """Maneja el cambio en el slider de ajuste horizontal"""
        if not self.updating_from_entry:
            self.updating_from_slider = True
            self.horizontal_var.set(value)
            self.updating_from_slider = False
            self._update_parameter('horizontal', float(value))
            
    def _validate_and_update_from_entry(self, param_name):
        """
        Valida el valor introducido en un campo de entrada y actualiza el slider correspondiente.
        
        Args:
            param_name: Nombre del parámetro a validar
        """
        if self.updating_from_slider:
            return
            
        try:
            self.updating_from_entry = True
            
            if param_name == 'grados_rotacion':
                value = float(self.grados_rotacion_var.get())
                min_val, max_val = self.slider_ranges['grados_rotacion']
                if min_val <= value <= max_val:
                    self.rotation_slider.set(value)
                    self._update_parameter('grados_rotacion', value)
                    # Asegurarse de que los cambios se aplican al procesamiento de video
                    if self.app:
                        self.app.update_parameters({'grados_rotacion': value})
                else:
                    # Valor fuera de rango, restauramos
                    self.grados_rotacion_var.set(str(self.rotation_slider.get()))
                    self.notifier.notify_error(f"Valor fuera de rango ({min_val} a {max_val})")
                    
            elif param_name == 'pixels_por_mm':
                value = float(self.pixels_por_mm_var.get())
                min_val, max_val = self.slider_ranges['pixels_por_mm']
                if min_val <= value <= max_val:
                    self.pixels_slider.set(value)
                    self._update_parameter('pixels_por_mm', value)
                    # Asegurarse de que los cambios se aplican al procesamiento de video
                    if self.app:
                        self.app.update_parameters({'pixels_por_mm': value})
                else:
                    self.pixels_por_mm_var.set(str(self.pixels_slider.get()))
                    self.notifier.notify_error(f"Valor fuera de rango ({min_val} a {max_val})")
                    
            elif param_name == 'altura':
                value = float(self.altura_var.get())
                min_val, max_val = self.slider_ranges['altura']
                if min_val <= value <= max_val:
                    self.altura_slider.set(value)
                    self._update_parameter('altura', value)
                    # Asegurarse de que los cambios se aplican al procesamiento de video
                    if self.app:
                        self.app.update_parameters({'altura': value})
                else:
                    self.altura_var.set(str(self.altura_slider.get()))
                    self.notifier.notify_error(f"Valor fuera de rango ({min_val} a {max_val})")
                    
            elif param_name == 'horizontal':
                value = float(self.horizontal_var.get())
                min_val, max_val = self.slider_ranges['horizontal']
                if min_val <= value <= max_val:
                    self.horizontal_slider.set(value)
                    self._update_parameter('horizontal', value)
                    # Asegurarse de que los cambios se aplican al procesamiento de video
                    if self.app:
                        self.app.update_parameters({'horizontal': value})
                else:
                    self.horizontal_var.set(str(self.horizontal_slider.get()))
                    self.notifier.notify_error(f"Valor fuera de rango ({min_val} a {max_val})")
                    
        except ValueError:
            # Si hay un error de formato, restaurar el valor anterior
            if param_name == 'grados_rotacion':
                self.grados_rotacion_var.set(str(self.rotation_slider.get()))
            elif param_name == 'pixels_por_mm':
                self.pixels_por_mm_var.set(str(self.pixels_slider.get()))
            elif param_name == 'altura':
                self.altura_var.set(str(self.altura_slider.get()))
            elif param_name == 'horizontal':
                self.horizontal_var.set(str(self.horizontal_slider.get()))
                
            self.notifier.notify_error("Valor no válido. Debe ser un número.")
            
        finally:
            self.updating_from_entry = False
            
    def _update_parameter(self, param_name, value):
        """
        Actualiza un parámetro individual y envía la actualización si hay un callback configurado.
        
        Args:
            param_name: Nombre del parámetro
            value: Nuevo valor
        """
        # Si hay un callback configurado y está corriendo en tiempo real, actualizamos
        if self.on_parameters_update and self.is_running:  # Corregido: '&&' -> 'and'
            current_params = self.get_current_parameters()
            if current_params:
                current_params[param_name] = value  # Actualizar solo el parámetro cambiado
                self.on_parameters_update(current_params)
                
    def _on_update_parameters(self):
        """Maneja el evento del botón de actualización de todos los parámetros"""
        try:
            # Obtener y validar los valores
            params = self.get_current_parameters()
            
            # Si hay un callback configurado, llamarlo con los nuevos parámetros
            if self.on_parameters_update and params:
                self.on_parameters_update(params)
                self.notifier.notify_info("Todos los parámetros actualizados correctamente")
            
        except ValueError as e:
            self.notifier.notify_error(f"Error en los parámetros: {str(e)}")
    
    def get_current_parameters(self) -> Dict[str, float]:
        """
        Obtiene los valores actuales de los parámetros desde la interfaz.
        
        Returns:
            Diccionario con los valores de los parámetros
            
        Raises:
            ValueError: Si algún valor no es válido
        """
        try:
            grados_rotacion = float(self.grados_rotacion_var.get())
            pixels_por_mm = float(self.pixels_por_mm_var.get())
            altura = float(self.altura_var.get())
            horizontal = float(self.horizontal_var.get())
            
            return {
                'grados_rotacion': grados_rotacion,
                'pixels_por_mm': pixels_por_mm,
                'altura': altura,
                'horizontal': horizontal
            }
        except ValueError:
            raise ValueError("Todos los valores deben ser números válidos")
            
    def update_parameters(self, parameters: Dict[str, float]) -> None:
        """
        Actualiza los valores de los parámetros en la interfaz y en el procesamiento.
        
        Args:
            parameters: Diccionario con los nuevos valores
        """
        # Actualizar los controles de la UI
        if 'grados_rotacion' in parameters:
            self.grados_rotacion_var.set(str(parameters['grados_rotacion']))
            if hasattr(self, 'rotation_slider'):
                self.rotation_slider.set(parameters['grados_rotacion'])
                
        if 'pixels_por_mm' in parameters:
            self.pixels_por_mm_var.set(str(parameters['pixels_por_mm']))
            if hasattr(self, 'pixels_slider'):
                self.pixels_slider.set(parameters['pixels_por_mm'])
                
        if 'altura' in parameters:
            self.altura_var.set(str(parameters['altura']))
            if hasattr(self, 'altura_slider'):
                self.altura_slider.set(parameters['altura'])
                
        if 'horizontal' in parameters:
            self.horizontal_var.set(str(parameters['horizontal']))
            if hasattr(self, 'horizontal_slider'):
                self.horizontal_slider.set(parameters['horizontal'])
            
        # Si el procesamiento de video está activo, actualizarlo también
        if self.app:
            self.app.update_parameters(parameters)
            self.notifier.notify_info("Parámetros aplicados al procesamiento de video")

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
    
    def _on_save_as_default(self):
        """Guarda los valores actuales como nuevos valores predeterminados"""
        try:
            # Obtener y validar los valores
            params = self.get_current_parameters()
            
            if params:
                # Si hay un callback configurado, llamarlo con los nuevos parámetros y una flag especial
                if self.on_parameters_update:
                    params['save_as_default'] = True  # Flag especial para indicar guardar como predeterminados
                    self.on_parameters_update(params)
                    self.notifier.notify_info("Valores guardados como nuevos valores predeterminados")
                
        except ValueError as e:
            self.notifier.notify_error(f"Error al guardar valores predeterminados: {str(e)}")
