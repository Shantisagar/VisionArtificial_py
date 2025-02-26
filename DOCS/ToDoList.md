## 1. Desacoplar la Interfaz de Usuario (Tkinter) y la Lógica de Procesamiento

**Título:** Separación de la UI de la lógica de procesamiento  
**Dependencias:**  
- Dependencia directa entre el módulo de video (UI) y la lógica de procesamiento en image_processing, rotacion, deteccion_bordes.

#### 🔹 Subtareas

- **Título de la subtarea:** Crear un controlador/interfaz para orquestar la lógica de procesamiento  
  - **Archivos involucrados:**  
    - video_stream.py
    - image_processing.py
  - **Acción a realizar:** Modificar  
  - **Justificación detallada:**  
    - Actualmente, el flujo de la aplicación mezcla la obtención y procesamiento de la imagen en el mismo contexto (Tkinter y procesamiento de imagen). Separar estas responsabilidades facilitará futuras migraciones (por ejemplo, a una API web) y reducirá el acoplamiento.
  - **Archivos de referencia:**  
    - Código existente en video_stream.py y image_processing.py.

- **Título de la subtarea:** Refactorizar la inicialización de la interfaz para utilizar inyección de dependencias  
  - **Archivos involucrados:**  
    - main.py
    - config_manager.py
  - **Acción a realizar:** Modificar  
  - **Justificación detallada:**  
    - Permitir que la lógica de negocio y la UI sean gestionadas de manera independiente ayudará en la transición hacia arquitecturas basadas en API.  
  - **Archivos de referencia:**  
    - Configuración actual en config_manager.py y main.py.

---

## 2. Refactorización SOLID en la Lógica Central

**Título:** Aplicación de principios SOLID en la lógica de procesamiento y registro  
**Dependencias:**  
- Involucra módulos como image_processing.py, registro_desvios.py y config_manager.py; depende de una correcta separación de responsabilidades.

#### 🔹 Subtareas

- **Título de la subtarea:** Definir interfaces y contratos para el procesamiento de imágenes  
  - **Archivos involucrados:**  
    - image_processing.py
    - deteccion_bordes.py
    - rotacion.py
  - **Acción a realizar:** Modificar  
  - **Justificación detallada:**  
    - Establecer contratos permite inyectar dependencias y mejorar el testeo unitario, facilitando futuras integraciones (por ejemplo, con Deep Learning), reduciendo el acoplamiento entre funciones.
  - **Archivos de referencia:**  
    - Código en image_processing.py, deteccion_bordes.py y rotacion.py.

- **Título de la subtarea:** Separar la gestión de logs y configuración de la lógica de negocio  
  - **Archivos involucrados:**  
    - config_manager.py
    - config_logger.py
  - **Acción a realizar:** Modificar  
  - **Justificación detallada:**  
    - Una configuración centralizada y desacoplada ayudará a que cada módulo sea independiente, facilitando cambios futuros sin afectar la lógica de negocio.
  - **Archivos de referencia:**  
    - Config_manager.py y config_logger.py.

- **Título de la subtarea:** Reestructurar la lógica de registro de desvíos para desacoplar la persistencia  
  - **Archivos involucrados:**  
    - registro_desvios.py
  - **Acción a realizar:** Modificar  
  - **Justificación detallada:**  
    - Crear una capa de abstracción en el acceso a datos (por ejemplo, a MySQL) permitirá cambiar o ampliar la base de datos sin modificar la lógica de negocio.
  - **Archivos de referencia:**  
    - Código actual en registro_desvios.py.

---

## 3. Optimización y Profiling del Procesamiento de Imágenes

**Título:** Mejorar el rendimiento del procesamiento de imágenes en CPU  
**Dependencias:**  
- Módulos de procesamiento: image_processing.py, deteccion_bordes.py, rotacion.py; depende de la funcionalidad central del sistema.

#### 🔹 Subtareas

- **Título de la subtarea:** Realizar profiling para identificar cuellos de botella  
  - **Archivos involucrados:**  
    - image_processing.py
    - deteccion_bordes.py
  - **Acción a realizar:** Modificar (incluyendo la instrumentación temporal de código para medir desempeño)  
  - **Justificación detallada:**  
    - Evaluar qué funciones o regiones de código consumen más recursos permitirá focalizar esfuerzos de optimización sin impactar el funcionamiento actual.
  - **Archivos de referencia:**  
    - image_processing.py y deteccion_bordes.py.

- **Título de la subtarea:** Optimizar pasos críticos (por ejemplo, cálculo de derivadas y procesamiento en NumPy)  
  - **Archivos involucrados:**  
    - deteccion_bordes.py
  - **Acción a realizar:** Modificar  
  - **Justificación detallada:**  
    - Mejorar el rendimiento en CPU es crítico para video en tiempo real. El uso de operaciones vectorizadas y algoritmos más eficientes reducirá el tiempo de procesamiento por frame.
  - **Archivos de referencia:**  
    - Código actual en deteccion_bordes.py.

- **Título de la subtarea:** Documentar y preparar la modularidad para integrar aceleración con GPU  
  - **Archivos involucrados:**  
    - Módulos de procesamiento (generalmente image_processing.py y dependencias)
  - **Acción a realizar:** Modificar (añadiendo comentarios/documentación estratégica)  
  - **Justificación detallada:**  
    - Crear puntos bien definidos en la canalización de procesamiento facilitará la futura integración con tecnologías de aceleración (como CUDA o bibliotecas específicas de GPU).
  - **Archivos de referencia:**  
    - image_processing.py, deteccion_bordes.py y rotacion.py.

---

## 4. Preparación para la Transición a una API basada en Flask/FastAPI

**Título:** Diseñar la arquitectura para exponer servicios de procesamiento a través de una API  
**Dependencias:**  
- Depende de la separación de lógica de negocio y UI (tareas anteriores) y una refactorización SOLID que permita invocar los módulos de procesamiento de forma independiente.

#### 🔹 Subtareas

- **Título de la subtarea:** Conceptualizar endpoints y contratos de comunicación para el procesamiento de imágenes  
  - **Archivos involucrados:**  
    - main.py
    - video_stream.py
  - **Acción a realizar:** Modificar (añadir documentación/prototipo)  
  - **Justificación detallada:**  
    - Definir cómo se expone la lógica actual mediante una API ayudará a planificar la transición sin interrumpir la funcionalidad. Se deben documentar los contratos de entrada/salida de cada servicio.
  - **Archivos de referencia:**  
    - main.py y video_stream.py.

- **Título de la subtarea:** Crear documentación interna para la futura migración a API  
  - **Archivos involucrados:**  
    - Archivo de documentación (por definir, podría ser en docs o como README actualizado)
  - **Acción a realizar:** Crear  
  - **Justificación detallada:**  
    - Una documentación clara de los servicios y la arquitectura actual facilitará la adopción de Flask/FastAPI en una siguiente fase, minimizando el riesgo de reestructuraciones imprevistas.
  - **Archivos de referencia:**  
    - Documentos internos de arquitectura y el código actual de procesamiento.
