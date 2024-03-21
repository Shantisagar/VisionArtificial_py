#VisionArtificial\main.py
import tkinter as tk
from video_stream import VideoStreamApp
import sys
from screeninfo import get_monitors

for monitor in get_monitors():
    print(f"Monitor {monitor.name}: {monitor.width}x{monitor.height}")


def manejar_menu():
    opcion = input("Seleccione una opción:\n0 - Testing\n1 - RTSP\n2 - HTTP (No disponible aún)\nOpción: ") or "0"
    if opcion == "0":
        print("Modo de calibración de reconocimiento de imagen activado.")
        return "C:/AppServ/www/VisionArtificial/tests/calibracion_deteccion_papel.jpg"
    elif opcion == "1":
        print("Modo de transmisión RTSP activado.")
        return "rtsp://192.168.0.11:8080/h264.sdp"
    elif opcion == "2":
        print("HTTP no está disponible aún.")
        return None
    else:
        print("Opción no válida.")
        sys.exit(1)

if __name__ == "__main__":
    #grados_rotacion = input("Ingrese los grados de rotación (en sentido antihorario, 0 por defecto): ")
    #grados_rotacion = float(grados_rotacion) if grados_rotacion.strip() else 0
    #altura = input("Ingrese la altura para corregir el eje vertical): ")
    #altura = float(altura) if altura.strip() else 0
    default_video_url = manejar_menu()
    root = tk.Tk()
    app = VideoStreamApp(root, default_video_url, grados_rotacion = -2)  # Asegúrate de que esta línea coincide
    app.run()
