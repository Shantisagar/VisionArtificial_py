# Documentación de la Arquitectura y Funciones Clave

Este documento es una herramienta para desarrolladores con el objetivo de entender la arquitectura del proyecto y conocer dónde buscar las funciones y componentes que pueden necesitar cambios o mejoras.

## Índice

1. [Arquitectura General](#arquitectura-general)
2. [Descripción de Módulos y Funciones](#descripción-de-módulos-y-funciones)
   1. [src/](#src)
   2. [src/capture/](#srccapture)
   3. [src/controllers/](#srctrollers)
   4. [src/views/](#srcviews)
3. [Áreas para Mejoras Identificadas](#áreas-para-mejoras-identificadas)
   1. [Función "Ajustar Altura" en el GUI](#función-ajustar-altura-en-el-gui)
   2. [Botones [ - ] y [ + ] al lado de la barra horizontal](#botones--y--al-lado-de-la-barra-horizontal)
   3. [Visualización de FPS y Métricas de CPU](#visualización-de-fps-y-métricas-de-cpu)
   4. [Incorporar una barra horizontal de "zoom"](#incorporar-una-barra-horizontal-de-zoom)
   5. [Selector de color de papel](#selector-de-color-de-papel)
   6. [Maximizar la ventana de la GUI después de 2 segundos](#maximizar-la-ventana-de-la-gui-después-de-2-segundos)
4. [Notas Adicionales](#notas-adicionales)

---

## Arquitectura General

El proyecto cuenta con la siguiente estructura de carpetas y archivos:

```bash
src/
    deteccion_bordes.py                           2.92kB - 056 líneas de código
    image_processing.py                           6.43kB - 123 líneas de código
    main.py                                       1.34kB - 030 líneas de código
    registro_desvios.py                           7.80kB - 150 líneas de código
    rotacion.py                                   1.22kB - 029 líneas de código
    video_stream.py                               10.92kB - 211 líneas de código
    __init__.py                                   0.06kB - 003 líneas de código
    capture/
        http_video_capture.py                     7.11kB - 145 líneas de código
        local_video_capture.py                    6.00kB - 135 líneas de código
        video_capture_factory.py                  1.89kB - 039 líneas de código
        video_capture_interface.py                1.66kB - 052 líneas de código
    controllers/
        app_controller.py                         4.99kB - 105 líneas de código
        gui_parameter_panel_controller.py         13.31kB - 236 líneas de código
        video_processor.py                        8.39kB - 178 líneas de código
    docs/
        00-Prompt-for-ProjectAnalysis.md          145.92kB - N/A
    views/
        control_panel_view.py                     6.22kB - 116 líneas de código
        gui_notifier.py                           7.17kB - 133 líneas de código
        gui_parameter_panel.py                    4.84kB - 094 líneas de código
        gui_parameter_panel_view.py               10.90kB - 198 líneas de código
        gui_view.py                               7.49kB - 129 líneas de código
        main_display_view.py                      6.25kB - 134 líneas de código
        notifier.py                               5.70kB - 129 líneas de código
        parameter_panel_layout.py                 8.11kB - 149 líneas de código
        parameter_row_factory.py                  7.93kB - 140 líneas de código
        tool_tip.py                               2.09kB - 062 líneas de código
        __init__.py                               0.06kB - 003 líneas de código
```

---

## Descripción de Módulos y Funciones

### src/
- **deteccion_bordes.py**  
  Contiene funciones para la detección de bordes en imágenes.  
  Consulta deteccion_bordes.py.

- **image_processing.py**  
  Módulo para procesar imágenes: transformación, rotación (usando `rotacion.rotar_imagen`) y anotación (ver src/image_processing.py).  

- **registro_desvios.py**  
  Funciones para registrar desviaciones encontradas durante el procesamiento.  
  Consulta registro_desvios.py.

- **video_stream.py**  
  Maneja la transmisión del video y su procesamiento en una cola; también se encarga de la actualización de la UI.  
  Consulta video_stream.py.

- **main.py**  
  Punto de entrada de la aplicación, configura el ambiente y lanza la interfaz gráfica.  
  Consulta main.py.

### src/capture/
- **http_video_capture.py y local_video_capture.py**  
  Implementan clases para capturar video desde distintas fuentes; ambos implementan la interfaz definida en `video_capture_interface.py`.

- **video_capture_factory.py**  
  Contiene la fábrica para instanciar la fuente de video adecuada según la configuración y el entorno.

### src/controllers/
- **app_controller.py**  
  Coordina la inicialización general de la aplicación, integrando vista, controladores y manejo de eventos.  
  Consulta app_controller.py.

- **gui_parameter_panel_controller.py**  
  Controlador específico para la gestión de parámetros en la interfaz; interactúa con el `gui_parameter_panel_view.py`.  
  Consulta gui_parameter_panel_controller.py.

- **video_processor.py**  
  Se encarga del procesamiento de frames de video; desacopla la lógica de procesamiento del componente de UI y captura.  
  Consulta video_processor.py.

### src/views/
- **gui_view.py**  
  Es el contenedor principal de la interfaz gráfica y organiza la interacción entre los distintos paneles.  
  Consulta gui_view.py.

- **control_panel_view.py**  
  Muestra los controles de configuración y estadísticas (como FPS y posiblemente futuros indicadores de rendimiento).  
  Consulta control_panel_view.py.

- **gui_parameter_panel.py y gui_parameter_panel_view.py**  
  Manejan la visualización y edición de parámetros (por ejemplo, `altura`, `grados_rotacion`, etc.) en la UI.  
  Consulta gui_parameter_panel.py y gui_parameter_panel_view.py.

- **main_display_view.py**  
  Se encarga de mostrar el video procesado y aplicar las transformaciones en tiempo real.  
  Consulta main_display_view.py.

- **parameter_panel_layout.py y parameter_row_factory.py**  
  Definen la estructura y disposición de los controles de parámetros en la interfaz.  
  Consulta parameter_panel_layout.py y parameter_row_factory.py.

- **gui_notifier.py, notifier.py y tool_tip.py**  
  Gestionan la comunicación de mensajes y tooltips en la UI.  
  Consulta gui_notifier.py, notifier.py y tool_tip.py.

---
