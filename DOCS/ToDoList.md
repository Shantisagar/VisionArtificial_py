### 🔍 **Análisis y Priorización de Mejoras en el Proyecto**

## 📌 **Identificación y Evaluación de Mejoras**

### **1️⃣ Identificación y Evaluación de Mejoras**

#### Mejora 1: Eliminar la Recolección de Parámetros desde la Consola
- **Costo de Implementación**: Medio
- **Impacto en el Proyecto**: Alto
- **Descripción**: Eliminar la dependencia de la consola para la actualización de parámetros y permitir que estos se actualicen desde la GUI.
- **Beneficio**: Mejora la experiencia del usuario y mantiene la coherencia en la interfaz de usuario.

#### Mejora 2: Actualizar la Interfaz Gráfica para Recolección de Parámetros
- **Costo de Implementación**: Medio
- **Impacto en el Proyecto**: Alto
- **Descripción**: Añadir campos de entrada en la GUI para que el usuario pueda actualizar los parámetros directamente desde la interfaz gráfica.
- **Beneficio**: Facilita la interacción del usuario y elimina la necesidad de utilizar la consola.

#### Mejora 3: Refactorizar el Controlador de Entrada
- **Costo de Implementación**: Medio
- **Impacto en el Proyecto**: Alto
- **Descripción**: Refactorizar el `InputController` para que recoja los parámetros desde la GUI en lugar de la consola.
- **Beneficio**: Mantiene la separación de responsabilidades y mejora la mantenibilidad del código.

#### Mejora 4: Actualizar la Vista de la GUI
- **Costo de Implementación**: Medio
- **Impacto en el Proyecto**: Alto
- **Descripción**: Actualizar la clase `GUIView` para incluir métodos que permitan la recolección y validación de parámetros desde la interfaz gráfica.
- **Beneficio**: Mejora la cohesión y la experiencia del usuario.

### **2️⃣ Priorización de Mejoras**

#### Alta Prioridad
1. **Mejora 1: Eliminar la Recolección de Parámetros desde la Consola**
2. **Mejora 2: Actualizar la Interfaz Gráfica para Recolección de Parámetros**
3. **Mejora 3: Refactorizar el Controlador de Entrada**
4. **Mejora 4: Actualizar la Vista de la GUI**

### **3️⃣ Plan de Implementación Segura**

#### 📌 **Tarea Principal**
- **Título**: Eliminar la Recolección de Parámetros desde la Consola y Actualizar la GUI
- **Descripción**: Refactorizar el sistema de recolección de parámetros para que se realice desde la GUI en lugar de la consola.
- **Dependencias**: Ninguna
- **Beneficio esperado**: Mejora la experiencia del usuario y mantiene la coherencia en la interfaz de usuario.

#### 🔹 **Subtareas**

1. **Título de la subtarea**: Eliminar Métodos de Recolección de Parámetros desde la Consola
   - **Orden de ejecución**: 1
   - **Archivos involucrados**: console_view.py
   - **Acción a realizar**: Modificar
   - **Justificación detallada**: Eliminar los métodos de recolección de parámetros en `ConsoleView` para evitar la dependencia de la consola.
   - **Archivos de referencia**: console_view.py

2. **Título de la subtarea**: Añadir Campos de Entrada en la GUI
   - **Orden de ejecución**: 2
   - **Archivos involucrados**: gui_view.py
   - **Acción a realizar**: Modificar
   - **Justificación detallada**: Añadir campos de entrada en la interfaz gráfica para que el usuario pueda actualizar los parámetros.
   - **Archivos de referencia**: gui_view.py

3. **Título de la subtarea**: Refactorizar el `InputController`
   - **Orden de ejecución**: 3
   - **Archivos involucrados**: input_controller.py
   - **Acción a realizar**: Modificar
   - **Justificación detallada**: Refactorizar `InputController` para que recoja los parámetros desde la GUI.
   - **Archivos de referencia**: input_controller.py

4. **Título de la subtarea**: Actualizar `GUIView` para Manejar Parámetros
   - **Orden de ejecución**: 4
   - **Archivos involucrados**: gui_view.py
   - **Acción a realizar**: Modificar
   - **Justificación detallada**: Añadir métodos en `GUIView` para manejar la recolección y validación de parámetros desde la interfaz gráfica.
   - **Archivos de referencia**: gui_view.py

### **4️⃣ Opciones y Alternativas**

#### Alternativa 1: Mantener la Recolección de Parámetros desde la Consola
- **Ventajas**: Menor costo de implementación.
- **Desventajas**: Peor experiencia de usuario, inconsistencia en la interfaz.
- **Recomendación**: No recomendado debido a la mala experiencia del usuario.

#### Alternativa 2: Implementar un Sistema Híbrido
- **Ventajas**: Flexibilidad para el usuario.
- **Desventajas**: Mayor complejidad en el código, posible inconsistencia.
- **Recomendación**: No recomendado debido a la complejidad y posible inconsistencia.

#### Recomendación Final
- **Implementar la recolección de parámetros exclusivamente desde la GUI** para mejorar la experiencia del usuario y mantener la coherencia en la interfaz de usuario.