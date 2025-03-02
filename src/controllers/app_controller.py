"""
Path: src/controllers/app_controller.py
Controlador principal de la aplicación.
Implementa la lógica de negocio y coordina la vista y el modelo.
"""

import logging
from typing import Dict, Any, Optional
import json
import os
from src.views.gui_view import GUIView

class AppController:
    """Controlador principal de la aplicación."""

    def __init__(self, logger: logging.Logger):
        """
        Inicializa el controlador.
        
        Args:
            logger: Logger configurado para registrar eventos
        """
        self.logger = logger
        self.view: Optional[GUIView] = None
        self.config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                      'config', 'parameters.json')
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Carga la configuración desde el archivo JSON.
        
        Returns:
            Diccionario con la configuración
        """
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.error(f"Error al cargar configuración: {e}")
            # Valores predeterminados
            return {
                "video_source": 0,
                "parameters": {
                    "grados_rotacion": 0,
                    "pixels_por_mm": 10,
                    "altura": 0,
                    "horizontal": 0
                }
            }

    def _save_config(self, config: Dict[str, Any]) -> None:
        """
        Guarda la configuración en el archivo JSON.
        
        Args:
            config: Diccionario con la configuración a guardar
        """
        try:
            # Asegurar que existe el directorio
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)

            self.logger.info(f"Configuración guardada en {self.config_file}")
        except (IOError, OSError) as e:
            self.logger.error(f"Error al guardar configuración: {e}")

    def setup_view(self, view: GUIView) -> None:
        """
        Configura la vista y establece los callbacks necesarios.
        
        Args:
            view: Instancia de GUIView a configurar
        """
        self.view = view

        # Este es el paso clave - conectar el callback para actualizar parámetros
        self.view.set_parameters_update_callback(self.on_parameters_update)

        # Inicializar la interfaz con los valores de configuración
        video_source = self.config.get("video_source", 0)
        params = self.config.get("parameters", {})

        grados_rotacion = params.get("grados_rotacion", 0)
        pixels_por_mm = params.get("pixels_por_mm", 10)
        altura = params.get("altura", 0)
        horizontal = params.get("horizontal", 0)

        self.view.inicializar_ui(
            video_source,
            grados_rotacion,
            altura,
            horizontal,
            pixels_por_mm
        )

        self.logger.info("Vista configurada correctamente")

    def on_parameters_update(self, parameters: Dict[str, float]) -> None:
        """
        Callback que se llama cuando los parámetros se actualizan desde la GUI.
        
        Args:
            parameters: Diccionario con los nuevos valores de parámetros
        """
        self.logger.info(f"Actualización de parámetros recibida: {parameters}")

        # Comprobar si es una solicitud de reset
        if parameters.get('reset', False):
            self.logger.info("Solicitada restauración de valores predeterminados")
            params = self.config.get("parameters", {})

            # Actualizar la vista con los valores originales
            if self.view:
                self.view.update_parameters(params)
            return

        # Comprobar si es una solicitud para guardar como predeterminados
        if parameters.get('save_as_default', False):
            self.logger.info("Guardando valores actuales como predeterminados")

            # Eliminar la flag especial antes de guardar
            parameters.pop('save_as_default', None)

            # Actualizar la configuración
            self.config["parameters"] = parameters
            self._save_config(self.config)
            return

        # Actualizar la vista y el procesamiento con los nuevos valores
        # Esto es crucial: asegurarse de que los parámetros se apliquen al procesamiento
        if self.view:
            self.view.update_parameters(parameters)

    def run(self) -> None:
        """Inicia la ejecución de la aplicación."""
        if self.view:
            self.view.ejecutar()
        else:
            self.logger.error("No se puede ejecutar la aplicación sin una vista configurada")
