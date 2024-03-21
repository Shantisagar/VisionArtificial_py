#VisionArtificial\main.py
import tkinter as tk
from video_stream import VideoStreamApp
import sys
from screeninfo import get_monitors
import json
import os

for monitor in get_monitors():
    print(f"Monitor {monitor.name}: {monitor.width}x{monitor.height}")
    
#crear funcion que tome los valores de config.json y los almacene en variables
def leer_configuracion():
    ruta_configuracion = 'src/config.json'
    configuracion_predeterminada = {
        "grados_rotacion_default": -2,
        "altura_default": 25,
        "altura2_default": 120,
        "perspectiva_default": 80,
        "rtsp_url_default": "rtsp://192.168.0.11:8080/h264.sdp",
        "ubicacion_default": "C:/AppServ/www/VisionArtificial/tests/calibracion_deteccion_papel.jpg"
    }

    # Verificar si el archivo de configuración existe
    if not os.path.exists(ruta_configuracion):
        # Si no existe, crear el archivo con la configuración predeterminada
        with open(ruta_configuracion, 'w') as archivo:
            json.dump(configuracion_predeterminada, archivo, indent=4)
        print("Archivo de configuración creado con valores predeterminados.")

    # Ahora, leer la configuración desde el archivo
    with open(ruta_configuracion, 'r') as archivo:
        datos = json.load(archivo)
    
    return datos


def manejar_menu(config):
    opcion = input("Seleccione una opción:\n0 - Testing\n1 - RTSP\n2 - HTTP (No disponible aún)\nOpción: ") or "0"
    if opcion == "0":
        print("Modo de calibración de reconocimiento de imagen activado.")
        # Usa el valor de la configuración para la ubicación de calibración
        return config["ubicacion_default"]
    elif opcion == "1":
        print("Modo de transmisión RTSP activado.")
        # Usa el valor de la configuración para la URL RTSP
        return config["rtsp_url_default"]
    elif opcion == "2":
        print("HTTP no está disponible aún.")
        return None
    else:
        print("Opción no válida.")
        sys.exit(1)


if __name__ == "__main__":
    config = leer_configuracion()
    # Ahora, extrae cada valor de configuración que necesitas
    grados_rotacion         = float(input(f'Ingrese los grados de rotación (en sentido antihorario, "   {config["grados_rotacion_default"]} " por defecto): ') or config["grados_rotacion_default"])
    altura                  = float(input(f'Ingrese la altura para corregir el eje vertical, "          {config["altura_default"]}          " por defecto): ') or config["altura_default"])
    perspectiva_default     = float(input(f'Ingrese la altura para corregir la perspectiva, "           {config["perspectiva_default"]}     " por defecto): ') or config["perspectiva_default"])
    altura2                 = float(input(f'Ingrese la altura para corregir el eje vertical, "          {config["altura2_default"]}         " por defecto): ') or config["altura2_default"])
    default_video_url = manejar_menu(config)
    root = tk.Tk()
    app = VideoStreamApp(root, default_video_url, grados_rotacion, altura,perspectiva_default)
    app.run()

