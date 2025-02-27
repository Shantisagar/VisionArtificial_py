
from utils.logging.logger_configurator import LoggerConfigurator
import mysql.connector
from datetime import datetime
from pytz import timezone
import pytz

# Configuración del logger
logger = LoggerConfigurator().configure()

def registrar_desvio(desvio_mm, TOLERANCIA):
    # Mostrar el desvío en la consola
    if desvio_mm > TOLERANCIA:
        logger.info(f"Desvío registrado: {desvio_mm} mm ENG")
        texto1 = f" Desvio: {desvio_mm} mm ENG"

    elif desvio_mm < -TOLERANCIA:
        logger.info(f"Desvío registrado: {desvio_mm} mm OP")
        texto1 = f"Desvio: {desvio_mm} mm OP"
    else:  # Esto cubre el caso donde el desvío está dentro de la tolerancia de +/- 2mm
        logger.info(f"Desvío registrado: {desvio_mm} mm - Centrado")
        if desvio_mm > 0:
            texto1 = f"Desvio: {desvio_mm} mm - Centrado ENG"
        elif desvio_mm < 0:
            texto1 = f"Desvio: {desvio_mm} mm - Centrado OP"
        else:
            texto1 = f"Desvio: {desvio_mm} mm - Centrado"

        # Ejemplo de datos a insertar
    enviar_datos(desvio_mm)
    return texto1





def enviar_datos(desvio_mm):
    try:
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
        direccion = 1 if desvio_mm > 0 else 0
        
        # Calcular enable
        enable_val = 1 if abs(desvio_mm) > 2 else 0

        # Insertar datos en la tabla
        cursor.execute('''
            INSERT INTO desvio_papel (unixtime, datetime, desvio, direccion, enable)
            VALUES (%s, %s, %s, %s, %s)
        ''', (unixtime, dt, desvio_mm, direccion, enable_val))

        # Confirmar la transacción
        conn.commit()
        logger.info("Datos de desvío registrados en la base de datos.")

    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos: {err}")

    finally:
        # Cerrar la conexión
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


