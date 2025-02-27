"""
Servicio para gestionar la entrada de parámetros de usuario y selección de opciones.
"""

import sys
import logging
from typing import Tuple, Dict, Any

class UserInputService:
    """Clase que encapsula las operaciones relacionadas con la entrada del usuario."""
    
    def __init__(self, logger: logging.Logger):
        """
        Inicializa el servicio con un logger inyectado.
        
        Args:
            logger: Logger configurado para registrar eventos
        """
        self.logger = logger
    
    def procesar_opcion_video(self, opcion: str, config: Dict[str, Any]) -> Any:
        """
        Procesa la opción de video seleccionada por el usuario.
        
        Args:
            opcion: Opción seleccionada por el usuario
            config: Diccionario con la configuración
            
        Returns:
            URL o ruta de la imagen seleccionada
        """
        try:
            if opcion == "0":
                self.logger.info("Modo de calibración de reconocimiento de imagen activado.")
                return config["ubicacion_default"]
            elif opcion == "1":
                self.logger.info("Modo de transmisión RTSP activado.")
                return f"rtsp://{config['url_default']}:8080/h264.sdp"
            elif opcion == "2":
                self.logger.info("Modo HTTP activado.")
                return f"http://{config['url_default']}:8080/photo.jpg"
            elif opcion == "3":
                self.logger.info("Modo de cámara web activado.")
                return 0  # Se utiliza el índice 0 para la cámara web por defecto
            else:
                self.logger.error("Opción no válida.")
                return None
        except Exception as e:
            self.logger.error(f"Error al procesar la opción de video: {e}")
            raise
    
    def validar_parametros(self, parametros: Dict[str, float]) -> bool:
        """
        Valida que los parámetros de configuración sean correctos.
        
        Args:
            parametros: Diccionario con los parámetros a validar
            
        Returns:
            True si los parámetros son válidos, False en caso contrario
        """
        try:
            # Verificar que todos los parámetros requeridos están presentes
            required_params = ['grados_rotacion', 'pixels_por_mm', 'altura', 'horizontal']
            for param in required_params:
                if param not in parametros:
                    self.logger.error(f"Falta el parámetro requerido: {param}")
                    return False
            
            # Verificar que los pixels_por_mm sean positivos
            if parametros['pixels_por_mm'] <= 0:
                self.logger.error("El valor de pixels_por_mm debe ser positivo")
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"Error al validar parámetros: {e}")
            return False
    
    def convertir_a_tupla_parametros(self, parametros: Dict[str, float]) -> Tuple[float, float, float, float]:
        """
        Convierte un diccionario de parámetros a una tupla ordenada.
        
        Args:
            parametros: Diccionario con los parámetros
            
        Returns:
            Tupla con grados_rotacion, pixels_por_mm, altura, horizontal
        """
        return (
            parametros['grados_rotacion'],
            parametros['pixels_por_mm'],
            parametros['altura'],
            parametros['horizontal']
        )
