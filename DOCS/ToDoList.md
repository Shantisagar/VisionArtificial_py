### 1. Refactorización de Métodos con Múltiples Responsabilidades

**Objetivo:**  
Simplificar y modularizar los métodos que combinan la creación, configuración y manejo de eventos en la interfaz, para mejorar su legibilidad y facilitar el mantenimiento y las pruebas.

**Tareas y Subtareas:**

- **1.1. Auditar Métodos Actuales**
  - **Descripción:** Revisar detenidamente los métodos en archivos como control_panel_view.py y gui_view.py para identificar bloques de código que combinen múltiples responsabilidades (por ejemplo, creación de widgets, configuración de callbacks y actualización de la UI).
  - **Archivos a modificar o revisar:**  
    - control_panel_view.py  
    - gui_view.py  
  - **Archivos de referencia:**  
    - interface_view_helpers.py  
  - **Dependencias:** Ninguna externa, se apoya en la documentación interna.
  - **Beneficio esperado:** Identificación clara de secciones que requieren descomposición, lo que facilitará el desarrollo incremental.

- **1.2. Extracción de Funciones Auxiliares**
  - **Descripción:** Dividir los métodos complejos en funciones o métodos privados que encapsulen tareas específicas, como la creación de widgets o la configuración de callbacks.
  - **Archivos a modificar:**  
    - control_panel_view.py  
    - gui_view.py  
  - **Archivos de referencia:** Patrón utilizado en interface_view_helpers.py.
  - **Dependencias:** Asegurar que las funciones extraídas sean reutilizables en toda la aplicación.
  - **Beneficio esperado:** Mejora en la separación de responsabilidades y mayor facilidad para realizar pruebas unitarias sobre cada función individual.

- **1.3. Actualización y Validación de Pruebas**
  - **Descripción:** Una vez refactorizados los métodos, actualizar (o crear nuevas) pruebas unitarias que garanticen el correcto funcionamiento de cada parte refactorizada.
  - **Archivos a modificar:**  
    - Archivo(s) de tests relacionados a la UI y a la lógica de control, si existen.
  - **Archivos de referencia:** Tests existentes en la suite del proyecto.
  - **Dependencias:** Dependencia directa de los cambios realizados en 1.2.
  - **Beneficio esperado:** Reducción de riesgos de errores en producción al garantizar que cada unidad de lógica refactorizada se prueba de manera independiente.

---

### 2. Consolidación de “Magic Numbers” y Constantes

**Objetivo:**  
Centralizar todos los valores fijos y “magic numbers” en un módulo de configuración o constantes para simplificar su modificación y reducir errores por duplicación.

**Tareas y Subtareas:**

- **2.1. Identificar Valores Fijos en el Código**
  - **Descripción:** Revisar archivos de la capa de presentación (por ejemplo, en interface_view_helpers.py, control_panel_view.py y gui_view.py) para localizar todos los valores fijos y parámetros (dimensiones, intervalos, umbrales).
  - **Archivos a modificar o revisar:**  
    - interface_view_helpers.py  
    - control_panel_view.py  
    - gui_view.py
  - **Archivos de referencia:** Código actual comentado y documentación interna.
  - **Dependencias:** Ninguna.
  - **Beneficio esperado:** Mapeo completo para proceder a centralizar los valores y evitar inconsistencias.

- **2.2. Crear un Módulo de Constantes**
  - **Descripción:** Diseñar y crear un archivo (por ejemplo, `constants.py`) en el que se definan todas las variables fijas usadas en la interfaz y posiblemente en otras áreas.
  - **Archivos a modificar o crear:**  
    - Se debe crear un nuevo archivo, posiblemente en src o `src/config/`.
  - **Archivos de referencia:** Métodos de ayuda en interface_view_helpers.py para obtener parámetros.
  - **Dependencias:** Esta tarea afectará cualquier archivo que use "magic numbers".
  - **Beneficio esperado:** Mayor claridad y facilidad para ajustar parámetros en el futuro sin necesidad de buscar en varias partes del código.

