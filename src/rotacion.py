"""
Path: src/rotacion.py
Este script contiene una función para rotar una imagen en sentido antihorario.
"""

import cv2
from src.utils.simple_logger import LoggerService

logger = LoggerService()


def rotar_imagen(frame, grados):
    # pylint: disable=no-member
    """
    Rota la imagen un número específico de grados en sentido antihorario.
    
    Utiliza la matriz de rotación de OpenCV para rotar 
    la imagen alrededor de su centro sin cambiar su escala.
    
    Parámetros:
    - frame (np.ndarray): Imagen a rotar.
    - grados (float): Número de grados para rotar la imagen.
    Los valores positivos rotan en sentido antihorario.
    
    Retorna:
    - np.ndarray: La imagen rotada.
    
    Lanza:
    - Exception: Si ocurre un error durante la rotación de la imagen.
    """
    try:
        altura, ancho = frame.shape[:2]
        punto_central = (ancho // 2, altura // 2)
        matriz_rotacion = cv2.getRotationMatrix2D(punto_central, grados, 1.0)
        return cv2.warpAffine(frame, matriz_rotacion, (ancho, altura))
    except Exception as e:
        logger.error("Error al rotar la imagen: %s", e)
        raise
