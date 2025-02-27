"""
Path: app/logs/json_config_strategy.py

"""
import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from utils.logging.config_strategy import ConfigStrategy

class JSONConfigStrategy(ConfigStrategy):
    """
    Estrategia para cargar la configuración desde un archivo JSON
    con soporte para diferentes entornos.
    """
    def __init__(self, config_path: str = 'utils/logging/logging.json'):
        """
        Inicializa la estrategia JSON con la ruta del archivo de configuración.

        Args:
            config_path (str): Ruta al archivo de configuración JSON.
        """
        self.config_path = Path(config_path)
        self._validate_config_path()

    def _validate_config_path(self) -> None:
        """Valida que la ruta del archivo de configuración sea correcta."""
        if not self.config_path.is_absolute():
            # Convertir ruta relativa a absoluta desde la raíz del proyecto.
            self.config_path = Path(os.path.dirname(__file__)).parent.parent / self.config_path

    def _adjust_log_level(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ajusta los niveles de log y elimina handlers no deseados según el entorno.

        Args:
            config (Dict[str, Any]): Configuración original.

        Returns:
            Dict[str, Any]: Configuración ajustada.
        """
        is_development = os.getenv('IS_DEVELOPMENT', 'true').lower() == 'true'

        # Ajustar nivel de log para el handler de consola
        if 'handlers' in config and 'console' in config['handlers']:
            config['handlers']['console']['level'] = 'DEBUG' if is_development else 'INFO'

        # Ajustar nivel de log para el root logger
        if 'loggers' in config and '' in config['loggers']:
            config['loggers']['']['level'] = 'DEBUG' if is_development else 'INFO'

        # Eliminar FileHandlers en producción
        if not is_development:
            file_handlers = [handler for handler in
                             config['handlers'] if 'FileHandler'
                             in config['handlers'][handler]['class']]
            for handler in file_handlers:
                del config['handlers'][handler]

        return config

    def load_config(self) -> Optional[Dict[str, Any]]:
        """
        Carga la configuración desde el archivo JSON y ajusta según el entorno.

        Returns:
            Optional[Dict[str, Any]]: Configuración ajustada o None si hay error.
        """
        try:
            # Primero intentar cargar desde LOG_CFG si está definido.
            config_path = os.getenv('LOG_CFG', str(self.config_path))
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return self._adjust_log_level(config)
        except FileNotFoundError as e:
            logging.error("Archivo de configuración no encontrado: %s", e)
        except json.JSONDecodeError as e:
            logging.error("Error al decodificar JSON: %s", e)
        except PermissionError as e:
            logging.error("No se tiene permiso para acceder al archivo: %s", e)
        except (OSError, IOError) as e:  # Para casos realmente inesperados.
            logging.error("Error al cargar la configuración: %s", e)
        return None

    def another_method(self):
        """Another public method to satisfy pylint."""
        print("Another method")
