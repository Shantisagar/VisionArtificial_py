import numpy as np
import logging

# Configuración del logger, asumiendo que ya tienes uno configurado en tu aplicación
logger = logging.getLogger(__name__)

def encontrar_borde(frame):
    """
    Identifica y marca el borde más significativo en la imagen con una línea amarilla.
    
    Calcula el promedio de gris para cada columna y luego identifica la posición del borde
    basándose en el cambio máximo en el valor promedio de gris a lo largo de las columnas.

    Parámetros:
    - frame (np.ndarray): Imagen en la cual se buscará y marcará el borde.
    
    Retorna:
    - np.ndarray: Imagen con una línea amarilla marcando la posición del borde detectado.
    
    Lanza:
    - Exception: Si ocurre un error durante el proceso.
    """
    try:
        grey_avg = calcular_promedio_gris(frame)
        mean = np.mean(grey_avg, axis=0).reshape(frame.shape[1])
        max_x = calcular_derivadas(mean).argmax()
        frame[:, max_x, :] = (255, 255, 0)  # Marca amarilla en la posición del borde
        return frame
    except Exception as e:
        logger.error(f"Error al encontrar el borde: {e}")
        raise

def calcular_promedio_gris(image):
    """
    Calcula el promedio de intensidad de gris para cada píxel en la imagen.

    Parámetros:
    - image (np.ndarray): Imagen de entrada para calcular el promedio de gris.
    
    Retorna:
    - np.ndarray: Imagen en escala de grises con el promedio calculado.
    
    Lanza:
    - Exception: Si ocurre un error durante el cálculo.
    """
    try:
        return np.mean(image, axis=2).reshape((*image.shape[:2], 1))
    except Exception as e:
        logger.error(f"Error al calcular el promedio de gris: {e}")
        raise

def calcular_derivadas(array):
    """
    Calcula la derivada discreta de un array, útil para identificar cambios significativos en los valores.

    Parámetros:
    - array (np.ndarray): Array unidimensional de valores numéricos.
    
    Retorna:
    - np.ndarray: Array unidimensional con las derivadas calculadas.
    
    Lanza:
    - Exception: Si ocurre un error durante el cálculo.
    """
    try:
        left, mid, right = array[:-2], array[1:-1], array[2:]
        return 2 * mid - left - right
    except Exception as e:
        logger.error(f"Error al calcular derivadas: {e}")
        raise
