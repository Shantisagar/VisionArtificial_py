"""
Path: src/main.py
Punto de entrada principal de la aplicación
Configura la aplicación e inicia la interfaz gráfica
"""

from src.views.gui_view import GUIView
from src.controllers.app_controller import AppController
from utils.logging.dependency_injection import get_logger
from utils.logging.error_manager import init_error_manager, handle_exception, critical_error

def main():
    """Función principal que inicia la aplicación"""
    try:
        # Obtener logger centralizado
        logger = get_logger()
        logger.info("Iniciando aplicación de Visión Artificial...")
        
        # Inicializar el gestor de errores con el logger
        init_error_manager(logger)
        logger.info("Gestor de errores inicializado")

        # Crear controlador
        controller = AppController(logger)

        # Crear vista y configurarla
        view = GUIView(logger)

        # Este es el paso clave: el controlador configura la vista y establece los callbacks
        controller.setup_view(view)

        # Ejecutar la aplicación
        controller.run()

        logger.info("Aplicación finalizada correctamente")
        return 0

    except (OSError, RuntimeError) as e:
        # Usar el gestor de errores para manejar la excepción
        critical_error(e, {"context": "main", "fase": "inicialización"})
        return 1
    except Exception as e:  # Capturar cualquier otra excepción inesperada
        # Usar el gestor de errores para manejar excepciones desconocidas
        critical_error(e, {"context": "main", "tipo": "excepción no controlada"})
        return 1
