1. ### Tarea Principal 1: Optimización del Procesamiento en Tiempo Real  
   **Dependencias:**  
   - Módulos: video_stream.py, image_processing.py, ProcessingController en image_processing.py

   #### 🔹 Subtareas  
   - **Separar el procesamiento de imágenes del hilo de la interfaz**  
     - **Archivos involucrados:**  
       - video_stream.py  
     - **Acción a realizar:** Modificar  
     - **Justificación detallada:**  
       La ejecución del procesamiento intensivo en el mismo hilo que la UI provoca bloqueos y reduce la fluidez, especialmente en transmisión en tiempo real o al manejar imágenes de alta resolución. Desacoplar este procesamiento (por ejemplo, implementando hilos o procesos separados) permitirá aprovechar mejor los recursos del sistema sin afectar la visualización.  
     - **Archivos de referencia:**  
       - image_processing.py (especialmente la clase ProcessingController)  
       - rotacion.py y deteccion_bordes.py para entender la lógica de procesamiento.

   - **Implementar gestión de sincronización y control de calidad de frames**  
     - **Archivos involucrados:**  
       - video_stream.py  
     - **Acción a realizar:** Modificar  
     - **Justificación detallada:**  
       Es necesario garantizar que el reenvío de frames desde el procesamiento a la UI se haga de forma sincronizada para evitar pérdida de frames o errores de concurrencia.  
     - **Archivos de referencia:**  
       - Bibliotecas de Python para concurrencia (como threading o concurrent.futures) pueden ser consultadas.

---

2. ### Tarea Principal 2: Refactorización para Adherencia a SOLID  
   **Dependencias:**  
   - Módulos: main.py, image_processing.py, video_stream.py, config_manager.py, config_logger.py

   #### 🔹 Subtareas  
   - **Revisión de responsabilidades y separación de preocupaciones**  
     - **Archivos involucrados:**  
       - main.py  
       - image_processing.py  
       - video_stream.py  
     - **Acción a realizar:** Modificar  
     - **Justificación detallada:**  
       Identificar y aislar funciones con múltiples responsabilidades (por ejemplo, entrada del usuario, procesamiento, y actualización de UI) facilita su mantenibilidad y posterior extensión. Se recomienda separar claramente la lógica de entrada, la de procesamiento y la de presentación.  
     - **Archivos de referencia:**  
       - La documentación actual de cada módulo para comprender responsabilidades.

   - **Implementar inyección de dependencias**  
     - **Archivos involucrados:**  
       - main.py  
       - config_manager.py  
       - video_stream.py  
     - **Acción a realizar:** Modificar  
     - **Justificación detallada:**  
       Inyectar dependencias (como el logger, configuraciones o controladores de procesamiento) ayudará a reducir el acoplamiento y abrirá la posibilidad de testear cada componente de forma aislada.  
     - **Archivos de referencia:**  
       - config_manager.py y src/logs/config_logger.py, para entender cómo se gestionan actualmente estas dependencias.

---

3. ### Tarea Principal 3: Desacoplar la Lógica de la Interfaz Gráfica  
   **Dependencias:**  
   - Módulos: video_stream.py, image_processing.py

   #### 🔹 Subtareas  
   - **Separar la lógica de presentación de la lógica de procesamiento**  
     - **Archivos involucrados:**  
       - video_stream.py  
     - **Acción a realizar:** Modificar  
     - **Justificación detallada:**  
       Se recomienda aplicar un patrón arquitectónico (como MVC o MVP) para que la UI (Tkinter) solo sea responsable de presentar resultados y obtenga los datos de un controlador o servicio. Esto facilita la migración futura a interfaces basadas en web (Flask/FastAPI) sin rehacer la lógica de procesamiento.  
     - **Archivos de referencia:**  
       - image_processing.py (para identificar la lógica de procesamiento)  
       - Ejemplos de implementación de MVC en Python.

   - **Documentar la interdependencia actual entre UI y procesamiento**  
     - **Archivos involucrados:**  
       - main.py  
       - video_stream.py  
     - **Acción a realizar:** Modificar (comentarios y documentación)  
     - **Justificación detallada:**  
       Documentar cómo la UI obtiene y muestra los datos procesados ayudará en la futura migración hacia una arquitectura desacoplada o basada en API web.  
     - **Archivos de referencia:**  
       - La documentación interna del proyecto, si existe, o comentarios en el código actual.

---

4. ### Tarea Principal 4: Abstracción de la Gestión de la Base de Datos  
   **Dependencias:**  
   - Módulos: registro_desvios.py

   #### 🔹 Subtareas  
   - **Extraer y definir una capa de Acceso a Datos (DAO)**  
     - **Archivos involucrados:**  
       - registro_desvios.py  
     - **Acción a realizar:** Modificar  
     - **Justificación detallada:**  
       Crear una capa de abstracción para el acceso a la base de datos permitirá cambiar fácilmente de MySQL a otra solución (u otras configuraciones) sin modificar la lógica principal de registro de desviaciones. Esto mejora la mantenibilidad y la escalabilidad.  
     - **Archivos de referencia:**  
       - Documentación de patrones DAO y ejemplos en Python.

   - **Configurar la abstracción para soportar múltiples motores de bases de datos**  
     - **Archivos involucrados:**  
       - registro_desvios.py  
     - **Acción a realizar:** Modificar  
     - **Justificación detallada:**  
       Permitir que la configuración de la base de datos se defina de manera flexible en un archivo de configuración o mediante variables de entorno facilitará futuros cambios o migraciones.  
     - **Archivos de referencia:**  
       - config_manager.py para ver ejemplos de manejo de configuraciones.
