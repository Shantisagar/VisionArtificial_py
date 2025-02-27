### 1. Tarea Principal: Refactorizar la separación de responsabilidades en main.py  
- **Dependencias:**  
  - Archivo principal de entrada (main.py).  
  - Módulo de configuración (src/config_manager.py).  
  - Módulo de logging (utils/logging/logger_configurator.py).  

#### 🔹 Subtareas:
- **Subtarea 1:** Extraer la lógica de recolección de parámetros y opciones de video a módulos o servicios independientes.  
  - **Archivos involucrados:**  
    - main.py  
  - **Acción a realizar:** Modificar (reubicar) el código.  
  - **Justificación:** Aislar las tareas de entrada de datos y selección de opciones mejora la adherencia al patrón MVC y facilita la prueba y mantenimiento de cada componente por separado.  
  - **Archivos de referencia:**  
    - El propio main.py con funciones como `obtener_opcion_video` y `recoger_parametros_usuario`.

- **Subtarea 2:** Crear un controlador central que orqueste la inicialización de la configuración, la recogida de datos y la activación de la UI.  
  - **Archivos involucrados:**  
    - main.py  
  - **Acción a realizar:** Modificar la estructura del flujo principal para delegar responsabilidades.  
  - **Justificación:** Facilita futuras extensiones (por ejemplo, integración con Deep Learning) y permite una evolución clara de cada capa.  
  - **Archivos de referencia:**  
    - Diseño MVC y documentación relacionada en el proyecto.

---

### 2. Tarea Principal: Aplicar principios SOLID mediante inyección de dependencias  
- **Dependencias:**  
  - Todos los módulos que actualmente usan dependencias globales (por ejemplo, Logger y ConfigManager).  

#### 🔹 Subtareas:
- **Subtarea 1:** Refactorizar el Logger, permitiendo que se inyecte la dependencia en lugar de instanciarlo directamente.  
  - **Archivos involucrados:**  
    - logger_configurator.py  
    - main.py  
  - **Acción a realizar:** Modificar el manejo del logger para aceptarlo desde un contenedor o pasarlo como parámetro.  
  - **Justificación:** Aumenta la flexibilidad para pruebas unitarias y reduce el acoplamiento en el código.  
  - **Archivos de referencia:**  
    - El módulo Logger actual y patrones de inyección de dependencias.

- **Subtarea 2:** Ajustar el ConfigManager para recibir parámetros de configuración mediante inyección, facilitando la extensión (por ejemplo, integrar otros orígenes de configuración).  
  - **Archivos involucrados:**  
    - config_manager.py  
    - main.py  
  - **Acción a realizar:** Modificar la inicialización y el uso de la configuración.  
  - **Justificación:** Permite cumplir con el DIP y mejora la capacidad de modificar o extender la fuente de configuración sin tocar el código base de entrada.  
  - **Archivos de referencia:**  
    - Configuración actual y documentación sobre inyección de dependencias.

---

### 3. Tarea Principal: Desacoplar la lógica de selección de modo de video  
- **Dependencias:**  
  - main.py y módulos relacionados con el procesamiento de video (src/video_stream.py).  

#### 🔹 Subtareas:
- **Subtarea 1:** Extraer la función `obtener_opcion_video` de main.py y moverla a un módulo controlador específico.  
  - **Archivos involucrados:**  
    - main.py  
    - Crear o modificar: `/src/controllers/video_option_controller.py` (nuevo)  
  - **Acción a realizar:** Modificar (reubicar) la lógica en un módulo dedicado.  
  - **Justificación:** Se mejora la separación entre la UI y la lógica de negocio, permitiendo la reutilización y una mayor claridad en el flujo de datos.  
  - **Archivos de referencia:**  
    - El contenido actual de `obtener_opcion_video` en main.py.

- **Subtarea 2:** Definir un contrato (por ejemplo, mediante una interfaz conceptual) que permita extender modos de video sin modificar el controlador.  
  - **Archivos involucrados:**  
    - `/src/controllers/video_option_controller.py`  
  - **Acción a realizar:** Modificar y documentar la intención de extensión.  
  - **Justificación:** Facilitar el cumplimiento del OCP y permitir la integración de nuevos métodos de entrada (Deep Learning, GPU, etc.).  
  - **Archivos de referencia:**  
    - Diseño actual y posibles futuros módulos de entrada.

---

### 4. Tarea Principal: Reestructurar la recolección de parámetros de entrada del usuario  
- **Dependencias:**  
  - main.py, junto con la interfaz de entrada en consola.  

#### 🔹 Subtareas:
- **Subtarea 1:** Dividir la función `recoger_parametros_usuario` en funciones más específicas o incluso en una clase dedicada a la validación y procesamiento de entradas.  
  - **Archivos involucrados:**  
    - main.py  
    - Opcional: crear `/src/controllers/input_controller.py`  
  - **Acción a realizar:** Modificar (dividir) la función en componentes más pequeños para manejar cada parámetro por separado.  
  - **Justificación:** Mejorar la claridad y reducir la complejidad de la función, facilitando su mantenimiento y futuras validaciones.  
  - **Archivos de referencia:**  
    - La función original `recoger_parametros_usuario` en main.py.

- **Subtarea 2:** Documentar la validación y los valores por defecto de cada parámetro para asegurar la consistencia en futuras modificaciones.  
  - **Archivos involucrados:**  
    - main.py o nuevo módulo de documentación / validación.  
  - **Acción a realizar:** Modificar la documentación interna.  
  - **Justificación:** Al documentar, se facilita la extensión del código y la comprensión por parte de nuevos desarrolladores.  
  - **Archivos de referencia:**  
    - Comentarios y docstrings existentes en main.py.

---

### 5. Tarea Principal: Centralizar el manejo de excepciones y logging  
- **Dependencias:**  
  - main.py y todos los módulos que actualmente realizan manejo de excepciones de forma individual.  

#### 🔹 Subtareas:
- **Subtarea 1:** Crear un sistema centralizado o patrón de manejo de errores para capturar y registrar las excepciones, evitando duplicación de código en cada función.  
  - **Archivos involucrados:**  
    - main.py  
    - Módulo Logger y posiblemente un nuevo middleware para manejo de errores.  
  - **Acción a realizar:** Modificar la estructura de try/except y centralizar la lógica.  
  - **Justificación:** Garantiza una consistencia en la captación de errores y facilita la localización y solución de problemas.  
  - **Archivos de referencia:**  
    - El manejo actual de excepciones en main.py y la configuración del logger.