- **2.3. Reemplazar Valores Fijos por Constantes**
  - **Descripción:** Actualizar en todos los módulos afectados para que utilicen las constantes centralizadas en lugar de valores literales.
  - **Archivos a modificar:**  
    - interface_view_helpers.py  
    - control_panel_view.py  
    - gui_view.py
  - **Archivos de referencia:** El nuevo archivo `constants.py`.
  - **Dependencias:** Concluye 2.1 y 2.2.
  - **Beneficio esperado:** Consistencia en el uso de parámetros, facilitando la configuración y mantenimiento del código.

---

### 3. Reorganización de la Estructura de Archivos (src/views)

**Objetivo:**  
Mejorar la modularidad del proyecto agrupando los archivos de la interfaz en subcarpetas según su función (por ejemplo, separar vistas de control y vistas de visualización).

**Tareas y Subtareas:**

- **3.1. Propuesta y Definición de la Nueva Estructura**
  - **Descripción:** Documentar una nueva estructura donde se clasifiquen las vistas en categorías, como “controls”, “display” y “helpers”.
  - **Archivos a modificar:**  
    - No se modifica código, se crea documentación interna.
  - **Archivos de referencia:** La lista actual de archivos en views.
  - **Dependencias:** Se debe coordinar con el equipo para que todos los cambios de rutas se apliquen de manera conjunta.
  - **Beneficio esperado:** Mayor claridad y facilidad para mantener el código al separar las responsabilidades en distintas carpetas.

- **3.2. Mover Archivos a las Nuevas Subcarpetas**
  - **Descripción:** Realizar la reorganización física de los archivos en subcarpetas, realineando los imports correspondientes.
  - **Archivos a modificar o mover:**  
    - gui_view.py  
    - control_panel_view.py  
    - main_display_view.py  
    - interface_view_helpers.py  
    - gui_notifier.py
  - **Archivos de referencia:** La propuesta de 3.1.
  - **Dependencias:** Coordinación con otros cambios si hay integración continua.
  - **Beneficio esperado:** Estructura de proyecto más lógica y modular, facilitando la incorporación de nuevos componentes.

- **3.3. Validación y Actualización de Importaciones**
  - **Descripción:** Ajustar todas las referencias/imports afectados por el cambio en la estructura y validar la correcta ejecución de la aplicación.
  - **Archivos a modificar:**  
    - Todos los archivos que hagan referencia a los módulos movidos.
  - **Archivos de referencia:** Documentación interna sobre la nueva estructura.
  - **Dependencias:** Completar 3.2.
  - **Beneficio esperado:** Asegurarse de que la reorganización no rompa la compilación ni la ejecución de la aplicación, garantizando integridad en la comunicación entre módulos.

---

### 4. Ampliación y Consolidación de Pruebas Unitarias e Integración

**Objetivo:**  
Aumentar la cobertura de pruebas en áreas críticas para reducir riesgos de regresiones y mejorar la confiabilidad del código.

**Tareas y Subtareas:**

- **4.1. Auditoría de Cobertura Actual**
  - **Descripción:** Revisar la suite de pruebas existente para identificar áreas críticas (por ejemplo, `ConfigModel`, callbacks en la UI y notificaciones) con poca cobertura.
  - **Archivos a modificar o revisar:**  
    - Archivos de tests actuales.
  - **Archivos de referencia:** Documentación interna de pruebas.
  - **Dependencias:** Ninguna.
  - **Beneficio esperado:** Identificar lagunas de cobertura antes de implementar cambios.

- **4.2. Creación de Pruebas para Módulos Críticos**
  - **Descripción:** Escribir pruebas unitarias nuevas para el modelo de configuración (`ConfigModel`), la gestión de notificaciones (`GUINotifier`) y la comunicación entre el controlador y la vista.
  - **Archivos a modificar o crear:**  
    - Crear o ampliar archivos de test para módulos actuales.
  - **Archivos de referencia:** Código de cada módulo a testear.
  - **Dependencias:** Basado en los cambios estructurales realizados en tareas anteriores.
  - **Beneficio esperado:** Mayor robustez y detección temprana de errores en futuras iteraciones.

