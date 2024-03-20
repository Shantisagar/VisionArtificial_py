import subprocess
import os
from pathlib import Path
from src.logs.config_logger import configurar_logging
import winshell
from win32com.client import Dispatch
from pywintypes import com_error

# Configuración del logger
logger = configurar_logging()

def crear_acceso_directo(ruta_archivo_bat, directorio_script):
    escritorio = Path(winshell.desktop())
    ruta_acceso_directo = escritorio / "VisionArtificial.lnk"
    ruta_icono = directorio_script / "config" / "VisionArtificial.ico"

    # Verificación de existencia del archivo de icono
    if not ruta_icono.is_file():
        logger.error(f"El archivo de icono '{ruta_icono}' no existe.")
        return False

    try:
        shell = Dispatch('WScript.Shell')
        acceso_directo = shell.CreateShortCut(str(ruta_acceso_directo))
        acceso_directo.Targetpath = str(ruta_archivo_bat)
        acceso_directo.WorkingDirectory = str(directorio_script)
        acceso_directo.IconLocation = str(ruta_icono)
        acceso_directo.save()
        logger.info(f"Acceso directo {'actualizado' if ruta_acceso_directo.exists() else 'creado'} exitosamente.")
        return True
    except com_error as e:
        logger.error(f"No se pudo crear/actualizar el acceso directo debido a un error de COM: {e}", exc_info=True)
    except OSError as e:
        logger.error(f"No se pudo crear/actualizar el acceso directo debido a un error del sistema operativo: {e}", exc_info=True)
        return False

def crear_archivo_bat_con_pipenv(directorio_script):
    ruta_main_py = directorio_script / 'src' / 'main.py'
    ruta_archivo_bat = directorio_script / 'VisionArtificial.bat'

    contenido_bat = f"""
@echo off
cd /d "%~dp0"
echo Verificando entorno virtual de Pipenv...
pipenv --venv
if errorlevel 1 (
   echo Creando entorno virtual...
   pipenv install
)
echo Ejecutando aplicacion...
pipenv run python "{ruta_main_py}"
echo.
pause
"""

    with open(ruta_archivo_bat, 'w') as archivo_bat:
        archivo_bat.write(contenido_bat.strip())
    logger.info("Archivo 'VisionArtificial.bat' creado exitosamente.")

def limpieza_pantalla():
    try:
        if os.name == 'nt':  # Windows
            subprocess.call('cls', shell=True)
        else:  # macOS y Linux
            subprocess.call('clear', shell=True)
        logger.info("Pantalla limpiada.")
    except Exception as e:
        logger.error(f"Error al limpiar la pantalla: {e}")

def main():
    directorio_script = Path(__file__).parent.resolve()
    limpieza_pantalla()
    logger.info("Iniciando instalador")

    # Crear archivo BAT
    ruta_archivo_bat = directorio_script / 'VisionArtificial.bat'
    if not ruta_archivo_bat.is_file():
        logger.info("Creando archivo 'VisionArtificial.bat'")
        crear_archivo_bat_con_pipenv(directorio_script)
    
    crear_acceso_directo(ruta_archivo_bat, directorio_script)

if __name__ == "__main__":
    main()
