#VisionArtificial\src\image_processing.py
import cv2
import numpy as np
from rotacion import rotar_imagen
from correccion_perspectiva import corregir_perspectiva
from deteccion_bordes import encontrar_borde
import logging
from logs.config_logger import configurar_logging

# Configuración del logger
logger = configurar_logging()

import cv2

def dibujar_reglas(frame):
    """
    Dibuja una línea horizontal y una línea vertical centradas en la imagen.

    Parámetros:
    - frame (np.ndarray): Imagen en la que se dibujarán las líneas.

    Retorna:
    - np.ndarray: La imagen con una línea horizontal y una vertical dibujadas.
    """
    # Obtener dimensiones de la imagen
    altura, ancho = frame.shape[:2]

    # Calcular el centro de la imagen
    centro_x, centro_y = ancho // 2, altura // 2

    # Dibujar una línea horizontal centrada
    cv2.line(frame, (0, centro_y), (ancho, centro_y), (0, 255, 0), 2)

    # Dibujar una línea vertical centrada
    cv2.line(frame, (centro_x, 0), (centro_x, altura), (255, 0, 0), 2)

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