- **4.3. Integración de Pruebas de Regresión**
  - **Descripción:** Configurar un sistema de ejecución automática de pruebas (por ejemplo, en un pipeline de CI) para asegurar que los cambios refactorizados no introduzcan regresiones.
  - **Archivos a modificar o crear:**  
    - Configuración del CI/CD (por ejemplo, archivos de configuración de pruebas en el repositorio).
  - **Archivos de referencia:** Documentación de integración y pruebas anteriores.
  - **Dependencias:** Completar 4.2.
  - **Beneficio esperado:** Mejora continua en la calidad del código al detectar errores antes de la integración en producción.

- **4.4. Verificación y Validación Final**
  - **Descripción:** Ejecutar la suite de pruebas completa después de cada cambio significativo y documentar los resultados.
  - **Archivos a modificar o revisar:**  
    - Resultados y reportes de pruebas generados en la fase de integración.
  - **Archivos de referencia:** Herramientas de reportes del sistema CI.
  - **Dependencias:** Conclusión de 4.3.
  - **Beneficio esperado:** Asegurar la estabilidad del sistema previo a despliegues en producción.

---

### 5. Evaluación e Implementación del Sistema de Eventos (Opcional, Baja Prioridad)

**Objetivo:**  
Explorar e implementar, de forma gradual, un mecanismo de bus de eventos para mejorar la comunicación entre componentes y desacoplar aún más las vistas del controlador.

**Tareas y Subtareas:**

- **5.1. Investigación y Discusión Técnica**
  - **Descripción:** Realizar reuniones o sesiones de análisis con el equipo para evaluar distintos patrones para implementación de un bus de eventos o patrón observador.
  - **Archivos a modificar o revisar:**  
    - Documentación interna y propuestas técnicas.
  - **Archivos de referencia:** Ejemplos de patrones observador en proyectos similares.
  - **Dependencias:** No afecta el funcionamiento actual, se trata de un estudio previo.
  - **Beneficio esperado:** Decisión informada sobre la mejor estrategia sin impacto inmediato en la producción.

- **5.2. Prototipado y Prueba de Concepto**
  - **Descripción:** Implementar un prototipo en una rama separada que demuestre la viabilidad de integrar un bus de eventos sin afectar la lógica actual.
  - **Archivos a modificar o crear:**  
    - Nuevos módulos de eventos (por ejemplo, `event_bus.py`).
  - **Archivos de referencia:** Ejemplo de implementación en otros proyectos o bibliotecas.
  - **Dependencias:** Revisión de la alternativa seleccionada en 5.1.
  - **Beneficio esperado:** Validar el concepto y evaluar el esfuerzo antes de una integración completa.

- **5.3. Integración Gradual en la Comunicación Interna**
  - **Descripción:** Una vez validado el prototipo, empezar a refactorizar la comunicación entre vistas y el controlador para utilizar el bus de eventos en módulos críticos.
  - **Archivos a modificar:**  
    - app_controller.py  
    - gui_view.py  
    - Otros módulos de comunicación inter-vistas.
  - **Archivos de referencia:** Prototipo desarrollado en 5.2.
  - **Dependencias:** Depende de la conclusión exitosa de 5.2.
  - **Beneficio esperado:** Mayor desacoplamiento y escalabilidad a largo plazo, facilitando la adición de nuevas funcionalidades.

- **5.4. Validación con Pruebas de Integración**
  - **Descripción:** Desarrollar pruebas específicas que confirmen que la integración del bus de eventos no rompe la funcionalidad existente.
  - **Archivos a modificar o crear:**  
    - Nuevos tests enfocados en el bus de eventos.
  - **Archivos de referencia:** Tests existentes en el proyecto y documentación del prototipo.
  - **Dependencias:** Finalización de 5.3.
  - **Beneficio esperado:** Garantizar la estabilidad del sistema tras la integración del nuevo sistema de eventos.
