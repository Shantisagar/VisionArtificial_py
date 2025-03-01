"""
Path: src/registro_desvios.py
Este módulo se encarga de registrar los desvíos de papel en la base de datos.
"""
from datetime import datetime
import mysql.connector
from pytz import timezone
from typing import Optional
from utils.logging.logger_configurator import LoggerConfigurator
from src.views.notifier import Notifier, ConsoleNotifier

# Configuración del logger
logger = LoggerConfigurator().configure()

# Instancia predeterminada del notificador
default_notifier = ConsoleNotifier(logger)

def inicializar_bd():
    """
    Crea la base de datos y la tabla si no existen.
    """
    try:
        # Conectar al servidor MySQL sin especificar una base de datos
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345678"
        )
        cursor = conn.cursor()

        # Crear la base de datos si no existe
        cursor.execute("CREATE DATABASE IF NOT EXISTS registro_va")

        # Usar la base de datos
        cursor.execute("USE registro_va")

        # Crear la tabla si no existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS desvio_papel (
                id INT AUTO_INCREMENT PRIMARY KEY,
                unixtime INT,
                datetime DATETIME,
                desvio FLOAT,
                direccion TINYINT,
                enable TINYINT
            )
        ''')

        conn.commit()
        logger.info("Base de datos y tabla inicializadas correctamente.")

    except mysql.connector.Error as err:
        logger.error(f"Error al inicializar la base de datos: {err}")

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def registrar_desvio(desvio_mm, TOLERANCIA, notifier: Optional[Notifier] = None) -> str:
    """
    Registra el desvío en la base de datos y notifica según corresponda.
    
    Args:
        desvio_mm: Valor del desvío en milímetros
        TOLERANCIA: Valor de tolerancia para determinar si el desvío es significativo
        notifier: Instancia de Notifier para manejar las notificaciones (opcional)
        
    Returns:
        Mensaje descriptivo del desvío
    """
    # Usar el notificador proporcionado o el predeterminado
    notifier = notifier or default_notifier
    
    # Generar la notificación del desvío
    mensaje = notifier.notify_desvio(desvio_mm, TOLERANCIA)
    
    # Registrar en la base de datos (separado de la notificación)
    enviar_datos(desvio_mm)
    
    return mensaje

def enviar_datos(desvio_mm):
    " Guarda los datos en la base de datos."
    try:
        # Convertir float64 de NumPy a float nativo de Python
        desvio_mm_float = float(desvio_mm)

        # Conectar a la base de datos
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345678",
            database="registro_va"
        )
        cursor = conn.cursor()

        unixtime = int(datetime.now().timestamp())
        # Obtener la zona horaria de Buenos Aires
        tz = timezone('America/Argentina/Buenos_Aires')

        # Obtener la fecha y hora en la zona horaria de Buenos Aires
        dt = datetime.fromtimestamp(unixtime, tz)

        # Calcular direccion
        direccion = 1 if desvio_mm_float > 0 else 0

        # Calcular enable
        enable_val = 1 if abs(desvio_mm_float) > 2 else 0

        # Insertar datos en la tabla
        cursor.execute('''
            INSERT INTO desvio_papel (unixtime, datetime, desvio, direccion, enable)
            VALUES (%s, %s, %s, %s, %s)
        ''', (unixtime, dt, desvio_mm_float, direccion, enable_val))

        # Confirmar la transacción
        conn.commit()

    except mysql.connector.Error as err:
        logger.error(f"Error al conectar a la base de datos: {err}")
    except Exception as e:
        logger.error(f"Error inesperado al guardar datos: {e}")
    finally:
        # Cerrar la conexión
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# Inicializar la base de datos cuando se importa el módulo
inicializar_bd()
