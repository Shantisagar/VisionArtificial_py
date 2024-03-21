import cv2

def corregir_perspectiva(frame, pts1, pts2):
    """Corrige la perspectiva de una región de la imagen."""
    matriz_transformacion = cv2.getPerspectiveTransform(pts1, pts2)
    altura, ancho = frame.shape[:2]
    return cv2.warpPerspective(frame, matriz_transformacion, (ancho, altura))
