# VisionArtificial\main.py
import tkinter as tk
from video_stream import VideoStreamApp
import sys
from screeninfo import get_monitors
from logs.config_logger import configurar_logging
from config_manager import leer_configuracion

# Configuración del logger
logger = configurar_logging()

def manejar_menu(config):
    """
    Maneja el menú de opciones de usuario y devuelve la URL del video o ruta de la imagen seleccionada.
    """
    try:
        opcion = input("Seleccione una opción:\n0 - Testing\n1 - RTSP\n2 - HTTP (No disponible aún)\nOpción: ") or "0"
        if opcion == "0":
            logger.info("Modo de calibración de reconocimiento de imagen activado.")
            return config["ubicacion_default"]
        elif opcion == "1":
            logger.info("Modo de transmisión RTSP activado.")
            return config["rtsp_url_default"]
        elif opcion == "2":
            logger.info("HTTP no está disponible aún.")
            return None
        else:
            logger.error("Opción no válida.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error al manejar el menú de opciones: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        config = leer_configuracion()
        grados_rotacion = float(input(f'Ingrese los grados de rotación (en sentido antihorario, "   {config["grados_rotacion_default"]} " por defecto): ') or config["grados_rotacion_default"])
        altura = float(input(f'Ingrese la altura para corregir el eje vertical, "          {config["altura_default"]}          " por defecto): ') or config["altura_default"])
        perspectiva_default = float(input(f'Ingrese la altura para corregir la perspectiva, "           {config["perspectiva_default"]}     " por defecto): ') or config["perspectiva_default"])
        altura2 = float(input(f'Ingrese la altura para corregir el eje vertical, "          {config["altura2_default"]}         " por defecto): ') or config["altura2_default"])
        default_video_url = manejar_menu(config)

        root = tk.Tk()
        app = VideoStreamApp(root, default_video_url, grados_rotacion, altura, perspectiva_default)
        app.run()
    except Exception as e:
        logger.error(f"Error al iniciar la aplicación: {e}")
        sys.exit(1)
