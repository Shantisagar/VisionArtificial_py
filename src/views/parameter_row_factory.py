"""
Path: src/views/parameter_row_factory.py
Clase responsable de crear filas individuales de parámetros para el panel de configuración.
"""

import tkinter as tk
import logging
from typing import Dict, Callable, Tuple, List

# Importamos ToolTip con ruta relativa en lugar de absoluta
from .tool_tip import ToolTip

# pylint: disable=too-many-arguments, too-many-locals, too-many-positional-arguments

class ParameterRowFactory:
    """
    Clase responsable de la creación de filas de parámetros individuales 
    con sus widgets y configuración.
    Sigue el patrón Factory para encapsular la lógica de creación de componentes UI complejos.
    """

    def __init__(self, logger: logging.Logger):
        """
        Inicializa el factory con configuraciones necesarias.
        
        Args:
            logger: Logger configurado para registrar eventos
        """
        self.logger = logger
        self.tooltips: List[ToolTip] = []

        # Descripciones de ayuda para los parámetros
        self.parameter_help = {
            'grados_rotacion': (
            "Ajusta la rotación de la imagen en grados. Valores positivos rotan en "
            "sentido horario, negativos en sentido antihorario."
            ),
            'pixels_por_mm': (
            "Define la escala de conversión de píxeles a milímetros. A mayor valor, "
            "mayor precisión en la medición de distancias."
            ),
            'altura': (
            "Ajusta la posición vertical de la línea de referencia en la imagen. "
            "Valores positivos mueven hacia abajo, negativos hacia arriba."
            ),
            'horizontal': (
            "Ajusta la posición horizontal de la línea de referencia en la imagen. "
            "Valores positivos mueven hacia la derecha, negativos hacia la izquierda."
            )
        }

    def set_parameter_help(self, help_texts: Dict[str, str]) -> None:
        """
        Establece los textos de ayuda para los parámetros.
        
        Args:
            help_texts: Diccionario con los textos de ayuda para cada parámetro
        """
        self.logger.debug(
            f"Actualizando textos de ayuda para parámetros: {list(help_texts.keys())}"
        )
        self.parameter_help.update(help_texts)

    def create_parameter_row(self,
                           parent: tk.Widget,
                           param_name: str,
                           label_text: str,
                           slider_callback: Callable,
                           var: tk.StringVar,
                           entry_validate_callback: Callable,
                           slider_range: Tuple[float, float]) -> Tuple[tk.Frame, tk.Scale]:
        """
        Crea una fila de controles para un parámetro (label, entry, slider, help button).
        
        Args:
            parent: Widget padre donde se creará la fila
            param_name: Nombre del parámetro (ej: 'grados_rotacion')
            label_text: Texto para la etiqueta del parámetro
            slider_callback: Función callback para el slider
            var: Variable StringVar para el valor del parámetro
            entry_validate_callback: Función para validar la entrada
            slider_range: Rango (mínimo, máximo) para el slider
            
        Returns:
            tuple: (frame, slider) - El frame contenedor y el slider creado
        """
        self.logger.debug(
            f"Creando controles para parámetro: {param_name}, valor actual: {var.get()}"
        )

        # Wrapping callbacks para añadir logging
        def on_slider_change(value):
            self.logger.debug(f"Slider {param_name} ajustado a: {value}")
            return slider_callback(value)

        def on_entry_validate(param, value):
            self.logger.debug(f"Validando entrada para {param}: {value}")
            return entry_validate_callback(param, value)

        # Crear frame contenedor
        frame = tk.Frame(parent)
        frame.pack(fill="x", padx=10, pady=5)

        # Crear etiqueta
        label = tk.Label(frame, text=label_text)
        label.grid(row=0, column=0, sticky="w", pady=2)
        self.tooltips.append(ToolTip(label, self.parameter_help.get(param_name, "")))

        # Crear entry
        entry = tk.Entry(frame, textvariable=var, width=10)
        entry.grid(row=0, column=1, padx=5, pady=2)
        tooltip_text = f"Ingrese un valor entre {slider_range[0]} y {slider_range[1]}"
        self.tooltips.append(ToolTip(entry, tooltip_text))

        # Crear slider
        slider_args = {
            'from_': slider_range[0],
            'to': slider_range[1],
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
            self.logger.warning(
                f"No se pudo convertir '{var.get()}' a float para el slider {param_name}"
            )
            slider.set(0)  # Valor por defecto seguro

        slider.grid(row=0, column=2, padx=5, pady=2, sticky="w")

        # Añadir tooltip al slider
        slider_tooltip_text = f"Deslice para ajustar {label_text.lower().rstrip(':')}"
        self.tooltips.append(ToolTip(slider, slider_tooltip_text))

        # Crear botón de ayuda
        help_icon = self._create_help_button(frame, self.parameter_help.get(param_name, ""))
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
        help_button.bind("<Button-1>", lambda e: self._show_help_window(parent, help_text))

        return help_button

    def _show_help_window(self, parent: tk.Widget, help_text: str) -> None:
        """
        Muestra una ventana emergente con información de ayuda.
        
        Args:
            parent: Widget desde el cual obtener la ventana raíz.
            help_text: Texto de ayuda a mostrar
        """
        self.logger.debug(f"Mostrando ventana de ayuda con texto: {help_text[:20]}...")
        root = parent.winfo_toplevel()

        help_window = tk.Toplevel(root)
        help_window.title("Ayuda")
        help_window.geometry("300x150")
        help_window.resizable(False, False)
        help_window.transient(root)
        help_window.grab_set()

        # Texto de ayuda
        help_label = tk.Label(
            help_window,
            text=help_text,
            wraplength=280,
            justify=tk.LEFT,
            padx=10,
            pady=10
        )
        help_label.pack(fill=tk.BOTH, expand=True)

        # Botón para cerrar
        close_button = tk.Button(help_window, text="Cerrar", command=help_window.destroy)
        close_button.pack(pady=10)

    def get_tooltips(self) -> List[ToolTip]:
        """
        Obtiene los tooltips creados por el factory.
        
        Returns:
            Lista de tooltips creados
        """
        return self.tooltips
