#VisionArtificial\config_manager.py
import json
import os
import sys
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
        "grados_rotacion_default": -2,
        "altura_default": 25,
        "altura2_default": 120,
        "perspectiva_default": 80,
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