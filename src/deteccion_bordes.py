import numpy as np
import logging

# Configuración del logger, asumiendo que ya tienes uno configurado en tu aplicación
logger = logging.getLogger(__name__)

def encontrar_borde(frame):
    """
    Identifica y marca el borde más significativo en el 60% central de la imagen con una línea amarilla.
    
    Calcula el promedio de gris para cada columna en el 60% central y luego identifica la posición del borde
    basándose en el cambio máximo en el valor promedio de gris a lo largo de estas columnas.

    Parámetros:
    - frame (np.ndarray): Imagen en la cual se buscará y marcará el borde.
    
    Retorna:
    - np.ndarray: Imagen con una línea amarilla marcando la posición del borde detectado.
    
    Lanza:
    - Exception: Si ocurre un error durante el proceso.
    """
    try:
        # Calcular los límites para excluir el 20% de los márgenes de cada lado
        cols = frame.shape[1]
        start_col = int(cols * 0.2)
        end_col = int(cols * 0.8)

        # Aplicar el cálculo del promedio de gris solo al 60% central
        grey_avg = calcular_promedio_gris(frame[:, start_col:end_col])
        mean = np.mean(grey_avg, axis=0).reshape(end_col - start_col)
        
        # Calcular las derivadas y encontrar la posición máxima del cambio en el segmento central
        max_x_central = calcular_derivadas(mean).argmax()
        
        # Ajustar la posición del borde al marco completo de la imagen
        max_x = max_x_central + start_col
        
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
    """
    try:
        left, mid, right = array[:-2], array[1:-1], array[2:]
        return 2 * mid - left - right
    except Exception as e:
        logger.error(f"Error al calcular derivadas: {e}")
        raise
