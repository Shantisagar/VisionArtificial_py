"""
Path: src/views/gui_parameter_panel_view.py
Vista para el panel de parámetros de configuración en la interfaz gráfica.
Se encarga exclusivamente de la creación y gestión de componentes visuales.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Callable, Tuple, List, Optional, Any

from src.views.tool_tip import ToolTip

class GUIParameterPanelView:
    """Clase responsable de la visualización de los parámetros en la interfaz gráfica."""

    def __init__(self, parent_frame: tk.Frame, logger: logging.Logger):
        """
        Inicializa la vista del panel de parámetros.
        
        Args:
            parent_frame: Frame padre donde se crearán los controles
            logger: Logger configurado para registrar eventos
        """
        self.parent_frame = parent_frame
        self.logger = logger

        # Variables para los valores de los parámetros
        self.grados_rotacion_var = tk.StringVar()
        self.pixels_por_mm_var = tk.StringVar()
        self.altura_var = tk.StringVar()
        self.horizontal_var = tk.StringVar()

        # Referencias a los controles de la UI
        self.rotation_slider = None
        self.pixels_slider = None
        self.altura_slider = None
        self.horizontal_slider = None

        # Rangos para los sliders
        self.slider_ranges = {
            'grados_rotacion': (-180, 180),
            'pixels_por_mm': (0.1, 50),
            'altura': (-500, 500),
            'horizontal': (-500, 500)
        }

        # Descripciones de ayuda para los parámetros
        self.parameter_help = {
            'grados_rotacion':
            "Ajusta la rotación de la imagen en grados. Valores positivos rotan en sentido horario, negativos en sentido antihorario.",
            'pixels_por_mm':
            "Define la escala de conversión de píxeles a milímetros. A mayor valor, mayor precisión en la medición de distancias.",
            'altura':
            "Ajusta la posición vertical de la línea de referencia en la imagen. Valores positivos mueven hacia abajo, negativos hacia arriba.",
            'horizontal': 
            "Ajusta la posición horizontal de la línea de referencia en la imagen. Valores positivos mueven hacia la derecha, negativos hacia la izquierda."
        }

        # Lista para almacenar referencias a tooltips
        self.tooltips: List[ToolTip] = []
        
        # Callbacks para cuando los controles cambien
        self.on_slider_change_callback: Optional[Callable[[str, float], None]] = None
        self.on_update_parameters_callback: Optional[Callable[[], None]] = None
        self.on_reset_parameters_callback: Optional[Callable[[], None]] = None
        self.on_save_as_default_callback: Optional[Callable[[], None]] = None
        self.on_entry_validate_callback: Optional[Callable[[str, str], Tuple[bool, Optional[str]]]] = None

    def set_callbacks(self, 
                      on_slider_change: Optional[Callable[[str, float], None]] = None,
                      on_update_parameters: Optional[Callable[[], None]] = None,
                      on_reset_parameters: Optional[Callable[[], None]] = None,
                      on_save_as_default: Optional[Callable[[], None]] = None,
                      on_entry_validate: Optional[Callable[[str, str], Tuple[bool, Optional[str]]]] = None) -> None:
        """
        Establece los callbacks que serán llamados por eventos de la UI.
        
        Args:
            on_slider_change: Callback para cambios en los sliders
            on_update_parameters: Callback para actualizar parámetros
            on_reset_parameters: Callback para restaurar valores predeterminados
            on_save_as_default: Callback para guardar como valores predeterminados
            on_entry_validate: Callback para validar entradas
        """
        self.on_slider_change_callback = on_slider_change
        self.on_update_parameters_callback = on_update_parameters
        self.on_reset_parameters_callback = on_reset_parameters
        self.on_save_as_default_callback = on_save_as_default
        self.on_entry_validate_callback = on_entry_validate

    def initialize(self, grados_rotacion: float, pixels_por_mm: float, altura: float, horizontal: float) -> None:
        """
        Inicializa los controles de parámetros con los valores proporcionados.
        
        Args:
            grados_rotacion: Grados de rotación para la imagen
            pixels_por_mm: Relación de píxeles por milímetro
            altura: Ajuste vertical para la imagen
            horizontal: Ajuste horizontal para la imagen
        """
        # Inicializar variables para los campos de entrada
        self.grados_rotacion_var.set(str(grados_rotacion))
        self.pixels_por_mm_var.set(str(pixels_por_mm))
        self.altura_var.set(str(altura))
        self.horizontal_var.set(str(horizontal))

        # Crear los controles en la interfaz
        self._create_parameter_inputs()
        self.logger.info("Panel de parámetros inicializado correctamente")

    def update_parameters_display(self, parameters: Dict[str, float]) -> None:
        """
        Actualiza la visualización de los parámetros en la interfaz.
        
        Args:
            parameters: Diccionario con los valores a mostrar
        """
        # Actualizar los controles de la UI
        if 'grados_rotacion' in parameters:
            self.grados_rotacion_var.set(str(parameters['grados_rotacion']))
            if hasattr(self, 'rotation_slider') and self.rotation_slider:
                self.rotation_slider.set(parameters['grados_rotacion'])
                
        if 'pixels_por_mm' in parameters:
            self.pixels_por_mm_var.set(str(parameters['pixels_por_mm']))
            if hasattr(self, 'pixels_slider') and self.pixels_slider:
                self.pixels_slider.set(parameters['pixels_por_mm'])
                
        if 'altura' in parameters:
            self.altura_var.set(str(parameters['altura']))
            if hasattr(self, 'altura_slider') and self.altura_slider:
                self.altura_slider.set(parameters['altura'])
                
        if 'horizontal' in parameters:
            self.horizontal_var.set(str(parameters['horizontal']))
            if hasattr(self, 'horizontal_slider') and self.horizontal_slider:
                self.horizontal_slider.set(parameters['horizontal'])

    def get_current_values(self) -> Dict[str, str]:
        """
        Obtiene los valores actuales desde los widgets de la interfaz.
        
        Returns:
            Diccionario con los valores como strings de los campos de entrada
        """
        return {
            'grados_rotacion': self.grados_rotacion_var.get(),
            'pixels_por_mm': self.pixels_por_mm_var.get(),
            'altura': self.altura_var.get(),
            'horizontal': self.horizontal_var.get()
        }

    def _create_parameter_inputs(self) -> None:
        """Crea los campos de entrada y sliders para los parámetros en el frame especificado."""
        # Frame para instrucciones
        help_frame = tk.Frame(self.parent_frame)
        help_frame.pack(fill="x", padx=10, pady=5)

        help_text = "Ajuste los parámetros usando los controles deslizantes o ingresando valores directamente. " + \
                    "Pase el cursor sobre cada elemento para ver más información."
        help_label = tk.Label(help_frame, text=help_text, justify=tk.LEFT, wraplength=400,
                              font=('Helvetica', 9, 'italic'))
        help_label.pack(pady=5, anchor=tk.W)

        # Sección para Grados de rotación
        _, rotation_slider = self._create_parameter_row(
            'grados_rotacion', 
            'Grados de rotación:', 
            lambda v: self._on_slider_change('grados_rotacion', v)
        )
        self.rotation_slider = rotation_slider

        # Sección para Píxeles por mm
        _, pixels_slider = self._create_parameter_row(
            'pixels_por_mm', 
            'Píxeles por mm:', 
            lambda v: self._on_slider_change('pixels_por_mm', v)
        )
        self.pixels_slider = pixels_slider

        # Sección para Altura (ajuste vertical)
        _, altura_slider = self._create_parameter_row(
            'altura', 
            'Altura (ajuste vertical):', 
            lambda v: self._on_slider_change('altura', v)
        )
        self.altura_slider = altura_slider

        # Sección para desplazamiento horizontal
        _, horizontal_slider = self._create_parameter_row(
            'horizontal', 
            'Ajuste horizontal:', 
            lambda v: self._on_slider_change('horizontal', v)
        )
        self.horizontal_slider = horizontal_slider

        # Frame para botones de acción
        buttons_frame = tk.Frame(self.parent_frame)
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
        buttons_frame2 = tk.Frame(self.parent_frame)
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

    def _create_parameter_row(self, param_name: str, label_text: str, slider_callback: Callable) -> Tuple[tk.Frame, tk.Scale]:
        """
        Crea una fila de controles para un parámetro (label, entry, slider, help button).
        
        Args:
            param_name: Nombre del parámetro (ej: 'grados_rotacion')
            label_text: Texto para la etiqueta del parámetro
            slider_callback: Función callback para el slider
            
        Returns:
            tuple: (frame, slider) - El frame contenedor y el slider creado
        """
        # Crear frame contenedor
        frame = tk.Frame(self.parent_frame)
        frame.pack(fill="x", padx=10, pady=5)

        # Crear etiqueta
        label = tk.Label(frame, text=label_text)
        label.grid(row=0, column=0, sticky="w", pady=2)
        self.tooltips.append(ToolTip(label, self.parameter_help[param_name]))

        # Obtener la variable StringVar correspondiente
        var = getattr(self, f"{param_name}_var")

        # Crear entry
        entry = tk.Entry(frame, textvariable=var, width=10)
        entry.grid(row=0, column=1, padx=5, pady=2)
        tooltip_text = f"Ingrese un valor entre {self.slider_ranges[param_name][0]} y {self.slider_ranges[param_name][1]}"
        self.tooltips.append(ToolTip(entry, tooltip_text))

        # Crear slider
        slider_args = {
            'from_': self.slider_ranges[param_name][0],
            'to': self.slider_ranges[param_name][1],
            'orient': tk.HORIZONTAL,
            'length': 200,
            'command': slider_callback
        }

        # Añadir parámetro 'resolution' solo si es para pixels_por_mm
        if param_name == 'pixels_por_mm':
            slider_args['resolution'] = 0.1

        slider = tk.Scale(frame, **slider_args)
        slider.set(float(var.get()))
        slider.grid(row=0, column=2, padx=5, pady=2, sticky="w")

        # Añadir tooltip al slider
        slider_tooltip_text = f"Deslice para ajustar {label_text.lower().rstrip(':')}"
        self.tooltips.append(ToolTip(slider, slider_tooltip_text))

        # Crear botón de ayuda
        help_icon = self._create_help_button(frame, self.parameter_help[param_name])
        help_icon.grid(row=0, column=3, padx=5, pady=2)

        # Configurar validaciones para el entry
        entry.bind('<FocusOut>', lambda e, pn=param_name: self._validate_entry(pn))
        entry.bind('<Return>', lambda e, pn=param_name: self._validate_entry(pn))

        return frame, slider

    def _create_help_button(self, parent: tk.Widget, help_text: str) -> tk.Label:
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

    def _show_help_window(self, help_text: str) -> None:
        """
        Muestra una ventana emergente con información de ayuda.
        
        Args:
            help_text: Texto de ayuda a mostrar
        """
        # Encontrar la ventana raíz para que la ventana emergente sea modal
        root = self.parent_frame.winfo_toplevel()

        help_window = tk.Toplevel(root)
        help_window.title("Ayuda")
        help_window.geometry("300x150")
        help_window.resizable(False, False)
        help_window.transient(root)
        help_window.grab_set()

        # Texto de ayuda
        help_label = tk.Label(help_window, text=help_text, wraplength=280, justify=tk.LEFT, padx=10, pady=10)
        help_label.pack(fill=tk.BOTH, expand=True)

        # Botón para cerrar
        close_button = ttk.Button(help_window, text="Cerrar", command=help_window.destroy)
        close_button.pack(pady=10)

    def _on_slider_change(self, param_name: str, value: Any) -> None:
        """
        Maneja los cambios en cualquier slider.
        
        Args:
            param_name: Nombre del parámetro asociado al slider
            value: Nuevo valor del slider
        """
        if self.on_slider_change_callback:
            try:
                # Convertir el valor a float ya que tkinter puede pasar el valor como string
                float_value = float(value)
                self.on_slider_change_callback(param_name, float_value)
            except (ValueError, TypeError) as e:
                self.logger.error(f"Error en _on_slider_change para {param_name}: {e}")

    def _validate_entry(self, param_name: str) -> None:
        """
        Valida el valor ingresado en un campo de entrada.
        
        Args:
            param_name: Nombre del parámetro a validar
        """
        if self.on_entry_validate_callback:
            # Obtener el valor según el parámetro
            value = getattr(self, f"{param_name}_var").get()
            self.on_entry_validate_callback(param_name, value)

    def _on_update_parameters(self) -> None:
        """Maneja el evento del botón de aplicar cambios."""
        if self.on_update_parameters_callback:
            self.on_update_parameters_callback()

    def _on_reset_parameters(self) -> None:
        """Maneja el evento del botón de restaurar valores predeterminados."""
        if self.on_reset_parameters_callback:
            self.on_reset_parameters_callback()

    def _on_save_as_default(self) -> None:
        """Maneja el evento del botón de guardar como valores predeterminados."""
        if self.on_save_as_default_callback:
            self.on_save_as_default_callback()
