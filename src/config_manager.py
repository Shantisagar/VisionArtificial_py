"""
Gestor de configuración con soporte para múltiples fuentes y acceso unificado.
Implementa principios SOLID mediante inyección de dependencias.
"""

import json
import os
import logging
from typing import Dict, Any, Optional
from utils.logging.logger_configurator import get_logger

class ConfigManager:
    """
    Gestor de configuración que permite trabajar con múltiples fuentes
    y provee una interfaz unificada para acceder a la configuración.
    """

    def __init__(self, config_data: Optional[Dict[str, Any]] = None,
                 config_path: Optional[str] = None,
                 logger: Optional[logging.Logger] = None):
        """
        Inicializa el gestor de configuración con datos o ruta especificados.
        
        Args:
            config_data: Diccionario de configuración predefinido o None
            config_path: Ruta al archivo de configuración o None
            logger: Logger a utilizar (inyección de dependencia) o None para usar el global
        """
        self.logger = logger or get_logger()
        self.config_path = config_path
        self._config = config_data or {}

        # Cargar configuración desde archivo si se proporciona una ruta
        if config_path and not config_data:
            self._load_config()

    @classmethod
    def from_file(cls, file_path: str,
                 logger: Optional[logging.Logger] = None) -> 'ConfigManager':
        """
        Crea un ConfigManager con una fuente de archivo.
        
        Args:
            file_path: Ruta al archivo de configuración
            logger: Logger a utilizar (opcional)
            
        Returns:
            Una instancia de ConfigManager configurada
        """
        return cls(config_path=file_path, logger=logger)

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any],
                 logger: Optional[logging.Logger] = None) -> 'ConfigManager':
        """
        Crea un ConfigManager con un diccionario predefinido.
        
        Args:
            config_dict: Diccionario de configuración
            logger: Logger a utilizar (opcional)
            
        Returns:
            Una instancia de ConfigManager configurada
        """
        return cls(config_data=config_dict, logger=logger)

    @classmethod
    def from_env_vars(cls, prefix: str = "APP_",
                     logger: Optional[logging.Logger] = None) -> 'ConfigManager':
        """
        Crea un ConfigManager a partir de variables de entorno.
        
        Args:
            prefix: Prefijo para filtrar las variables de entorno
            logger: Logger a utilizar (opcional)
            
        Returns:
            Una instancia de ConfigManager configurada
        """
        config = {
            key[len(prefix):].lower(): value
            for key, value in os.environ.items()
            if key.startswith(prefix)
        }
        return cls(config_data=config, logger=logger)

    def _load_config(self) -> None:
        """Carga la configuración desde el archivo."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as file:
                    self._config = json.load(file)
            else:
                self.logger.warning(f"Archivo de configuración no encontrado: {self.config_path}")
        except FileNotFoundError:
            self.logger.warning(f"Archivo de configuración no encontrado: {self.config_path}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Error al decodificar JSON desde archivo: {e}")
        except OSError as e:
            self.logger.error(f"Error de OS al cargar configuración desde archivo: {e}")

    def get_config(self) -> Dict[str, Any]:
        """
        Devuelve la configuración completa.
        
        Returns:
            Diccionario con la configuración actual
        """
        return self._config.copy()

    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor específico de la configuración.
        
        Args:
            key: Clave de la configuración a recuperar
            default: Valor por defecto si la clave no existe
            
        Returns:
            El valor de la configuración o el valor por defecto
        """
        return self._config.get(key, default)

    def update_config(self, new_config: Dict[str, Any]) -> None:
        """
        Actualiza la configuración y la persiste en el archivo si hay uno configurado.
        
        Args:
            new_config: Diccionario con los valores a actualizar
        """
        # Actualizar la configuración en memoria
        self._config.update(new_config)

        # Persistir en el archivo si hay uno configurado
        if self.config_path:
            self._save_config()

    def _save_config(self) -> None:
        """Guarda la configuración en el archivo configurado."""
        try:
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

        except OSError as e:
            self.logger.error(f"Error de OS al guardar configuración en archivo: {e}")
        except TypeError as e:
            self.logger.error(f"Error al codificar JSON para guardar en archivo: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Error al decodificar JSON desde archivo: {e}")
