"""
Módulo de procesamiento de imágenes que incluye funciones de transformación,
detección de bordes y anotación gráfica.
"""

import cv2
import numpy as np
import datetime
from src.rotacion import rotar_imagen
from src.deteccion_bordes import encontrar_borde
from utils.logging.logger_configurator import LoggerConfigurator
from src.registro_desvios import registrar_desvio

TOLERANCIA = 2  # Tolerancia en milímetros
logger = LoggerConfigurator().configure()

# ----------------------- Utilidades de Dibujo y Cálculos -----------------------

def dibujar_reglas(frame, pixels_por_mm=20):
    """
    Dibuja líneas guía (horizontal y vertical) y marca milimétrica sobre la imagen.
    """
    altura, ancho = frame.shape[:2]
    centro_x, centro_y = ancho // 2, altura // 2

    # Línea horizontal (verde)
    cv2.line(frame, (0, centro_y), (ancho, centro_y), (0, 255, 0), 2)
    # Línea vertical (roja, punteada)
    for y in range(0, altura, 4):
        if y % 8 < 4:
            cv2.line(frame, (centro_x, y), (centro_x, min(y+2, altura)), (255, 0, 0), 1)

    # Marcas de milímetros y números de centímetros
    int_pixels = int(pixels_por_mm)
    for mm in range(int(-centro_x // int_pixels), int(centro_x // int_pixels)):
        x_pos = centro_x + mm * int_pixels
        if mm % 10 == 0:
            cv2.line(frame, (x_pos, centro_y - 10), (x_pos, centro_y + 10), (255, 255, 255), 2)
            cv2.putText(frame, str(mm // 10), (x_pos - 5, centro_y + 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
        else:
            cv2.line(frame, (x_pos, centro_y - 5), (x_pos, centro_y + 5), (255, 255, 255), 1)
            cv2.putText(frame, str(mm), (x_pos - 5, centro_y + 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
    return frame

def calcular_desvio_en_mm(posicion_borde_x, ancho_imagen, pixels_por_mm):
    """
    Calcula la desviación en milímetros respecto del centro de la imagen.
    """
    centro_imagen_x = ancho_imagen / 2
    desvio_pixeles = posicion_borde_x - centro_imagen_x
    desvio_mm = round(desvio_pixeles / pixels_por_mm, 2)
    return desvio_mm

def desplazar_horizontal(frame, horizontal):
    """
    Desplaza la imagen horizontalmente mediante una transformación afín.
    """
    altura, ancho = frame.shape[:2]
    M = np.float32([[1, 0, horizontal], [0, 1, 0]])
    return cv2.warpAffine(frame, M, (ancho, altura))

# ------------------ Clase Controladora del Procesamiento ------------------

class ProcessingController:
    def __init__(self, default_pixels_por_mm=20):
        self.default_pixels_por_mm = default_pixels_por_mm

    def process(self, frame, grados, altura, horizontal, pixels_por_mm):
        """
        Orquesta el procesamiento en cadena: rotación, desplazamiento, detección de borde,
        anotación gráfica y registro de desviación.
        """
        try:
            # Transformaciones básicas
            if grados != 0:
                frame = rotar_imagen(frame, grados)
            if horizontal != 0:
                frame = desplazar_horizontal(frame, horizontal)
            # Detección de borde
            frame, max_x = encontrar_borde(frame)
            # Dibujar reglas sobre la imagen
            frame = dibujar_reglas(frame, pixels_por_mm)
            # Calcular la desviación y registrar el dato
            desvio_mm = calcular_desvio_en_mm(max_x, frame.shape[1], pixels_por_mm)
            now = datetime.datetime.now()
            fecha_hora = now.strftime("%d-%m-%Y %H:%M:%S")
            texto0 = fecha_hora
            texto1 = registrar_desvio(desvio_mm, TOLERANCIA)
            # Ejemplo de otros textos informativos
            texto2 = "Ancho de bobina: 790mm"
            texto3 = "Formato bolsa: 260x120x360"
            texto4 = "solapa: 30mm"

            # Posicionamiento y dibujo de la información en la imagen
            posiciones = [
                (frame.shape[1] - 700, 100),
                (frame.shape[1] - 700, 150),
                (frame.shape[1] - 700, 200),
                (frame.shape[1] - 700, 250),
                (frame.shape[1] - 700, 300)
            ]
            textos = [texto0, texto1, texto2, texto3, texto4]
            fuente = cv2.FONT_HERSHEY_SIMPLEX
            escala_fuente = 0.7
            color = (0, 255, 255)
            grosor = 2
            for pos, texto in zip(posiciones, textos):
                cv2.putText(frame, texto, pos, fuente, escala_fuente, color, grosor)

            return frame
        except Exception as e:
            logger.error("Error al procesar la imagen: %s", e)
            raise