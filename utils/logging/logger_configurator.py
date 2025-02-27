"""
Path: app/core_logs/logger_configurator.py
Clase LoggerConfigurator mejorada para garantizar una única instancia y configuración consistente.
"""

import logging.config
from typing import Optional
import json
from utils.logging.json_config_strategy import JSONConfigStrategy
from utils.logging.config_strategy import ConfigStrategy

class LoggerConfigurator:
    """Clase singleton para configurar el logger usando una estrategia y filtros dinámicos."""
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_strategy: Optional[ConfigStrategy] = None,
                 default_level: int = logging.INFO):
        """
        Inicializa el configurador del logger (solo una vez).
        
        Args:
            config_strategy (Optional[ConfigStrategy]): Estrategia para cargar la config.
            default_level (int): Nivel de log por defecto.
        """
        if not self._initialized:
            self.config_strategy = config_strategy or JSONConfigStrategy()
            self.default_level = default_level
            self.filters = {}
            self._logger = None
            self._initialized = True

    def register_filter(self, name: str, filter_class: type) -> None:
        """
        Registra un filtro dinámicamente.
        
        Args:
            name (str): Nombre del filtro.
            filter_class (type): Clase que hereda de logging.Filter.
        """
        if name not in self.filters:
            self.filters[name] = filter_class()

    def configure(self) -> logging.Logger:
        """
        Configura y retorna el logger. 
        Si ya se configuró anteriormente, retorna la misma instancia.
        
        Returns:
            logging.Logger: Logger configurado.
        """
        if self._logger is not None:
            return self._logger

        config = self.config_strategy.load_config()

        if config:
            if 'filters' not in config:
                config['filters'] = {}


            for name, filter_instance in self.filters.items():
                config['filters'][name] = {
                    '()': f"{filter_instance.__class__.__module__}."
                        f"{filter_instance.__class__.__name__}"
                }
            print(f"Filters: {self.filters}\n")
            print(f"Config: {config}\n")
            try:
                logging.debug(f"Logger configuration: {json.dumps(config, indent=4)}")
                logging.config.dictConfig(config)
                self._logger = logging.getLogger("app_logger")
            except ValueError as e:  # Error típico al usar dictConfig
                logging.error(f"Error en la configuración del logger (dictConfig): {e}")
                # MODIFICACIÓN: invoca el fallback si se produce ValueError
                self._use_default_config()
            except (TypeError, AttributeError, ImportError, KeyError) as e:
                logging.error(f"Error específico al aplicar la configuración: {e}")
                self._use_default_config()
            else:
                self._use_default_config()

        return self._logger

    def _use_default_config(self) -> None:
        """
        Aplica la configuración por defecto cuando la configuración principal falla.
        """
        logging.basicConfig(
            level=self.default_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self._logger = logging.getLogger("app_logger")
        logging.warning("Usando configuración por defecto del logger.")
