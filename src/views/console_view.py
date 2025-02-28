"""
Vista para manejar interacciones de consola con el usuario.
Implementa la capa de presentación del patrón MVC.
"""

import logging
from typing import Dict, Any, Tuple, Optional, List

class ConsoleView:
    """Clase responsable de la interacción con el usuario vía consola."""
    
    def __init__(self, logger: logging.Logger):
        """
        Inicializa la vista de consola.
        
        Args:
            logger: Logger configurado para registrar eventos
        """
        self.logger = logger
    
    def mostrar_menu_fuente_video(self, options: Optional[List[str]] = None) -> str:
        """
        Muestra el menú de opciones de fuente de video y captura la elección del usuario.
        
        Args:
            options: Lista de opciones a mostrar (opcional)
            
        Returns:
            La opción seleccionada por el usuario
        """
        menu_text = "Seleccione una opción:\n"
        
        # Si no se proporcionan opciones, usar las predeterminadas
        if options is None:
            options = [
                "0 - Testing",
                "1 - RTSP",
                "2 - HTTP",
                "3 - Cámara web"
            ]
        
        # Construir el menú
        for option in options:
            menu_text += f"{option}\n"
        
        menu_text += "Opción: "
        
        # Solicitar y retornar la opción
        return input(menu_text) or "3"  # Por defecto, cámara web
    
    def solicitar_parametros_usuario(self, config: Dict[str, Any]) -> Dict[str, float]:
        """
        Solicita y recoge todos los parámetros del usuario vía consola.
        
        Args:
            config: Diccionario con valores por defecto para mostrar al usuario
            
        Returns:
            Diccionario con los valores ingresados por el usuario
        """
        try:
            grados_rotacion = self.solicitar_grados_rotacion(config["grados_rotacion_default"])
            pixels_por_mm = self.solicitar_pixels_por_mm(config["pixels_por_mm_default"])
            altura = self.solicitar_altura(config["altura_default"])
            horizontal = self.solicitar_horizontal(config["horizontal_default"])
            
            return {
                'grados_rotacion': grados_rotacion,
                'pixels_por_mm': pixels_por_mm,
                'altura': altura,
                'horizontal': horizontal
            }
        except ValueError as e:
            self.mostrar_error(f"Error al procesar un valor: {e}")
            raise
    
    def solicitar_grados_rotacion(self, valor_default: float) -> float:
        """
        Solicita los grados de rotación al usuario.
        
        Args:
            valor_default: Valor por defecto a mostrar al usuario
            
        Returns:
            Grados de rotación ingresados como número flotante
            
        Raises:
            ValueError: Si el valor ingresado no puede convertirse a flotante
        """
        valor = input(f'Ingrese los grados de rotación (valor por defecto "{valor_default}"): ') or str(valor_default)
        try:
            return float(valor)
        except ValueError:
            raise ValueError("El valor de grados de rotación debe ser un número.")
    
    def solicitar_pixels_por_mm(self, valor_default: float) -> float:
        """
        Solicita los píxeles por milímetro al usuario.
        
        Args:
            valor_default: Valor por defecto a mostrar al usuario
            
        Returns:
            Píxeles por milímetro ingresados como número flotante
            
        Raises:
            ValueError: Si el valor ingresado no puede convertirse a flotante o es negativo
        """
        valor = input(f'Ingrese el valor de pixeles por mm (valor por defecto "{valor_default}"): ') or str(valor_default)
        try:
            return float(valor)
        except ValueError:
            raise ValueError("El valor de píxeles por mm debe ser un número positivo.")
    
    def solicitar_altura(self, valor_default: float) -> float:
        """
        Solicita el valor de altura para corrección del eje vertical.
        
        Args:
            valor_default: Valor por defecto a mostrar al usuario
            
        Returns:
            Altura ingresada como número flotante
            
        Raises:
            ValueError: Si el valor ingresado no puede convertirse a flotante
        """
        valor = input(f'Ingrese la altura para corregir eje vertical (valor por defecto "{valor_default}"): ') or str(valor_default)
        try:
            return float(valor)
        except ValueError:
            raise ValueError("El valor de altura debe ser un número.")
    
    def solicitar_horizontal(self, valor_default: float) -> float:
        """
        Solicita el desplazamiento horizontal al usuario.
        
        Args:
            valor_default: Valor por defecto a mostrar al usuario
            
        Returns:
            Desplazamiento horizontal ingresado como número flotante
            
        Raises:
            ValueError: Si el valor ingresado no puede convertirse a flotante
        """
        valor = input(f'Ingrese el desplazamiento horizontal (valor por defecto "{valor_default}"): ') or str(valor_default)
        try:
            return float(valor)
        except ValueError:
            raise ValueError("El valor de desplazamiento horizontal debe ser un número.")
    
    def mostrar_error(self, mensaje: str) -> None:
        """
        Muestra un mensaje de error al usuario.
        
        Args:
            mensaje: Mensaje de error a mostrar
        """
        print(f"ERROR: {mensaje}")
        self.logger.error(mensaje)
    
    def mostrar_info(self, mensaje: str) -> None:
        """
        Muestra un mensaje informativo al usuario.
        
        Args:
            mensaje: Mensaje informativo a mostrar
        """
        print(f"INFO: {mensaje}")
        self.logger.info(mensaje)
