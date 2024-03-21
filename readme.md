# VisionArtificial - Detección de Desvíos en la Producción de Bolsas de Papel

Este proyecto de visión artificial tiene como objetivo identificar desvíos en la alineación de la materia prima durante el proceso productivo de confección de bolsas de papel, utilizando técnicas avanzadas de procesamiento de imágenes para asegurar la calidad y precisión en la producción.

## Objetivo

Desarrollar una herramienta capaz de detectar si el papel está centrado o si se ha desplazado de su alineación central. En caso de desvío, la herramienta determina cuánto se ha desviado, permitiendo correcciones en tiempo real para mantener la eficiencia y calidad del proceso productivo.

## Tecnologías Utilizadas

- **Python**: Lenguaje de programación utilizado para el desarrollo del proyecto.
- **OpenCV (cv2)**: Biblioteca de visión por computadora utilizada para el procesamiento de imágenes y videos.
- **NumPy**: Utilizado para el manejo eficiente de arrays y matrices, fundamental en el procesamiento de imágenes.
- **Pillow (PIL)**: Biblioteca para la apertura, manipulación y guardado de muchas diferentes formatos de archivo de imágenes.

## Estructura del Proyecto

El proyecto se organiza de la siguiente manera:

```bash
VisionArtificial/
    installer.py
    readme.md
    config/
    DOCS/
        00-Prompt-for-ProjectAnalysis.md
        license.md
        screenshots/
    src/
        image_processing.py
        main.py
        logs/
            config_logger.py
            __init__.py
            __pycache__/
    tests/
    __pycache__/
```

## Capturas de Pantalla

La siguiente captura de pantalla muestra la interfaz de la aplicación IP Webcam en funcionamiento, ilustrando cómo se puede utilizar un dispositivo móvil Android como cámara para capturar imágenes en tiempo real.

![App Android](https://github.com/AgustinMadygraf/VisionArtificial/blob/main/DOCS/screenshots/ip_webcam_app_screenshot.jpg)

Y aquí hay una vista previa de la aplicación de visión artificial en ejecución, demostrando la detección de desvíos en un entorno de producción simulado:

![Ejecución de la Aplicación](https://github.com/AgustinMadygraf/VisionArtificial/blob/main/DOCS/screenshots/EjecucionAppVisionArtificial_Resultados.png)

## Cómo Empezar

### Pre-requisitos

- Asegúrate de tener Python 3.9 instalado en tu sistema.
- Pipenv para la gestión de entornos virtuales y dependencias.

### Configuración del Entorno

1. **Instalación de Pipenv**: Si aún no lo has hecho, instala Pipenv ejecutando:
   ```bash
   pip install pipenv
   ```

2. **Clonar el Repositorio**: Clona este repositorio a tu máquina local usando:
   ```bash
   git clone https://github.com/AgustinMadygraf/VisionArtificial.git
   ```

3. **Instalar Dependencias**: Navega al directorio del proyecto y ejecuta:
   ```bash
   pipenv install
   ```
   Esto creará un entorno virtual para el proyecto e instalará las dependencias necesarias como OpenCV, NumPy y Pillow.

### Ejecutar la Aplicación

Una vez configurado el entorno, puedes iniciar la aplicación con:
```bash
pipenv run python src/main.py
```

O activar el entorno virtual y ejecutar la aplicación dentro de él:
```bash
pipenv shell
python src/main.py
```

## Integración con IP Webcam

Este proyecto puede utilizar [IP Webcam](https://play.google.com/store/apps/details?id=com.pas.webcam) para la captura de imágenes en tiempo real. Asegúrate de seguir las instrucciones de configuración de la aplicación IP Webcam para adecuarla a las necesidades específicas del proyecto.

## Contribuciones

Las contribuciones son muy bienvenidas. Si tienes una mejora, corrección o característica nueva que añadir, no dudes en fork el repositorio y enviar un pull request con tus cambios.

## Licencia

Este proyecto está liberado bajo la licencia [ESPECIFICAR TIPO DE LICENCIA]. Consulta el archivo `LICENSE` para más detalles.