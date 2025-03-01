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
    """Clase responsable de cargar y gestionar la configuración desde un archivo JSON."""

    def __init__(self, config: Dict[str, Any], config_file: str = None, logger=None):
        """
        Inicializa el gestor de configuración con un diccionario de configuración 
        y opcionalmente un archivo para persistencia.
        
        Args:
            config: Diccionario con la configuración
            config_file: Ruta al archivo de configuración para operaciones de guardado
            logger: Logger configurado para registro de eventos (opcional)
        """
        self.config = config
        self.config_file = config_file
        self.logger = logger or logging.getLogger(__name__)

    @classmethod
    def from_file(cls, file_path: str, logger=None):
        """
        Crea una instancia del gestor cargando la configuración desde un archivo.
        
        Args:
            file_path: Ruta al archivo de configuración JSON
            logger: Logger configurado para registro de eventos (opcional)
            
        Returns:
            Instancia de ConfigManager con la configuración cargada
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            json.JSONDecodeError: Si el archivo no contiene JSON válido
        """
        local_logger = logger or logging.getLogger(__name__)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                config = json.load(file)
            local_logger.info(f"Configuración cargada desde {file_path}")
            return cls(config, file_path, local_logger)
        except FileNotFoundError:
            local_logger.error(f"Archivo de configuración no encontrado: {file_path}")
            raise
        except json.JSONDecodeError as e:
            local_logger.error(f"Error al parsear el archivo de configuración {file_path}: {e}")
            raise
        except Exception as e:
            local_logger.error(f"Error inesperado cargando configuración: {e}")
            raise

    def get_config(self) -> Dict[str, Any]:
        """
        Obtiene el diccionario de configuración.
        
        Returns:
            Diccionario con la configuración actual
        """
        return self.config.copy()  # Devolver una copia para evitar modificación externa accidental

    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """
        Actualiza la configuración con nuevos valores y guarda los cambios si hay un archivo configurado.
        
        Args:
            new_config: Diccionario con los nuevos valores de configuración a actualizar
            
        Returns:
            True si se actualizó y guardó correctamente, False en caso contrario
        """
        try:
            # Actualizar solo las claves proporcionadas
            for key, value in new_config.items():
                self.config[key] = value
                
            # Guardar los cambios si hay un archivo de configuración definido
            if self.config_file:
                with open(self.config_file, 'w', encoding='utf-8') as file:
                    json.dump(self.config, file, indent=4)
                self.logger.info(f"Configuración actualizada y guardada en {self.config_file}")
            else:
                self.logger.info("Configuración actualizada (sin persistencia)")
                
            return True
        except (IOError, OSError) as e:
            self.logger.error(f"Error al guardar la configuración: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error inesperado actualizando configuración: {e}")
            return False
