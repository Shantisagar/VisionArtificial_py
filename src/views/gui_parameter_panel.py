"""
Path: src/views/gui_parameter_panel.py
Panel para manejar los parámetros de configuración en la interfaz gráfica.
Extrae la responsabilidad de gestión de parámetros de GUIView.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Callable, Tuple, List, Optional

from src.views.tool_tip import ToolTip

class GUIParameterPanel:
    """Clase responsable de la gestión de los parámetros en la interfaz gráfica."""

    def __init__(self, parent_frame: tk.Frame, logger: logging.Logger):
        """
        Inicializa el panel de parámetros.
        
        Args:
            parent_frame: Frame padre donde se crearán los controles
            logger: Logger configurado para registrar eventos
        """
        self.parent_frame = parent_frame
        self.logger = logger

        # Callback para cuando se actualicen los parámetros
        self.on_parameters_update: Optional[Callable[[Dict[str, float]], None]] = None

        # Campos para los parámetros de configuración
        self.grados_rotacion_var = tk.StringVar()
        self.pixels_por_mm_var = tk.StringVar()
        self.altura_var = tk.StringVar()
        self.horizontal_var = tk.StringVar()

        # Referencias a los sliders
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

        # Variables para controlar si el cambio viene del slider o del campo de texto
        self.updating_from_slider = False
        self.updating_from_entry = False

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

        # Notificador para mensajes de error/información (se establecerá desde fuera)
        self.notifier = None

    def set_notifier(self, notifier) -> None:
        """
        Establece el notificador para mensajes de error/información.
        
        Args:
            notifier: Objeto notificador que implementa métodos notify_error y notify_info
        """
        self.notifier = notifier

    def set_parameters_update_callback(self, callback: Callable[[Dict[str, float]], None]) -> None:
        """
        Establece el callback que se llamará cuando los parámetros se actualicen.
        
        Args:
            callback: Función a llamar con los nuevos parámetros
        """
        self.on_parameters_update = callback

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
            self._on_rotation_slider_change
        )
        self.rotation_slider = rotation_slider

        # Sección para Píxeles por mm
        _, pixels_slider = self._create_parameter_row(
            'pixels_por_mm', 
            'Píxeles por mm:', 
            self._on_pixels_slider_change
        )
        self.pixels_slider = pixels_slider

        # Sección para Altura (ajuste vertical)
        _, altura_slider = self._create_parameter_row(
            'altura', 
            'Altura (ajuste vertical):', 
            self._on_altura_slider_change
        )
        self.altura_slider = altura_slider

        # Sección para desplazamiento horizontal
        _, horizontal_slider = self._create_parameter_row(
            'horizontal', 
            'Ajuste horizontal:', 
            self._on_horizontal_slider_change
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
        entry.bind('<FocusOut>', lambda e, pn=param_name: self._validate_and_update_from_entry(pn))
        entry.bind('<Return>', lambda e, pn=param_name: self._validate_and_update_from_entry(pn))

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

    def _on_slider_change(self, param_name: str, value: str) -> None:
        """
        Método centralizado para manejar cambios en cualquier slider.
        
        Args:
            param_name: Nombre del parámetro asociado al slider
            value: Nuevo valor del slider
        """
        if self.updating_from_entry:
            return

        try:
            self.updating_from_slider = True

            # Actualizar la variable StringVar correspondiente
            if param_name == 'grados_rotacion':
                self.grados_rotacion_var.set(value)
            elif param_name == 'pixels_por_mm':
                self.pixels_por_mm_var.set(value)
            elif param_name == 'altura':
                self.altura_var.set(value)
            elif param_name == 'horizontal':
                self.horizontal_var.set(value)

            self.updating_from_slider = False

            # Actualizar el parámetro en el modelo y procesamiento
            self._update_parameter(param_name, float(value))

        except ValueError as e:
            self.logger.error(f"Error de valor al actualizar desde slider {param_name}: {e}")
            self.updating_from_slider = False
        except TypeError as e:
            self.logger.error(f"Error de tipo al actualizar desde slider {param_name}: {e}")
            self.updating_from_slider = False
    
    def _on_rotation_slider_change(self, value: str) -> None:
        """Maneja el cambio en el slider de rotación"""
        self._on_slider_change('grados_rotacion', value)
            
    def _on_pixels_slider_change(self, value: str) -> None:
        """Maneja el cambio en el slider de píxeles por mm"""
        self._on_slider_change('pixels_por_mm', value)
            
    def _on_altura_slider_change(self, value: str) -> None:
        """Maneja el cambio en el slider de altura"""
        self._on_slider_change('altura', value)
            
    def _on_horizontal_slider_change(self, value: str) -> None:
        """Maneja el cambio en el slider de ajuste horizontal"""
        self._on_slider_change('horizontal', value)
            
    def _validate_parameter(self, param_name: str, value: str) -> Tuple[bool, Optional[str]]:
        """
        Valida un parámetro según sus rangos permitidos.
        
        Args:
            param_name: Nombre del parámetro a validar
            value: Valor a validar
            
        Returns:
            tuple: (es_válido, mensaje_error)
        """
        try:
            # Convertir a float para validación numérica
            float_value = float(value)
            
            # Validar según el tipo de parámetro y su rango
            if param_name in self.slider_ranges:
                min_val, max_val = self.slider_ranges[param_name]
                
                if min_val <= float_value <= max_val:
                    return True, None
                else:
                    return False, f"Valor fuera de rango ({min_val} a {max_val})"
            else:
                return False, f"Parámetro '{param_name}' no reconocido"
                
        except ValueError:
            return False, "Valor no válido. Debe ser un número."
    
    def _validate_and_update_from_entry(self, param_name: str) -> None:
        """
        Valida el valor introducido en un campo de entrada y actualiza el slider correspondiente.
        
        Args:
            param_name: Nombre del parámetro a validar
        """
        if self.updating_from_slider:
            return
            
        try:
            self.updating_from_entry = True
            
            # Obtener el valor según el parámetro
            if param_name == 'grados_rotacion':
                value = self.grados_rotacion_var.get()
            elif param_name == 'pixels_por_mm':
                value = self.pixels_por_mm_var.get()
            elif param_name == 'altura':
                value = self.altura_var.get()
            elif param_name == 'horizontal':
                value = self.horizontal_var.get()
            else:
                self.updating_from_entry = False
                return
            
            # Validar el valor
            is_valid, error_msg = self._validate_parameter(param_name, value)
            
            if is_valid:
                # Convertir a float para las operaciones
                float_value = float(value)
                
                # Actualizar el slider correspondiente
                self._update_slider_from_entry(param_name, float_value)
                self._update_parameter(param_name, float_value)
                
            else:
                # Restaurar valor anterior y mostrar error
                self._restore_previous_value(param_name)
                if self.notifier:
                    self.notifier.notify_error(error_msg)
                
        except (ValueError, TypeError) as e:
            self.logger.error(f"Error al validar parámetro {param_name}: {e}")
            # Si hay un error de formato, restaurar el valor anterior
            self._restore_previous_value(param_name)
            
            if self.notifier:
                self.notifier.notify_error(f"Error al validar: {str(e)}")
            
        finally:
            self.updating_from_entry = False
            
    def _restore_previous_value(self, param_name: str) -> None:
        """
        Restaura el valor anterior de un parámetro desde su slider.
        
        Args:
            param_name: Nombre del parámetro a restaurar
        """
        if param_name == 'grados_rotacion' and hasattr(self, 'rotation_slider'):
            self.grados_rotacion_var.set(str(self.rotation_slider.get()))
        elif param_name == 'pixels_por_mm' and hasattr(self, 'pixels_slider'):
            self.pixels_por_mm_var.set(str(self.pixels_slider.get()))
        elif param_name == 'altura' and hasattr(self, 'altura_slider'):
            self.altura_var.set(str(self.altura_slider.get()))
        elif param_name == 'horizontal' and hasattr(self, 'horizontal_slider'):
            self.horizontal_var.set(str(self.horizontal_slider.get()))
    
    def _update_slider_from_entry(self, param_name: str, value: float) -> None:
        """
        Actualiza el slider correspondiente con el valor de entrada validado.
        
        Args:
            param_name: Nombre del parámetro
            value: Valor validado a establecer en el slider
        """
        try:
            if param_name == 'grados_rotacion' and hasattr(self, 'rotation_slider'):
                self.rotation_slider.set(value)
            elif param_name == 'pixels_por_mm' and hasattr(self, 'pixels_slider'):
                self.pixels_slider.set(value)
            elif param_name == 'altura' and hasattr(self, 'altura_slider'):
                self.altura_slider.set(value)
            elif param_name == 'horizontal' and hasattr(self, 'horizontal_slider'):
                self.horizontal_slider.set(value)
        except (ValueError, TypeError) as e:
            self.logger.error(f"Error al actualizar slider {param_name}: {e}")
    
    def _update_parameter(self, param_name: str, value: float) -> None:
        """
        Actualiza un parámetro individual y envía la actualización si hay un callback configurado.
        
        Args:
            param_name: Nombre del parámetro
            value: Nuevo valor
        """
        # Si hay un callback configurado, actualizamos
        if self.on_parameters_update:
            current_params = self.get_current_parameters()
            if current_params:
                current_params[param_name] = value  # Actualizar solo el parámetro cambiado
                self.on_parameters_update(current_params)
                
    def _on_update_parameters(self) -> None:
        """Maneja el evento del botón de actualización de todos los parámetros"""
        try:
            # Obtener y validar los valores
            params = self.get_current_parameters()
            
            # Si hay un callback configurado, llamarlo con los nuevos parámetros
            if self.on_parameters_update and params:
                self.logger.info(f"Enviando actualización de parámetros desde panel: {params}")
                self.on_parameters_update(params)
                if self.notifier:
                    self.notifier.notify_info("Todos los parámetros actualizados correctamente")
            else:
                if not self.on_parameters_update:
                    self.logger.error("No hay callback configurado para actualización de parámetros")
                self.logger.warning("No se pudieron actualizar los parámetros - callback no configurado o parámetros inválidos")
                if self.notifier:
                    self.notifier.notify_error("No se pudieron aplicar los cambios")
            
        except ValueError as e:
            self.logger.error(f"Error en los parámetros: {str(e)}")
            if self.notifier:
                self.notifier.notify_error(f"Error en los parámetros: {str(e)}")
                
    def _on_reset_parameters(self) -> None:
        """Restaura los valores predeterminados de los parámetros"""
        try:
            # Solicitar valores predeterminados al controlador
            if self.notifier:
                self.notifier.notify_info("Restaurando valores predeterminados...")
                
            # Solicitar valores predeterminados al controlador
            if self.on_parameters_update:
                self.on_parameters_update({'reset': True})
                
        except (ValueError, TypeError) as e:
            if self.notifier:
                self.notifier.notify_error(f"Error al restaurar valores predeterminados: {str(e)}")
                
    def _on_save_as_default(self) -> None:
        """Guarda los valores actuales como nuevos valores predeterminados"""
        try:
            # Obtener y validar los valores
            params = self.get_current_parameters()
            
            if params:
                # Si hay un callback configurado, llamarlo con los nuevos parámetros y una flag especial
                if self.on_parameters_update:
                    params['save_as_default'] = True  # Flag especial para indicar guardar como predeterminados
                    self.on_parameters_update(params)
                    if self.notifier:
                        self.notifier.notify_info("Valores guardados como nuevos valores predeterminados")
                
        except ValueError as e:
            if self.notifier:
                self.notifier.notify_error(f"Error al guardar valores predeterminados: {str(e)}")
    
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
        Actualiza los valores de los parámetros en la interfaz.
        
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
                
        # Notificar sobre la actualización
        if self.notifier:
            self.notifier.notify_info("Parámetros actualizados correctamente")
