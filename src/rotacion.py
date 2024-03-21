import cv2


def rotar_imagen(frame, grados):
    """Rota la imagen un número específico de grados en sentido antihorario."""
    altura, ancho = frame.shape[:2]
    punto_central = (ancho // 2, altura // 2)
    matriz_rotacion = cv2.getRotationMatrix2D(punto_central, grados, 1.0)
    return cv2.warpAffine(frame, matriz_rotacion, (ancho, altura))