#VisionArtificial\src\correccion_perspectiva.py
import cv2
import logging
import numpy as np

# Configuración del logger, asumiendo que ya tienes uno configurado en tu aplicación
logger = logging.getLogger(__name__)

def corregir_perspectiva(frame, pts1, pts2):
    """
    Corrige la perspectiva de una región específica de la imagen, basándose en puntos de origen y destino.

    Utiliza una transformación de perspectiva para mapear los puntos de una región de la imagen (pts1) a una nueva 
    perspectiva (pts2), usualmente para corregir efectos de inclinación o ángulo.

    Parámetros:
    - frame (np.ndarray): Imagen en la que se aplicará la corrección de perspectiva.
    - pts1 (np.ndarray): Array de puntos 2D (4 puntos) en la imagen original que definen la región a corregir.
    - pts2 (np.ndarray): Array de puntos 2D (4 puntos) que definen cómo se debe mostrar la región corregida.

    Retorna:
    - np.ndarray: Imagen con la corrección de perspectiva aplicada.

    Lanza:
    - Exception: Si ocurre un error durante la transformación de perspectiva.
    """
    try:
        # Asegurar que los puntos son arrays de NumPy de tipo float32
        pts1 = np.array(pts1, dtype=np.float32)
        pts2 = np.array(pts2, dtype=np.float32)

        matriz_transformacion = cv2.getPerspectiveTransform(pts1, pts2)
        altura, ancho = frame.shape[:2]
        return cv2.warpPerspective(frame, matriz_transformacion, (ancho, altura))
    except Exception as e:
        logger.error(f"Error al corregir la perspectiva: {e}")
        raise
