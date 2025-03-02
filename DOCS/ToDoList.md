
## Áreas para Mejoras Identificadas

### Función "Ajustar Altura" en el GUI

- **Contexto:**  
  Se ha identificado que la funcionalidad de ajustar la altura del botón en la interfaz (`"ajustar altura"`) no se comporta como se espera.  
- **Posible Ubicación:**  
  Revisa la implementación en `gui_parameter_panel_view.py` y el manejo del parámetro `altura` dentro de las variables asociadas (`altura_var`).  
- **Acción:**  
  Verificar callbacks y lógica de actualización en la interacción con `gui_parameter_panel_controller.py`.

### Botones [ - ] y [ + ] al lado de la barra horizontal

- **Contexto:**  
  Se requiere agregar botones para incrementar o decrementar el parámetro seleccionado en 1 unidad.  
- **Posible Ubicación:**  
  La gestión de la disposición de controles se realiza en `parameter_panel_layout.py`, mientras que la creación de cada fila de parámetro se define en `parameter_row_factory.py`.  
- **Acción:**  
  Investigar la generación de controles en estos archivos para implementar o modificar los botones de decremento ([ - ]) y incremento ([ + ]).

### Visualización de FPS y Métricas de CPU

- **Visualización de FPS:**  
  - **Contexto:** Se desea mostrar los FPS actuales en la interfaz.  
  - **Posible Ubicación:** La vista principal del video en `main_display_view.py` o incluso dentro del `control_panel_view.py` donde se muestran estadísticas.  
  - **Acción:** Agregar una función para calcular y visualizar los FPS.

- **Rendimiento de CPU (con openhardwaremonitor-v0.9.6):**  
  - **Contexto:** Se planea integrar la monitorización de la CPU usando la herramienta `openhardwaremonitor-v0.9.6`.  
  - **Posible Ubicación:** Dado que actualmente no se muestra, puedes crear una nueva función o módulo que reciba la información de rendimiento y actualice la interfaz en `control_panel_view.py`.  
  - **Acción:** Determinar la lógica de conexión con OpenHardwareMonitor y ubicar el panel de estadísticas donde se mostrará esta información.

### Incorporar una barra horizontal de "zoom"

- **Contexto:**  
  Se requiere agregar una barra horizontal para ajustar el nivel de zoom en la visualización del video.
- **Posible Ubicación:**  
  La barra de zoom debe ubicarse en el panel de control, posiblemente debajo de los controles de parámetros.
- **Acción:**  
  Investigar la implementación de la barra de zoom en `control_panel_view.py` y `main_display_view.py`. Asegurarse de que el valor de zoom se aplique correctamente a la visualización del video.

### Selector de color de papel

- **Contexto:**  
  Se necesita un selector para elegir entre diferentes colores de papel (Blanco, Marrón). Dependiendo del color seleccionado, se aplicará un filtro de contraste específico.
- **Posible Ubicación:**  
  El selector de color de papel debe ubicarse en el panel de control, junto a otros controles de parámetros.
- **Acción:**  
  Implementar el selector en `control_panel_view.py` y `gui_parameter_panel_view.py`. Definir los filtros de contraste en `video_processor.py` para aplicar los cambios en la visualización del video según el color de papel seleccionado.

### Maximizar la ventana de la GUI después de 2 segundos

- **Contexto:**  
  Se requiere que la ventana de la GUI se maximice automáticamente 2 segundos después de inicializarla.
- **Posible Ubicación:**  
  La lógica para maximizar la ventana debe implementarse en `gui_view.py`.
- **Acción:**  
  Programar la maximización de la ventana utilizando `self.root.after(2000, self.maximizar_ventana)` en el método `inicializar_ui` de `gui_view.py`.

---
