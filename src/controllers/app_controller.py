"""
Path: src/controllers/app_controller.py
Controlador principal de la aplicación.
Implementa la lógica de negocio y coordina la vista y el modelo.
"""

import logging
from typing import Dict, Optional
from src.views.gui_view import GUIView
from src.models.config_model import ConfigModel

class AppController:
    """Controlador principal de la aplicación."""

    def __init__(self, logger: logging.Logger):
        """
        Inicializa el controlador.
        
        Args:
            logger: Logger configurado para registrar eventos
        """
        self.logger = logger
        self.logger.debug("Inicializando AppController")
        self.view: Optional[GUIView] = None

        # Usar el nuevo modelo de configuración en lugar de manipular directamente los archivos
        self.logger.debug("Creando instancia de ConfigModel")
        self.config_model = ConfigModel(logger)
        
        self.logger.debug("Cargando configuración inicial")
        self.config = self.config_model.load_config()
        self.logger.debug(f"Configuración inicial cargada: {self.config}")

    def setup_view(self, view: GUIView) -> None:
        """
        Configura la vista y establece los callbacks necesarios.
        
        Args:
            view: Instancia de GUIView a configurar
        """
        self.logger.debug(f"Configurando vista: {view.__class__.__name__}")
        self.view = view

        # Este es el paso clave - conectar el callback para actualizar parámetros
        self.logger.debug("Conectando callback para actualización de parámetros")
        self.view.set_parameters_update_callback(self.on_parameters_update)
        self.logger.debug("Callback conectado correctamente")

        # Inicializar la interfaz con los valores de configuración
        video_source = self.config.get("video_source", 0)
        params = self.config.get("parameters", {})

        grados_rotacion = params.get("grados_rotacion", 0)
        pixels_por_mm = params.get("pixels_por_mm", 10)
        altura = params.get("altura", 0)
        horizontal = params.get("horizontal", 0)

        self.logger.debug(
            f"Inicializando UI con: video={video_source}, rotación={grados_rotacion}, "
            f"píxeles/mm={pixels_por_mm}, altura={altura}, horizontal={horizontal}"
        )
        
        self.logger.debug("Llamando a inicializar_ui en la vista")
        self.view.inicializar_ui(
            video_source,
            grados_rotacion,
            altura,
            horizontal,
            pixels_por_mm
        )
        self.logger.debug("Vista inicializada correctamente")

        self.logger.info("Vista configurada correctamente")
        self.logger.debug("Proceso de setup_view completado")

    def on_parameters_update(self, parameters: Dict[str, float]) -> None:
        """
        Callback que se llama cuando los parámetros se actualizan desde la GUI.
        
        Args:
            parameters: Diccionario con los nuevos valores de parámetros
        """
        self.logger.info(f"Actualización de parámetros recibida: {parameters}")
        self.logger.debug(f"Estado actual de parámetros antes de actualizar: {self.config.get('parameters', {})}")

        # Comprobar si es una solicitud de reset
        if parameters.get('reset', False):
            self.logger.debug("Detectada bandera 'reset' - restaurando valores predeterminados")
            self.logger.info("Solicitada restauración de valores predeterminados")
            params = self.config.get("parameters", {})
            self.logger.debug(f"Valores a restaurar: {params}")

            # Actualizar la vista con los valores originales
            if self.view:
                self.logger.debug("Actualizando vista con valores predeterminados")
                self.view.update_parameters(params)
                self.logger.debug("Vista actualizada con valores predeterminados")
            return

        # Comprobar si es una solicitud para guardar como predeterminados
        if parameters.get('save_as_default', False):
            self.logger.debug("Detectada bandera 'save_as_default' - guardando configuración")
            self.logger.info("Guardando valores actuales como predeterminados")

            # Eliminar la flag especial antes de guardar
            clean_params = parameters.copy()
            clean_params.pop('save_as_default', None)
            self.logger.debug(f"Parámetros limpios para guardar: {clean_params}")

            # Actualizar la configuración utilizando el modelo
            old_params = self.config.get("parameters", {})
            self.config["parameters"] = clean_params
            self.logger.debug(f"Configuración actualizada: {old_params} -> {clean_params}")
            
            save_success = self.config_model.save_config(self.config)
            self.logger.debug(f"Resultado de guardar configuración: {'éxito' if save_success else 'fallo'}")
            if save_success:
                self.logger.info("Configuración guardada correctamente como predeterminada")
            else:
                self.logger.warning("No se pudo guardar la configuración como predeterminada")
            return

        # Actualizar la vista y el procesamiento con los nuevos valores
        # Esto es crucial: asegurarse de que los parámetros se apliquen al procesamiento
        if self.view:
            self.logger.debug(f"Actualizando vista con nuevos parámetros: {parameters}")
            self.view.update_parameters(parameters)
            self.logger.debug("Vista actualizada con nuevos parámetros")
        else:
            self.logger.error("No se puede actualizar la vista - no está inicializada")
            self.logger.debug("Error: intento de actualizar parámetros en vista no inicializada")

    def run(self) -> None:
        """Inicia la ejecución de la aplicación."""
        self.logger.debug("Iniciando ejecución de la aplicación")
        if self.view:
            self.logger.debug("Llamando a ejecutar() en la vista")
            self.view.ejecutar()
            self.logger.debug("La vista ha terminado de ejecutarse")
        else:
            self.logger.error("No se puede ejecutar la aplicación sin una vista configurada")
            self.logger.debug("Error crítico: intento de ejecutar sin vista configurada")
