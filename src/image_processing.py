#VisionArtificial\src\image_processing.py
import cv2
import numpy as np
import datetime
from rotacion import rotar_imagen
from deteccion_bordes import encontrar_borde
from logs.config_logger import configurar_logging

# Configuración del logger
logger = configurar_logging()

def dibujar_reglas(frame, pixels_por_mm=20):
    """
    Dibuja una línea horizontal y una línea vertical centradas en la imagen, con una regla sobre la línea
    horizontal que marca milímetros y centímetros. La línea vertical es roja, de 1 pixel de grosor y punteada.

    Parámetros:
    - frame (np.ndarray): Imagen en la que se dibujarán las líneas y marcas de la regla.
    - pixels_por_mm (int): Número de píxeles que representan un milímetro en la imagen.

    Retorna:
    - np.ndarray: La imagen con una línea horizontal y una vertical dibujadas, y una regla sobre la horizontal.
    """
    altura, ancho = frame.shape[:2]
    centro_x, centro_y = ancho // 2, altura // 2

    # Dibujar línea horizontal verde
    cv2.line(frame, (0, centro_y), (ancho, centro_y), (0, 255, 0), 2)

    # Dibujar línea vertical roja y punteada
    for y in range(0, altura, 4):  # Cambia 4 por otro valor para ajustar el espaciado de los puntos
        if y % 8 < 4:  # Cambia 4 para ajustar la longitud de los segmentos
            cv2.line(frame, (centro_x, y), (centro_x, min(y+2, altura)), (255, 0, 0), 1)  # Cambia 2 para ajustar la longitud de los segmentos

    # Dibujar marcas de milímetros y números de centímetros
    for mm in range(-centro_x // pixels_por_mm, centro_x // pixels_por_mm):
        if mm % 10 == 0:  # Marcas más largas para centímetros
            cv2.line(frame, (centro_x + mm * pixels_por_mm, centro_y - 10), (centro_x + mm * pixels_por_mm, centro_y + 10), (255, 255, 255), 2)
            cv2.putText(frame, str(mm // 10), (centro_x + mm * pixels_por_mm - 5, centro_y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
        else:  # Marcas más cortas para milímetros
            cv2.line(frame, (centro_x + mm * pixels_por_mm, centro_y - 5), (centro_x + mm * pixels_por_mm, centro_y + 5), (255, 255, 255), 1)
            cv2.putText(frame, str(mm), (centro_x + mm * pixels_por_mm - 5, centro_y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)

    return frame
def calcular_desvio_en_mm(posicion_borde_x, ancho_imagen, pixels_por_mm):
    centro_imagen_x = ancho_imagen / 2
    desvio_pixeles = posicion_borde_x - centro_imagen_x
    desvio_mm = desvio_pixeles / pixels_por_mm
    return desvio_mm

def process_image(frame, grados, altura, horizontal, pixels_por_mm):
    """
    Procesa la imagen aplicando rotación, desplazamiento horizontal, corrección de perspectiva y detección de bordes.
    """
    try:
        if grados != 0:
            frame = rotar_imagen(frame, grados)
        
        if horizontal != 0:
            frame = desplazar_horizontal(frame, horizontal)
        
        #frame, posicion_borde_x = encontrar_borde(frame)
        frame,max_x = encontrar_borde(frame)
  
        frame = dibujar_reglas(frame)
        posicion_borde_x = max_x
        # Calcular el desvío en milímetros
        desvio_mm = calcular_desvio_en_mm(posicion_borde_x, frame.shape[1], pixels_por_mm)
        
        # Mostrar el desvío en la consola
        logger.info(f"Desvio registrado: {desvio_mm} mm")

        # Obtener la fecha y hora actuales
        now = datetime.datetime.now()
        fecha_hora = now.strftime("%Y-%m-%d %H:%M:%S")

        # Preparar el texto a mostrar en la imagen
        texto = f"{fecha_hora} - Desvio: {desvio_mm} mm"
        # Ubicación del texto en la imagen (arriba a la derecha)
        posicion = (frame.shape[1] - 500, 100)  
        
        # Especificaciones de fuente
        fuente = cv2.FONT_HERSHEY_SIMPLEX
        escala_fuente = 0.7
        color = (0, 255, 255)  # Amarillo en BGR
        grosor = 2

        # Dibujar el texto en la imagen
        cv2.putText(frame, texto, posicion, fuente, escala_fuente, color, grosor)

        return frame
    except Exception as e:
        logger.error(f"Error al procesar la imagen: {e}")
        raise

def desplazar_horizontal(frame, horizontal):
    """
    Desplaza la imagen horizontalmente según el valor especificado.

    Parámetros:
    - frame (np.ndarray): La imagen a desplazar.
    - horizontal (float): La cantidad de desplazamiento horizontal.
    
    Retorna:
    - np.ndarray: La imagen desplazada.
    """
    altura, ancho = frame.shape[:2]
    M = np.float32([[1, 0, horizontal], [0, 1, 0]])  # Matriz de transformación
    return cv2.warpAffine(frame, M, (ancho, altura))
