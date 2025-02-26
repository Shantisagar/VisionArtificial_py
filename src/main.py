"""
Path: src/main.py
Archivo de entrada simplificado para iniciar la aplicación.
"""

import sys
import tkinter as tk
from src.video_stream import VideoStreamApp
from src.logs.config_logger import configurar_logging
from src.config_manager import leer_configuracion, actualizar_configuracion

logger = configurar_logging()

def manejar_menu(config):
    """
    Maneja el menú de opciones de usuario y devuelve la URL del video o ruta de la imagen seleccionada.
    """
    try:
        opcion = input("Seleccione una opción:\n0 - Testing\n1 - RTSP\n2 - HTTP\nOpción: ") or "2"
        if opcion == "0":
            logger.info("Modo de calibración de reconocimiento de imagen activado.")
            return config["ubicacion_default"]
        elif opcion == "1":
            logger.info("Modo de transmisión RTSP activado.")
            return f"rtsp://{config['url_default']}:8080/h264.sdp"
        elif opcion == "2":
            logger.info("Modo HTTP activado.") 
            return f"http://{config['url_default']}:8080/photo.jpg"
        else:
            logger.error("Opción no válida.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error al manejar el menú de opciones: {e}")
        sys.exit(1)

def main():
    """
    Función principal para la ejecución de la aplicación.
    """
    try:
        # Ruta al archivo de configuración
        config_path = 'src/config.json'
        config = leer_configuracion(config_path)

        # Recopilar inputs del usuario
        grados_rotacion = float(input(
            f'Ingrese los grados de rotación (en sentido horario, "{config["grados_rotacion_default"]}" por defecto): ') 
            or config["grados_rotacion_default"])
        pixels_por_mm = float(input(
            f'Ingrese para corregir los pixeles por mm, "{config["pixels_por_mm_default"]}" por defecto: ') 
            or config["pixels_por_mm_default"])
        altura = float(input(
            f'Ingrese la altura para corregir el eje vertical en px "{config["altura_default"]}" por defecto: ') 
            or config["altura_default"])
        horizontal = float(input(
            f'Ingrese para corregir el eje horizontal en px, "{config["horizontal_default"]}" por defecto: ') 
            or config["horizontal_default"])
        
        # Actualizar la configuración
        nueva_config = {
            "grados_rotacion_default": grados_rotacion,
            "altura_default": altura,
            "horizontal_default": horizontal,
            "pixels_por_mm_default": pixels_por_mm
        }
        actualizar_configuracion(config_path, nueva_config)
        
        default_video_url = manejar_menu(config)
        
        root = tk.Tk()
        app = VideoStreamApp(root, default_video_url, grados_rotacion, altura, horizontal, pixels_por_mm)
        app.run()
    except Exception as e:
        logger.error(f"Error al iniciar la aplicación: {e}")
        sys.exit(1)
