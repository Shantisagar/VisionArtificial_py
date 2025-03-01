"""
Path: src/views/parameter_panel_layout.py
Clase para manejar la construcción del layout del panel de parámetros.
Se encarga de la creación y organización de widgets UI.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Callable, Tuple, Any, List

from src.views.tool_tip import ToolTip

class ParameterPanelLayout:
    """Clase responsable de la construcción y organización de los widgets del panel de parámetros."""

    def __init__(self, parent_frame: tk.Frame, logger: logging.Logger):
        """
        Inicializa el gestor de layout para el panel de parámetros.
        
        Args:
            parent_frame: Frame padre donde se crearán los controles
            logger: Logger configurado para registrar eventos
        """
        self.parent_frame = parent_frame
        self.logger = logger
        self.logger.debug("Inicializando ParameterPanelLayout")
        
        # Lista para almacenar referencias a tooltips
        self.tooltips: List[ToolTip] = []
        
        # Rangos para los sliders (configuración por defecto)
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
        self.logger.debug(f"Configuración por defecto - Rangos: {self.slider_ranges}")
        
    def set_slider_ranges(self, ranges: Dict[str, Tuple[float, float]]) -> None:
        """
        Establece los rangos para los sliders.
        
        Args:
            ranges: Diccionario con los rangos para cada parámetro
        """
        self.logger.debug(f"Actualizando rangos de sliders: {ranges}")
        self.slider_ranges.update(ranges)
            
    def set_parameter_help(self, help_texts: Dict[str, str]) -> None:
        """
        Establece los textos de ayuda para los parámetros.
        
        Args:
            help_texts: Diccionario con los textos de ayuda para cada parámetro
        """
        self.logger.debug(f"Actualizando textos de ayuda para parámetros: {list(help_texts.keys())}")
        self.parameter_help.update(help_texts)

    def create_parameter_inputs(self, 
                              var_dict: Dict[str, tk.StringVar], 
                              on_slider_change: Callable[[str, float], None],
                              on_update_parameters: Callable[[], None],
                              on_reset_parameters: Callable[[], None],
                              on_save_as_default: Callable[[], None],
                              on_entry_validate: Callable[[str, str], None]) -> Dict[str, tk.Scale]:
        """
        Crea los controles de parámetros en la interfaz.
        
        Args:
            var_dict: Diccionario de variables tkinter para cada parámetro
            on_slider_change: Callback para cambios en sliders
            on_update_parameters: Callback para actualizar parámetros
            on_reset_parameters: Callback para restaurar valores predeterminados
            on_save_as_default: Callback para guardar como valores predeterminados
            on_entry_validate: Callback para validar entradas
            
        Returns:
            Diccionario de sliders creados
        """
        self.logger.debug("Creando controles de parámetros en la interfaz")
        self.logger.debug(f"Valores iniciales: {[(k, v.get()) for k, v in var_dict.items()]}")
        
        # Frame para instrucciones
        help_frame = tk.Frame(self.parent_frame)
        help_frame.pack(fill="x", padx=10, pady=5)

        help_text = "Ajuste los parámetros usando los controles deslizantes o ingresando valores directamente. " + \
                    "Pase el cursor sobre cada elemento para ver más información."
        help_label = tk.Label(help_frame, text=help_text, justify=tk.LEFT, wraplength=400,
                              font=('Helvetica', 9, 'italic'))
        help_label.pack(pady=5, anchor=tk.W)

        # Diccionario para almacenar referencias a los sliders
        sliders = {}
        
        # Sección para Grados de rotación
        _, rotation_slider = self._create_parameter_row(
            'grados_rotacion', 
            'Grados de rotación:', 
            lambda v: on_slider_change('grados_rotacion', v),
            var_dict['grados_rotacion'],
            on_entry_validate
        )
        sliders['grados_rotacion'] = rotation_slider

        # Sección para Píxeles por mm
        _, pixels_slider = self._create_parameter_row(
            'pixels_por_mm', 
            'Píxeles por mm:', 
            lambda v: on_slider_change('pixels_por_mm', v),
            var_dict['pixels_por_mm'],
            on_entry_validate
        )
        sliders['pixels_por_mm'] = pixels_slider

        # Sección para Altura (ajuste vertical)
        _, altura_slider = self._create_parameter_row(
            'altura', 
            'Altura (ajuste vertical):', 
            lambda v: on_slider_change('altura', v),
            var_dict['altura'],
            on_entry_validate
        )
        sliders['altura'] = altura_slider

        # Sección para desplazamiento horizontal
        _, horizontal_slider = self._create_parameter_row(
            'horizontal', 
            'Ajuste horizontal:', 
            lambda v: on_slider_change('horizontal', v),
            var_dict['horizontal'],
            on_entry_validate
        )
        sliders['horizontal'] = horizontal_slider

        # Frame para botones de acción
        buttons_frame = tk.Frame(self.parent_frame)
        buttons_frame.pack(fill="x", padx=10, pady=10)

        # Botón para actualizar todos los parámetros
        update_button = ttk.Button(
            buttons_frame, 
            text="Aplicar cambios", 
            command=on_update_parameters,
            style="Accent.TButton"
        )
        update_button.pack(side=tk.LEFT, padx=5, pady=5, fill="x", expand=True)
        self.tooltips.append(ToolTip(update_button, "Aplica todos los cambios de parámetros al procesamiento de video"))

        # Botón para restaurar valores predeterminados
        reset_button = ttk.Button(
            buttons_frame,
            text="Restaurar valores predeterminados",
            command=on_reset_parameters,
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
            command=on_save_as_default,
            style="Save.TButton"
        )
        save_default_button.pack(padx=5, pady=5, fill="x")
        self.tooltips.append(ToolTip(save_default_button, 
                              "Guarda los valores actuales como nuevos valores predeterminados para futuras sesiones"))
        
        self.logger.debug(f"Creados {len(sliders)} controles de parámetros")
        return sliders

    def _create_parameter_row(self, param_name: str, label_text: str, slider_callback: Callable, 
                             var: tk.StringVar, entry_validate_callback: Callable) -> Tuple[tk.Frame, tk.Scale]:
        """
        Crea una fila de controles para un parámetro (label, entry, slider, help button).
        
        Args:
            param_name: Nombre del parámetro (ej: 'grados_rotacion')
            label_text: Texto para la etiqueta del parámetro
            slider_callback: Función callback para el slider
            var: Variable StringVar para el valor del parámetro
            entry_validate_callback: Función para validar la entrada
            
        Returns:
            tuple: (frame, slider) - El frame contenedor y el slider creado
        """
        self.logger.debug(f"Creando controles para parámetro: {param_name}, valor actual: {var.get()}")
        
        # Wrapping callbacks para añadir logging
        def on_slider_change(value):
            self.logger.debug(f"Slider {param_name} ajustado a: {value}")
            return slider_callback(value)
        
        def on_entry_validate(param, value):
            self.logger.debug(f"Validando entrada para {param}: {value}")
            return entry_validate_callback(param, value)
            
        # Crear frame contenedor
        frame = tk.Frame(self.parent_frame)
        frame.pack(fill="x", padx=10, pady=5)

        # Crear etiqueta
        label = tk.Label(frame, text=label_text)
        label.grid(row=0, column=0, sticky="w", pady=2)
        self.tooltips.append(ToolTip(label, self.parameter_help[param_name]))

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
            'command': on_slider_change
        }

        # Añadir parámetro 'resolution' solo si es para pixels_por_mm
        if param_name == 'pixels_por_mm':
            slider_args['resolution'] = 0.1

        slider = tk.Scale(frame, **slider_args)
        try:
            current_value = float(var.get())
            slider.set(current_value)
            self.logger.debug(f"Slider {param_name} inicializado con valor: {current_value}")
        except (ValueError, TypeError):
            self.logger.warning(f"No se pudo convertir '{var.get()}' a float para el slider {param_name}")
            slider.set(0)  # Valor por defecto seguro
            
        slider.grid(row=0, column=2, padx=5, pady=2, sticky="w")

        # Añadir tooltip al slider
        slider_tooltip_text = f"Deslice para ajustar {label_text.lower().rstrip(':')}"
        self.tooltips.append(ToolTip(slider, slider_tooltip_text))

        # Crear botón de ayuda
        help_icon = self._create_help_button(frame, self.parameter_help[param_name])
        help_icon.grid(row=0, column=3, padx=5, pady=2)

        # Configurar validaciones para el entry
        entry.bind('<FocusOut>', lambda e, pn=param_name: on_entry_validate(pn, var.get()))
        
        # Aplicar cambios al presionar Enter
        entry.bind('<Return>', lambda e, pn=param_name: on_entry_validate(pn, var.get()))

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
        self.logger.debug(f"Mostrando ventana de ayuda con texto: {help_text[:20]}...")
        
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
