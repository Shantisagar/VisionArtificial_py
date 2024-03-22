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

def dibujar_reglas(frame, altura, pixels_per_mm=4, altura2=120):
    """
    Dibuja reglas horizontales y marcas de milímetros en una imagen para la evaluación visual de dimensiones.

    Dibuja dos líneas horizontales a lo largo de la imagen para representar mediciones verticales específicas,
    y agrega marcas de milímetros en la parte superior e inferior de la imagen para ayudar en la medición de distancias.

    Parámetros:
    - frame (np.ndarray): Imagen en la que se dibujarán las reglas.
    - altura (int): Desplazamiento vertical desde la mitad de la imagen para la primera línea horizontal.
    - pixels_per_mm (int, opcional): Número de píxeles que representan un milímetro en la imagen, por defecto es 4.
    - altura2 (int, opcional): Desplazamiento adicional desde la primera línea horizontal para la segunda línea, por defecto es 120.

    Retorna:
    - np.ndarray: La imagen con las reglas y marcas de milímetros dibujadas.
    """
    image_width = frame.shape[1]
    image_height = frame.shape[0]

    # Dibuja reglas en la parte superior e inferior de la imagen
    cv2.line(frame, (0, int(image_height - 30)), (int(image_width), int(image_height - 30)), (255, 0, 0), 2)
    cv2.line(frame, (0, 30), (int(image_width), 30), (255, 0, 0), 2)

    # Agrega marcas de milímetros a las reglas
    for mm in range(-10, 121, 10):
        x = int((mm + 10) * pixels_per_mm)
        cv2.line(frame, (x, int(image_height - 40)), (x, int(image_height - 20)), (0, 0, 255), 1)
        cv2.putText(frame, f"{mm} ", (x, int(image_height - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        cv2.line(frame, (x, 10), (x, 30), (0, 0, 255), 1)
        cv2.putText(frame, f"{mm} ", (x, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    # Calcula la posición media en el eje y y dibuja una línea verde horizontal
    mitad_altura = image_height // 2
    mitad_altura += altura  # Asegúrate de que "altura" sea un entero o se convierta a entero
    cv2.line(frame, (0, int(mitad_altura)), (int(image_width), int(mitad_altura)), (0, 255, 0), 2)
    mitad_altura += altura2  # Asegúrate de que "altura2" sea un entero
    cv2.line(frame, (0, int(mitad_altura)), (int(image_width), int(mitad_altura)), (0, 255, 0), 2)

    return frame

def process_image(frame, grados, altura, perspectiva_default):
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
        frame = dibujar_reglas(frame, altura)

        return frame
    except Exception as e:
        logger.error(f"Error al procesar la imagen: {e}")
        raise

