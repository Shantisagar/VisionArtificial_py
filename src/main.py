# VisionArtificial\main.py
import tkinter as tk
from video_stream import VideoStreamApp
import sys
from screeninfo import get_monitors
import json
import os
import logging
from logs.config_logger import configurar_logging

# Configuración del logger
logger = configurar_logging()

def leer_configuracion():
    """
    Lee la configuración desde el archivo 'config.json' y devuelve un diccionario con los valores configurados.
    Si el archivo no existe, se crea uno con valores predeterminados.
    """
    ruta_configuracion = 'src/config.json'
    configuracion_predeterminada = {
        "grados_rotacion_default": 0,
        "altura_default": 0,
        "altura2_default": 100,
        "perspectiva_default": 0,
        "rtsp_url_default": "rtsp://192.168.0.11:8080/h264.sdp",
        "ubicacion_default": "C:/AppServ/www/VisionArtificial/tests/calibracion_deteccion_papel.jpg"
    }

    try:
        if not os.path.exists(ruta_configuracion):
            with open(ruta_configuracion, 'w') as archivo:
                json.dump(configuracion_predeterminada, archivo, indent=4)
            logger.info("Archivo de configuración creado con valores predeterminados.")

        with open(ruta_configuracion, 'r') as archivo:
            datos = json.load(archivo)
    except Exception as e:
        logger.error(f"Error al leer o crear el archivo de configuración: {e}")
        sys.exit(1)
    
    return datos

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
