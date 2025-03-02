"""
Path: src/views/gui_parameter_panel_view.py
Vista para el panel de parámetros de configuración en la interfaz gráfica.
Se encarga exclusivamente de la creación y gestión de componentes visuales.
"""

import tkinter as tk
import logging
from typing import Dict, Callable, Tuple, List, Optional, Any

from src.views.tool_tip import ToolTip
from src.views.parameter_panel_layout import ParameterPanelLayout

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
        self.zoom_var = tk.DoubleVar(value=1.0)
        self.paper_color_var = tk.StringVar(value="Blanco")

        # Referencias a los controles de la UI
        self.zoom_scale = None
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

        # Selector de color de papel
        self.paper_color_menu = tk.OptionMenu(
            self.parent_frame,
            self.paper_color_var,
            "Blanco", 
            "Marrón"
        )

        # Objeto de layout para la construcción de la UI
        self.layout_manager = ParameterPanelLayout(parent_frame, logger)

        # Lista para almacenar referencias a tooltips
        self.tooltips: List[ToolTip] = []
        self.apply_button = None  # Added to fix attribute-defined-outside-init warning

        # Callbacks para cuando los controles cambien
        self.on_slider_change_callback: Optional[Callable[[str, float], None]] = None
        self.on_update_parameters_callback: Optional[Callable[[], None]] = None
        self.on_reset_parameters_callback: Optional[Callable[[], None]] = None
        self.on_save_as_default_callback: Optional[Callable[[], None]] = None
        self.on_entry_validate_callback: Optional[
            Callable[[str, str], Tuple[bool, Optional[str]]]
        ] = None

    def set_callbacks(self,
                      on_slider_change: Optional[Callable[[str, float], None]] = None,
                      on_update_parameters: Optional[Callable[[], None]] = None,
                      on_reset_parameters: Optional[Callable[[], None]] = None,
                      on_save_as_default: Optional[Callable[[], None]] = None,
                      on_entry_validate: Optional[
                          Callable[[str, str], Tuple[bool, Optional[str]]]
                      ] = None) -> None:
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

    def initialize(self,
                   grados_rotacion: float,
                   pixels_por_mm: float,
                   altura: float,
                   horizontal: float) -> None:
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

        # Configurar el layout manager con los rangos de sliders
        self.layout_manager.set_slider_ranges(self.slider_ranges)

        # Crear los controles en la interfaz
        self._create_parameter_inputs()
        self.logger.info("Panel de parámetros inicializado correctamente")
        tk.Label(self.parent_frame, text="Color de Papel").pack()
        self.paper_color_menu = tk.OptionMenu(
            self.parent_frame,
            self.paper_color_var,
            "Blanco", 
            "Marrón"
        )
        self.paper_color_menu.pack()
        self.zoom_scale = tk.Scale(
            self.parent_frame,
            from_=0.1,
            to=3.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.zoom_var
        )
        self.zoom_scale.pack()
        self.zoom_scale.pack()

        # Selector de color de papel
        tk.Label(self.parent_frame, text="Color de Papel").pack()
        self.paper_color_menu = tk.OptionMenu(
            self.parent_frame,
            self.paper_color_var,
            "Blanco", 
            "Marrón"
        )
        self.paper_color_menu.pack()

        # Botón para aplicar cambios
        self.apply_button = tk.Button(
            self.parent_frame, text="Aplicar Cambios", command=self.apply_changes
        )
        self.apply_button.pack()

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

    def update_parameter_text(self, param_name: str, value: str) -> None:
        """
        Actualiza solo el texto de un parámetro específico.
        
        Args:
            param_name: Nombre del parámetro a actualizar
            value: Nuevo valor como string
        """
        var = getattr(self, f"{param_name}_var", None)
        if var:
            var.set(value)

    def update_slider_value(self, param_name: str, value: float) -> None:
        """
        Actualiza el valor de un slider específico.
        
        Args:
            param_name: Nombre del parámetro asociado al slider
            value: Nuevo valor para el slider
        """
        slider = None
        if param_name == 'grados_rotacion' and self.rotation_slider:
            slider = self.rotation_slider
        elif param_name == 'pixels_por_mm' and self.pixels_slider:
            slider = self.pixels_slider
        elif param_name == 'altura' and self.altura_slider:
            slider = self.altura_slider
        elif param_name == 'horizontal' and self.horizontal_slider:
            slider = self.horizontal_slider

        if slider:
            slider.set(value)

    def _create_parameter_inputs(self) -> None:
        """Crea los campos de entrada y sliders para los parámetros en el frame especificado."""
        # Crear un diccionario con las variables StringVar para cada parámetro
        var_dict = {
            'grados_rotacion': self.grados_rotacion_var,
            'pixels_por_mm': self.pixels_por_mm_var,
            'altura': self.altura_var,
            'horizontal': self.horizontal_var
        }

        # Delegar la creación de la UI al layout manager
        sliders = self.layout_manager.create_parameter_inputs(
            var_dict,
            self._on_slider_change,
            self._on_update_parameters,
            self._on_reset_parameters,
            self._on_save_as_default,
            self._validate_entry
        )

        # Almacenar referencias a los sliders
        self.rotation_slider = sliders['grados_rotacion']
        self.pixels_slider = sliders['pixels_por_mm']
        self.altura_slider = sliders['altura']
        self.horizontal_slider = sliders['horizontal']

        # Copiar los tooltips creados en el layout manager
        self.tooltips.extend(self.layout_manager.tooltips)

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

    def _validate_entry(self, param_name: str, value: str) -> None:
        """
        Valida el valor ingresado en un campo de entrada.
        
        Args:
            param_name: Nombre del parámetro a validar
            value: Valor a validar
        """
        if self.on_entry_validate_callback:
            is_valid, error_message = self.on_entry_validate_callback(param_name, value)

            # Si hay un mensaje de error, mostrar retroalimentación al usuario
            if not is_valid and error_message:
                self.logger.warning(f"Valor inválido en {param_name}: {error_message}")
                # Como mejora futura: Mostrar el mensaje de error visualmente al usuario

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

    def apply_changes(self):
        """Aplica los cambios de parámetros y llama al callback correspondiente."""
        parameters = {
            'grados_rotacion': self.grados_rotacion_var.get(),
            'pixels_por_mm': self.pixels_por_mm_var.get(),
            'altura': self.altura_var.get(),
            'horizontal': self.horizontal_var.get(),
            'zoom': self.zoom_var.get(),
            'paper_color': self.paper_color_var.get()
        }
        if self.on_update_parameters_callback:
            self.on_update_parameters_callback(parameters)
