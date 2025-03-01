"""
Path: src/services/user_input_service.py
Servicio para gestionar la entrada de parámetros de usuario y selección de opciones.
"""

import logging
from typing import Tuple, Dict, Any
from src.controllers.video_option_controller import VideoOptionController

class UserInputService:
    """Clase que encapsula las operaciones relacionadas con la entrada del usuario."""

    # Límites de validación para los parámetros
    # Estos valores podrían moverse a la configuración si necesitan ser ajustables
    GRADOS_ROTACION_MIN = -180.0
    GRADOS_ROTACION_MAX = 180.0
    PIXELS_POR_MM_MIN = 0.1
    ALTURA_MIN = -1000.0
    ALTURA_MAX = 1000.0
    HORIZONTAL_MIN = -1000.0
    HORIZONTAL_MAX = 1000.0

    def __init__(self, logger: logging.Logger):
        """
        Inicializa el servicio con un logger inyectado.
        
        Args:
            logger: Logger configurado para registrar eventos
        """
        self.logger = logger
        # Utilizamos el nuevo controlador para manejar las opciones de video
        self.video_controller = VideoOptionController(logger)

    def procesar_opcion_video(self, opcion: str, config: Dict[str, Any]) -> Any:
        """
        Procesa la opción de video para la cámara web.
        El parámetro opcion se mantiene por compatibilidad, pero solo se usa la cámara web.
        
        Args:
            opcion: Ignorado (mantenido por compatibilidad)
            config: Diccionario con la configuración
            
        Returns:
            Índice de la cámara web (0)
        """
        try:
            # Siempre usamos la cámara web como fuente única de video
            self.logger.info("Configurando cámara web como fuente de video")
            return self.video_controller.get_source_url("1", config)
        except Exception as e:
            self.logger.error(f"Error al inicializar la cámara web: {e}")
            raise

    def get_video_menu_options(self) -> list[str]:
        """
        Obtiene la opción de menú para la cámara web.
        Método mantenido por compatibilidad.
        
        Returns:
            Lista con la única opción disponible (cámara web)
        """
        return self.video_controller.get_menu_options()

    def get_webcam_url(self, config):
        """
        Obtiene la URL o índice de la webcam directamente de la configuración.
        
        Args:
            config: Configuración de la aplicación
            
        Returns:
            URL o índice de la webcam
        """
        try:
            # Por defecto, usar la primera cámara (índice 0)
            return 0
        except Exception as e:
            self.logger.error(f"Error al obtener URL de webcam: {e}")
            return None

    def validar_grados_rotacion(self, grados: float) -> bool:
        """
        Valida que los grados de rotación estén dentro del rango permitido.
        
        Args:
            grados: Valor de grados a validar
            
        Returns:
            True si el valor es válido, False en caso contrario
            
        Notes:
            Los grados de rotación deben estar entre -180 y 180 grados.
            Este parámetro afecta la orientación de la imagen procesada.
        """
        if not isinstance(grados, (int, float)):
            self.logger.error("Grados de rotación debe ser un número.")
            return False

        if grados < self.GRADOS_ROTACION_MIN or grados > self.GRADOS_ROTACION_MAX:
            self.logger.error(
                f"Grados de rotación fuera de rango "
                f"({self.GRADOS_ROTACION_MIN} a {self.GRADOS_ROTACION_MAX})"
            )
            return False

        return True

    def validar_pixels_por_mm(self, pixels: float) -> bool:
        """
        Valida que los píxeles por milímetro sean positivos y tengan un valor razonable.
        
        Args:
            pixels: Valor de píxeles por milímetro a validar
            
        Returns:
            True si el valor es válido, False en caso contrario
            
        Notes:
            Los píxeles por milímetro deben ser positivos.
            Este parámetro afecta las mediciones realizadas en la imagen.
            Valores típicos están entre 1 y 50 píxeles/mm dependiendo de la resolución.
        """
        if not isinstance(pixels, (int, float)):
            self.logger.error("Píxeles por mm debe ser un número.")
            return False

        if pixels < self.PIXELS_POR_MM_MIN:
            self.logger.error(f"Píxeles por mm debe ser mayor que {self.PIXELS_POR_MM_MIN}")
            return False

        return True

    def validar_altura(self, altura: float) -> bool:
        """
        Valida que el valor de altura para la corrección del eje vertical esté en un rango válido.
        
        Args:
            altura: Valor de altura a validar
            
        Returns:
            True si el valor es válido, False en caso contrario
            
        Notes:
            La altura ajusta la posición vertical de la imagen procesada.
            Los límites dependen del tamaño de la imagen y la aplicación específica.
        """
        if not isinstance(altura, (int, float)):
            self.logger.error("Altura debe ser un número.")
            return False

        if altura < self.ALTURA_MIN or altura > self.ALTURA_MAX:
            self.logger.error(f"Altura fuera de rango ({self.ALTURA_MIN} a {self.ALTURA_MAX})")
            return False

        return True

    def validar_horizontal(self, horizontal: float) -> bool:
        """
        Valida que el desplazamiento horizontal esté en un rango válido.
        
        Args:
            horizontal: Valor de desplazamiento horizontal a validar
            
        Returns:
            True si el valor es válido, False en caso contrario
            
        Notes:
            El desplazamiento horizontal ajusta la posición horizontal de la imagen procesada.
            Los límites dependen del tamaño de la imagen y la aplicación específica.
        """
        if not isinstance(horizontal, (int, float)):
            self.logger.error("Desplazamiento horizontal debe ser un número.")
            return False

        if horizontal < self.HORIZONTAL_MIN or horizontal > self.HORIZONTAL_MAX:
            self.logger.error(
                f"Desplazamiento horizontal fuera de rango "
                f"({self.HORIZONTAL_MIN} a {self.HORIZONTAL_MAX})"
            )
            return False

        return True

    def validar_parametros(self, parametros: Dict[str, float]) -> bool:
        """
        Valida que los parámetros de configuración sean correctos.
        
        Args:
            parametros: Diccionario con los parámetros a validar
            
        Returns:
            True si los parámetros son válidos, False en caso contrario
            
        Notes:
            Esta validación incluye verificar que todos los parámetros requeridos estén presentes,
            y que cada parámetro individual cumpla con sus reglas de validación específicas.
            También puede incluir validaciones que involucren múltiples parámetros.
        """
        try:
            # Verificar que todos los parámetros requeridos están presentes
            required_params = ['grados_rotacion', 'pixels_por_mm', 'altura', 'horizontal']
            for param in required_params:
                if param not in parametros:
                    self.logger.error(f"Falta el parámetro requerido: {param}")
                    return False

            # Validar cada parámetro individual
            if not self.validar_grados_rotacion(parametros['grados_rotacion']):
                return False

            if not self.validar_pixels_por_mm(parametros['pixels_por_mm']):
                return False

            if not self.validar_altura(parametros['altura']):
                return False

            if not self.validar_horizontal(parametros['horizontal']):
                return False

            # Aquí podríamos agregar validaciones adicionales que involucren
            # relaciones entre múltiples parámetros

            return True
        except (KeyError, TypeError, ValueError) as e:
            self.logger.error(f"Error al validar parámetros: {e}")
            return False

    def convertir_a_tupla_parametros(
        self, parametros: Dict[str, float]
    ) -> Tuple[float, float, float, float]:
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
