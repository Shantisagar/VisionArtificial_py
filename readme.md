# VisionArtificial - Detección de Desvíos en la Producción de Bolsas de Papel

Este proyecto de visión artificial tiene como objetivo identificar desvíos en la alineación de la materia prima durante el proceso productivo de confección de bolsas de papel, utilizando técnicas avanzadas de procesamiento de imágenes para asegurar la calidad y precisión en la producción.

## Objetivo

Desarrollar una herramienta capaz de detectar si el papel está centrado o si se ha desplazado de su alineación central. En caso de desvío, la herramienta determina cuánto se ha desviado, permitiendo correcciones en tiempo real para mantener la eficiencia y calidad del proceso productivo.

## Tecnologías Utilizadas

- **Python**: Lenguaje de programación utilizado para el desarrollo del proyecto.
- **OpenCV (cv2)**: Biblioteca de visión por computadora utilizada para el procesamiento de imágenes y videos.
- **NumPy**: Utilizado para el manejo eficiente de arrays y matrices, fundamental en el procesamiento de imágenes.

## Estructura del Proyecto

El proyecto se organiza de la siguiente manera:

```
VisionArtificial/
├── app.py                     # Aplicación principal con GUI para visualización de procesamiento en tiempo real.
├── image_processing.py        # Script de procesamiento de imágenes, incluye lógica para detección de desvíos.
├── readme.md                  # Este archivo.
└── DOCS/                      # Documentación adicional y guías de uso.
```

## Cómo Empezar

### Pre-requisitos

Asegúrate de tener Python 3.6 o superior instalado en tu sistema. Además, necesitarás instalar las siguientes bibliotecas:

- OpenCV
- NumPy
- Pillow (para la interfaz de usuario)

Puedes instalar estas dependencias ejecutando:

```bash
pip install opencv-python numpy Pillow
```

### Instrucciones de Uso

1. **Clonar el Repositorio**: Primero, clona este repositorio a tu máquina local usando:

   ```
   git clone https://github.com/AgustinMadygraf/VisionArtificial.git
   ```

2. **Ejecutar la Aplicación**: Navega al directorio del proyecto y ejecuta:

   ```
   python app.py
   ```

   Sigue las instrucciones en pantalla para iniciar el análisis de desvíos en tiempo real.


## Integración con IP Webcam

Este proyecto utiliza la aplicación [IP Webcam](https://play.google.com/store/apps/details?id=com.pas.webcam) para convertir un dispositivo móvil Android en una cámara en red, lo que permite capturar imágenes en tiempo real para su procesamiento. IP Webcam es una solución versátil que funciona en cualquier plataforma con VLC player o navegador web, incluso sin conexión a Internet a través de una red WiFi.

### Características de IP Webcam utilizadas:

- **Transmisión de Video**: Utilizamos la capacidad de IP Webcam para transmitir video que luego se analiza en tiempo real para la detección de desvíos.
- **Accesibilidad**: Emite en una red WiFi permitiendo el acceso remoto y en tiempo real a la transmisión de la cámara.
- **Formatos de Video**: Graba y transmite video en formatos compatibles con nuestro sistema de procesamiento de imágenes.
- **Flexibilidad**: Compatible con una amplia gama de software de terceros y reproductores de audio.

Asegúrate de seguir las instrucciones de configuración de la aplicación para adecuarla a las necesidades específicas del proyecto. La comunicación bidireccional de audio y la integración con sistemas de videovigilancia amplían las posibilidades de uso dentro del contexto industrial.

### Configuración de IP Webcam para el Proyecto:

1. Instala IP Webcam en tu dispositivo móvil desde la [Play Store](https://play.google.com/store/apps/details?id=com.pas.webcam).
2. Configura la aplicación según las instrucciones para iniciar la transmisión de video.
3. Conecta tu dispositivo móvil a la misma red WiFi que tu sistema de visión artificial.
4. Ingresa la URL de transmisión proporcionada por IP Webcam en el script de nuestro proyecto para comenzar a recibir datos de video.

La integración con IP Webcam permite al proyecto de visión artificial ser más accesible y fácil de configurar, aprovechando la tecnología disponible para mejorar los procesos de producción.



## Contribuciones

Las contribuciones son muy bienvenidas. Si tienes una mejora, corrección o característica nueva que añadir, no dudes en fork el repositorio y enviar un pull request con tus cambios.

## Licencia

Este proyecto está liberado bajo la licencia [ESPECIFICAR TIPO DE LICENCIA]. Consulta el archivo `LICENSE` para más detalles.
