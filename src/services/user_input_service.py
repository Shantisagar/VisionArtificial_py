"""
Servicio para gestionar la entrada de parámetros de usuario y selección de opciones.
"""

import sys
import logging
from typing import Tuple, Dict, Any

class UserInputService:
    """Clase que encapsula las operaciones de entrada del usuario."""
    
    def __init__(self, logger: logging.Logger):
        """
        Inicializa el servicio con un logger inyectado.
        
        Args:
            logger: Logger configurado para registrar eventos
        """
        self.logger = logger
    
    def obtener_opcion_video(self, config: Dict[str, Any]) -> str:
        """
        Maneja el menú de opciones de usuario y devuelve la URL o ruta de la imagen.
        
        Args:
            config: Diccionario con la configuración
            
        Returns:
            URL o ruta de la imagen seleccionada
        """
        try:
            opcion = input(
                "Seleccione una opción:\n0 - Testing\n1 - RTSP\n2 - HTTP\n3 - Cámara web\nOpción: "
            ) or "3"
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
                sys.exit(1)
        except Exception as e:
            self.logger.error(f"Error al manejar el menú de opciones: {e}")
            sys.exit(1)
    
    def recoger_parametros_usuario(self, config: Dict[str, Any]) -> Tuple[float, float, float, float]:
        """
        Recoge los parámetros necesarios desde la entrada estándar, utilizando valores por defecto
        en caso de no especificar una entrada.
        
        Args:
            config: Diccionario con la configuración
            
        Returns:
            Tupla con grados_rotacion, pixels_por_mm, altura, horizontal
        """
        try:
            grados_rotacion = float(
                input(f'Ingrese los grados de rotación (valor por defecto "{config["grados_rotacion_default"]}"): ')
                or config["grados_rotacion_default"]
            )
            pixels_por_mm = float(
                input(f'Ingrese el valor de pixeles por mm (valor por defecto "{config["pixels_por_mm_default"]}"): ')
                or config["pixels_por_mm_default"]
            )
            altura = float(
                input(f'Ingrese la altura para corregir eje vertical (valor por defecto "{config["altura_default"]}"): ')
                or config["altura_default"]
            )
            horizontal = float(
                input(f'Ingrese el desplazamiento horizontal (valor por defecto "{config["horizontal_default"]}"): ')
                or config["horizontal_default"]
            )
            return grados_rotacion, pixels_por_mm, altura, horizontal
        except Exception as e:
            self.logger.error(f"Error al recoger parámetros del usuario: {e}")
            sys.exit(1)
