import numpy as np

def encontrar_borde(frame):
    """Encuentra la posición del borde del papel y marca una línea amarilla."""
    grey_avg = calcular_promedio_gris(frame)
    mean = np.mean(grey_avg, axis=0).reshape(frame.shape[1])
    max_x = calcular_derivadas(mean).argmax()
    frame[:, max_x, :] = (255, 255, 0)  # Marca amarilla en la posición del borde
    return frame

def calcular_promedio_gris(image):
    """Calcula el promedio de gris de la imagen."""
    return np.mean(image, axis=2).reshape((*image.shape[:2], 1))

def calcular_derivadas(array):
    """Calcula las derivadas del array."""
    left, mid, right = array[:-2], array[1:-1], array[2:]
    return 2 * mid - left - right

