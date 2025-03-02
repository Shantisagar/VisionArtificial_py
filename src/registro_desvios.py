"""
Path: src/registro_desvios.py
Este módulo se encarga de registrar los desvíos de papel en la base de datos.

Estrategia de Logging y Notificaciones:
--------------------------------------
Este módulo implementa el enfoque dual de registro/notificación:
1. Logging técnico: Todos los eventos relevantes para depuración y monitoreo
   se registran mediante el sistema centralizado de logging.
2. Notificaciones: Los eventos significativos para el usuario se canalizan 
   a través del sistema de notificaciones (Notifier).

La separación de estas responsabilidades permite que la información técnica
detallada se registre sin abrumar al usuario final, mientras que los mensajes
importantes se presentan de manera clara y consistente en la interfaz.
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
    
    Esta función registra todas las operaciones importantes en el logger
    para facilitar la depuración y el seguimiento de problemas de conexión.
    """
    conn = None
    cursor = None
    try:
        # Conectar al servidor MySQL sin especificar una base de datos
        logger.info("Intentando conexión al servidor MySQL para inicializar la BD...")
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
        logger.error("Error al inicializar la base de datos: %s", err)
        # Clasificar y registrar errores específicos de MySQL
        error_msg = str(err).lower()
        if "can't connect" in error_msg:
            logger.error("No se pudo establecer conexión con el servidor MySQL.")
        elif "access denied" in error_msg:
            logger.error("Acceso denegado. Verificar credenciales de la base de datos.")

    except Exception as e:
        logger.error("Error inesperado durante la inicialización de la BD: %s", e)

    finally:
        # Cerrar el cursor de manera segura
        if cursor:
            try:
                cursor.close()
            except Exception as e:
                logger.error("Error al cerrar el cursor de la BD: %s", e)

        # Cerrar la conexión de manera segura
        if conn:
            try:
                if hasattr(conn, 'is_connected') and conn.is_connected():
                    conn.close()
                    logger.debug("Conexión a la BD cerrada correctamente.")
            except Exception as e:
                logger.error(f"Error al cerrar la conexión de BD: {e}")

def registrar_desvio(desvio_mm, TOLERANCIA, notifier: Optional[Notifier] = None) -> str:
    """
    Registra el desvío en la base de datos y notifica según corresponda.
    
    Esta función ejemplifica la separación de responsabilidades:
    1. Notificación al usuario: A través del objeto Notifier
    2. Registro en la BD: Operación técnica que se registra en el logger
    
    Args:
        desvio_mm: Valor del desvío en milímetros
        TOLERANCIA: Valor de tolerancia para determinar si el desvío es significativo
        notifier: Instancia de Notifier para manejar las notificaciones (opcional)
        
    Returns:
        Mensaje descriptivo del desvío
    """
    # Usar el notificador proporcionado o el predeterminado
    notifier = notifier or default_notifier

    # Registrar en el logger que se está procesando un desvío
    logger.debug(f"Procesando desvío de {desvio_mm}mm (tolerancia: {TOLERANCIA}mm)")

    # Generar la notificación del desvío
    mensaje = notifier.notify_desvio(desvio_mm, TOLERANCIA)

    # Registrar en la base de datos (separado de la notificación)
    enviar_datos(desvio_mm)

    return mensaje

def enviar_datos(desvio_mm):
    """
    Guarda los datos del desvío en la base de datos.

    Toda operación con la BD genera entradas apropiadas en el log,
    pero no necesariamente notificaciones al usuario final.

    Args:
        desvio_mm: Valor del desvío en milímetros
    """
    conn = None
    cursor = None
    try:
        # Convertir float64 de NumPy a float nativo de Python
        desvio_mm_float = float(desvio_mm)

        logger.debug(f"Intentando guardar desvío de {desvio_mm_float}mm en la BD...")

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
        #logger.info(f"Datos de desvío {desvio_mm_float}mm guardados correctamente en la BD.")

    except mysql.connector.Error as err:
        logger.error(f"Error de MySQL al guardar datos: {err}")
        # Clasificar y registrar errores específicos de MySQL para facilitar el diagnóstico
        error_msg = str(err).lower()
        if "can't connect" in error_msg:
            logger.error("No se pudo establecer conexión con el servidor MySQL.")
        elif "access denied" in error_msg:
            logger.error("Acceso denegado. Verificar credenciales de la base de datos.")
        elif "unknown database" in error_msg:
            logger.error("La base de datos especificada no existe.")

    except ValueError as e:
        logger.error(f"Error al convertir el valor de desvío a float: {e}")

    except Exception as e:
        logger.error(f"Error inesperado al guardar datos en la BD: {e}")

    finally:
        # Cerrar el cursor de manera segura
        if cursor:
            try:
                cursor.close()
                logger.debug("Cursor de la base de datos cerrado correctamente.")
            except Exception as e:
                logger.error(f"Error al cerrar el cursor de la BD: {e}")

        # Cerrar la conexión de manera segura
        if conn:
            try:
                if hasattr(conn, 'is_connected') and conn.is_connected():
                    conn.close()
                    logger.debug("Conexión a la base de datos cerrada correctamente.")
            except Exception as e:
                logger.error(f"Error al cerrar la conexión de BD: {e}")

# Inicializar la base de datos cuando se importa el módulo
inicializar_bd()
