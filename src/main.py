"""
Archivo de entrada para iniciar la aplicación separando la lógica de entrada,
configuración e inicialización de la UI.
"""

import sys
import tkinter as tk
from src.video_stream import VideoStreamApp
from src.logs.config_logger import configurar_logging
from src.config_manager import ConfigManager

logger = configurar_logging()

def obtener_opcion_video(config):
    """
    Maneja el menú de opciones de usuario y devuelve la URL o ruta de la imagen.
    """
    try:
        opcion = input(
            "Seleccione una opción:\n0 - Testing\n1 - RTSP\n2 - HTTP\nOpción: "
        ) or "2"
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
        logger.error("Error al manejar el menú de opciones: %s", e)
        sys.exit(1)

def recoger_parametros_usuario(config):
    """
    Recoge los parámetros necesarios desde la entrada estándar, utilizando valores por defecto
    en caso de no especificar una entrada.
    """
    try:
        grados_rotacion = float(
            input(f'Ingrese los grados de rotación (valor por defecto "{config["grados_rotacion_default"]}"): ')
            or config["grados_rotacion_default"]
        )
        pixels_por_mm = float(
            input(f'Ingrese el valor de pixeles por mm (valor por defecto "{config["pixels_por_mm_default"]}"): ')
            or config["pixels_por_mm_default"]
        )
        altura = float(
            input(f'Ingrese la altura para corregir eje vertical (valor por defecto "{config["altura_default"]}"): ')
            or config["altura_default"]
        )
        horizontal = float(
            input(f'Ingrese el desplazamiento horizontal (valor por defecto "{config["horizontal_default"]}"): ')
            or config["horizontal_default"]
        )
        return grados_rotacion, pixels_por_mm, altura, horizontal
    except Exception as e:
        logger.error("Error al recoger parámetros del usuario: %s", e)
        sys.exit(1)

def main():
    """
    Función principal que orquesta la inicialización de la configuración, recogida de datos e interfaz.
    """
    try:
        config_path = 'src/config.json'
        config_manager = ConfigManager(config_path)
        config = config_manager.get_config()

        # Recoger parámetros de entrada
        grados_rotacion, pixels_por_mm, altura, horizontal = recoger_parametros_usuario(config)
        nueva_config = {
            "grados_rotacion_default": grados_rotacion,
            "altura_default": altura,
            "horizontal_default": horizontal,
            "pixels_por_mm_default": pixels_por_mm
        }
        config_manager.update_config(nueva_config)

        # Seleccionar el modo de video según opción elegida
        default_video_url = obtener_opcion_video(config)

    except Exception as e:
        logger.error("Error al iniciar la aplicación: %s", e)
        sys.exit(1)

    # Inicializar la interfaz y ejecutar la aplicación
    root = tk.Tk()
    app = VideoStreamApp(root, default_video_url, grados_rotacion, altura, horizontal, pixels_por_mm)
    app.run()

if __name__ == '__main__':
    main()