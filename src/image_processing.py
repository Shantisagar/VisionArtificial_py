import cv2
import numpy as np
from rotacion import rotar_imagen
from correccion_perspectiva import corregir_perspectiva
from deteccion_bordes import encontrar_borde


def aplicar_marcajes(frame, altura):
    """Encuentra bordes y dibuja marcas en la imagen."""
    frame = encontrar_borde(frame)
    frame = dibujar_reglas(frame, altura)
    return frame


def dibujar_reglas(frame, altura, pixels_per_mm=4, altura2=120):
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


def process_image(frame, grados, altura,perspectiva_default):
    if grados != 0:
        frame = rotar_imagen(frame, grados)
    
    # Definir pts1 y pts2 para la corrección de perspectiva
    pts1 = np.float32([[0, 0], [640, 0], [0, 480], [640, 480]])
    pts2 = np.float32([[0, 0], [640, perspectiva_default], [0, 480], [640, 480]])

    # Estos puntos deben ser ajustados según tu necesidad específica
    
    frame = corregir_perspectiva(frame, pts1, pts2)
    
    frame = encontrar_borde(frame)
    frame = dibujar_reglas(frame, altura)
    
    return frame


