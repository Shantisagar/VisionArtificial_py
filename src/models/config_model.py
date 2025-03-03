"""
Path: src/models/config_model.py
Modelo para gestión de configuraciones de la aplicación.
Encargado de cargar y guardar parámetros de configuración.
"""

import json
import os
import logging
from typing import Dict, Any, Optional
from utils.logging.error_manager import handle_exception

class ConfigModel:
    """Clase responsable de gestionar la configuración de la aplicación."""

    def __init__(self, logger: logging.Logger, config_path: Optional[str] = None):
        """
        Inicializa el modelo de configuración.
        
        Args:
            logger: Logger configurado para registrar eventos
            config_path: Ruta al archivo de configuración (opcional)
        """
        self.logger = logger

        # Si no se especifica una ruta, usar la ruta predeterminada en el directorio config
        if config_path is None:
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.config_file = os.path.join(base_path, 'config', 'parameters.json')
        else:
            self.config_file = config_path

        self.logger.debug(
            f"ConfigModel inicializado con archivo de configuración: {self.config_file}"
        )
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.logger.debug(f"Ruta base del proyecto: {base_path}")
        self.logger.debug(f"Directorio actual de trabajo: {os.getcwd()}")

    def load_config(self) -> Dict[str, Any]:
        """
        Carga la configuración desde el archivo JSON.
        
        Returns:
            Diccionario con la configuración
        """
        self.logger.debug(f"Intentando cargar configuración desde: {self.config_file}")

        # Cargar el archivo de configuración
        raw_config = self._load_config_file()

        # Validar y completar la configuración
        validated_config = self._validate_and_complete_config(raw_config)

        self.logger.debug(f"Configuración final cargada: {validated_config}")
        return validated_config

    def _load_config_file(self) -> Dict[str, Any]:
        """
        Carga el archivo de configuración JSON.
        
        Returns:
            Configuración cargada o diccionario vacío si hay error
        """
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.logger.debug("Archivo de configuración abierto correctamente")
                config = json.load(f)
                self.logger.debug(f"Configuración cargada: {config}")
                self.logger.info(f"Configuración cargada desde {self.config_file}")
                return config
        except FileNotFoundError as e:
            self._handle_load_error(e, "archivo no encontrado")
            return {}
        except json.JSONDecodeError as e:
            self._handle_load_error(e, "formato JSON inválido",
                                  {"line": e.lineno, "column": e.colno})
            return {}
        except OSError as e:
            self._handle_load_error(e, "error inesperado")
            return {}

    def _handle_load_error(self, error: Exception, error_type: str,
                         extra_data: Dict[str, Any] = None) -> None:
        """
        Maneja los errores durante la carga de configuración.
        
        Args:
            error: La excepción que ocurrió
            error_type: Tipo de error para mensajes específicos
            extra_data: Datos adicionales para el contexto de error
        """
        self.logger.debug(f"Error al cargar configuración ({error_type}): {error}")

        # Preparar contexto para el gestor de errores
        context = {
            "component": "ConfigModel", 
            "method": "load_config",
            "filepath": self.config_file,
            "error_type": error_type
        }

        # Añadir datos adicionales si existen
        if extra_data:
            context.update(extra_data)

        # Registrar el error
        handle_exception(error, context)

        # Registrar mensaje adecuado según tipo de error
        if error_type == "archivo no encontrado":
            self.logger.warning(
                f"Archivo de configuración no encontrado: {self.config_file}. "
                "Se usarán valores predeterminados."
            )
        elif error_type == "formato JSON inválido":
            self.logger.error(f"Error al decodificar el archivo de configuración: {error}")
        else:
            self.logger.error(f"Error inesperado al cargar la configuración: {error}")

    def _validate_and_complete_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida y completa la configuración con valores predeterminados si es necesario.
        
        Args:
            config: Configuración cargada del archivo
            
        Returns:
            Configuración validada y completada
        """
        # Si no hay configuración o está vacía, usar la predeterminada
        if not config:
            self.logger.warning("Configuración vacía o no cargada, usando valores predeterminados")
            return self._get_default_config()

        default_config = self._get_default_config()

        # Asegurar que exista la clave video_source
        if "video_source" not in config:
            self.logger.warning("Clave 'video_source' no encontrada, usando valor predeterminado")
            config["video_source"] = default_config["video_source"]

        # Asegurar que exista la clave parameters y sea del tipo correcto
        if "parameters" not in config or not isinstance(config["parameters"], dict):
            self.logger.warning(
                "Clave 'parameters' no encontrada o inválida, usando valores predeterminados"
            )
            config["parameters"] = default_config["parameters"]
        else:
            # Completar parámetros faltantes
            for key, value in default_config["parameters"].items():
                if key not in config["parameters"]:
                    self.logger.warning(
                        f"Parámetro '{key}' no encontrado, usando valor predeterminado"
                    )
                    config["parameters"][key] = value

        return config

    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        Guarda la configuración en el archivo JSON.
        
        Args:
            config: Diccionario con la configuración a guardar
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        self.logger.debug(f"Intentando guardar configuración: {config}")

        # Validar la configuración antes de guardar
        if not self._validate_config(config):
            self.logger.error("La configuración no es válida, no se guardará")
            return False

        # Asegurar que existe el directorio
        if not self._ensure_config_directory_exists():
            return False

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.logger.debug("Archivo abierto para escritura")
                json.dump(config, f, indent=4)
                self.logger.debug("Configuración escrita correctamente")

            self.logger.info(f"Configuración guardada en {self.config_file}")
            return True
        except (IOError, OSError) as e:
            self._handle_save_error(e, config)
            return False

    def _handle_save_error(self, error: Exception, config: Dict[str, Any]) -> None:
        """
        Maneja los errores durante el guardado de configuración.
        
        Args:
            error: La excepción que ocurrió
            config: La configuración que se estaba intentando guardar
        """
        self.logger.debug(f"Excepción al guardar: {type(error).__name__}, {str(error)}")
        handle_exception(error, {
            "component": "ConfigModel", 
            "method": "save_config",
            "filepath": self.config_file,
            "config_keys": list(config.keys())
        })
        self.logger.error(f"Error al guardar configuración: {error}")

    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Valida que la configuración tenga el formato correcto.
        
        Args:
            config: Configuración a validar
            
        Returns:
            bool: True si la configuración es válida, False en caso contrario
        """
        if not isinstance(config, dict):
            self.logger.error(f"La configuración debe ser un diccionario, no {type(config)}")
            return False

        # Validar que contiene las claves requeridas
        required_keys = ["video_source", "parameters"]
        for key in required_keys:
            if key not in config:
                self.logger.error(f"Falta la clave '{key}' en la configuración")
                return False

        # Validar que parameters es un diccionario
        if not isinstance(config.get("parameters", {}), dict):
            self.logger.error("El campo 'parameters' debe ser un diccionario")
            return False

        return True

    def _ensure_config_directory_exists(self) -> bool:
        """
        Asegura que el directorio de configuración exista.
        
        Returns:
            True si el directorio existe o se creó correctamente, False en caso contrario
        """
        config_dir = os.path.dirname(self.config_file)
        self.logger.debug(f"Verificando directorio de configuración: {config_dir}")
        try:
            os.makedirs(config_dir, exist_ok=True)
            self.logger.debug("Directorio confirmado")
            return True
        except (IOError, OSError) as e:
            self.logger.error(f"Error al crear directorio de configuración: {e}")
            handle_exception(e, {
                "component": "ConfigModel", 
                "method": "_ensure_config_directory_exists",
                "directory": config_dir
            })
            return False

    def _get_default_config(self) -> Dict[str, Any]:
        """
        Retorna la configuración predeterminada.
        
        Returns:
            Diccionario con la configuración predeterminada
        """
        default_config = {
            "video_source": 0,
            "parameters": {
                "grados_rotacion": 0,
                "pixels_por_mm": 10,
                "altura": 0,
                "horizontal": 0
            }
        }
        self.logger.debug(f"Generando configuración predeterminada: {default_config}")
        self.logger.info("Usando configuración predeterminada")
        return default_config

    def get_parameters(self) -> Dict[str, Any]:
        """
        Obtiene los parámetros de la configuración.
        
        Returns:
            Diccionario con los parámetros
        """
        self.logger.debug("Solicitando parámetros de configuración")
        config = self.load_config()
        parameters = config.get("parameters", self._get_default_config()["parameters"])
        self.logger.debug(f"Parámetros obtenidos: {parameters}")
        return parameters

    def get_video_source(self) -> Any:
        """
        Obtiene la fuente de video de la configuración.
        
        Returns:
            Índice o URL de la fuente de video
        """
        self.logger.debug("Solicitando fuente de video")
        config = self.load_config()
        video_source = config.get("video_source", self._get_default_config()["video_source"])
        self.logger.debug(f"Fuente de video: {video_source}")
        return video_source
