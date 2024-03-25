#VisionArtificial\src\image_processing.py
import cv2
import numpy as np
from rotacion import rotar_imagen
from correccion_perspectiva import corregir_perspectiva
from deteccion_bordes import encontrar_borde
from logs.config_logger import configurar_logging

# Configuración del logger
logger = configurar_logging()

def dibujar_reglas(frame, pixels_por_mm=10):
    """
    Dibuja una línea horizontal y una línea vertical centradas en la imagen, con una regla sobre la línea
    horizontal que marca milímetros y centímetros.

    Parámetros:
    - frame (np.ndarray): Imagen en la que se dibujarán las líneas y marcas de la regla.
    - pixels_por_mm (int): Número de píxeles que representan un milímetro en la imagen.

    Retorna:
    - np.ndarray: La imagen con una línea horizontal y una vertical dibujadas, y una regla sobre la horizontal.
    """
    altura, ancho = frame.shape[:2]
    centro_x, centro_y = ancho // 2, altura // 2

    # Dibujar líneas centradas
    cv2.line(frame, (0, centro_y), (ancho, centro_y), (0, 255, 0), 2)  # Línea horizontal verde
    cv2.line(frame, (centro_x, 0), (centro_x, altura), (255, 0, 0), 2)  # Línea vertical roja

    # Dibujar marcas de milímetros y números de centímetros
    for mm in range(-centro_x // pixels_por_mm, centro_x // pixels_por_mm):
        if mm % 10 == 0:  # Marcas más largas para centímetros
            cv2.line(frame, (centro_x + mm * pixels_por_mm, centro_y - 10), (centro_x + mm * pixels_por_mm, centro_y + 10), (255, 255, 255), 2)
            cv2.putText(frame, str(mm // 10), (centro_x + mm * pixels_por_mm - 5, centro_y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
        else:  # Marcas más cortas para milímetros
            cv2.line(frame, (centro_x + mm * pixels_por_mm, centro_y - 5), (centro_x + mm * pixels_por_mm, centro_y + 5), (255, 255, 255), 1)

    return frame



def process_image(frame, grados, altura, perspectiva_default, horizontal):
    """
    Procesa la imagen aplicando rotación, corrección de perspectiva y detección de bordes.
    """
    try:
        if grados != 0:
            frame = rotar_imagen(frame, grados)

        pts1 = np.float32([[0, 0], [640, 0], [0, 480], [640, 480]])
        pts2 = np.float32([[0, 0], [640, perspectiva_default], [0, 480], [640, 480]])
        
        frame = corregir_perspectiva(frame, pts1, pts2)
        frame = encontrar_borde(frame)
        frame = dibujar_reglas(frame)

        return frame
    except Exception as e:
        logger.error(f"Error al procesar la imagen: {e}")
        raise

