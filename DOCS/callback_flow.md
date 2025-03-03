# Flujo de Callbacks en la Arquitectura MVC

Este documento explica el flujo de comunicación entre los componentes de la aplicación, específicamente cómo se utilizan los callbacks para la actualización de parámetros.

## Diagrama de Flujo

```
+----------------+       (1) define callback       +----------------+
|                |--------------------------->     |                |
| AppController  |                                 |    GUIView     |
|                |<---------------------------|    |                |
+----------------+       (4) notifica cambios      +----------------+
        ^                                                   |
        |                                                   |
        | (5) actualiza config                              | (2) propaga callback
        |                                                   v
+----------------+                                  +----------------+
|                |                                  |                |
| ConfigModel    |                                  | ControlPanel   |
|                |                                  |                |
+----------------+                                  +----------------+
                                                           |
                                                           | (3) usuario modifica
                                                           v
```

## Explicación del Flujo

1. **Definición del Callback**: 
   - En `AppController.setup_view()`, se establece el método `on_parameters_update` como callback.
   - Este callback se pasa a `GUIView` mediante `view.set_parameters_update_callback()`.

2. **Propagación del Callback**:
   - `GUIView` almacena el callback en `self.on_parameters_update`.
   - Si `control_panel` ya está inicializado, propaga el callback a `ControlPanelView.set_parameters_update_callback()`.
   - Si no, lo hará más tarde durante la inicialización en `_configure_component_callbacks()`.

3. **Interacción del Usuario**:
   - Cuando el usuario ajusta controles en la interfaz (deslizadores, campos numéricos), `ControlPanelView` captura estos eventos.
   - `ControlPanelView` invoca el callback registrado con los nuevos valores de parámetros.

4. **Notificación de Cambios**:
   - El callback `on_parameters_update` en `AppController` se ejecuta con los nuevos parámetros.
   - `AppController` procesa los parámetros (comprueba flags especiales como 'reset' o 'save_as_default').

5. **Actualización del Modelo**:
   - Si los parámetros incluyen 'save_as_default', `AppController` actualiza la configuración en `ConfigModel`.
   - En todos los casos, `AppController` llama a `view.update_parameters()` para actualizar la UI con los nuevos valores.

## Casos Especiales

### Banderas Especiales
- **reset**: Indica que se deben restaurar los valores predeterminados.
- **save_as_default**: Indica que los valores actuales deben guardarse como predeterminados.

### Manejo de Errores
- Se implementa verificación para evitar callbacks nulos.
- Se capturan excepciones durante la propagación de callbacks y actualización de parámetros.
- Se devuelven valores booleanos para indicar éxito/fallo en operaciones críticas.

## Mejores Prácticas

1. **Siempre verificar la existencia de callbacks antes de invocarlos**:
   ```python
   if self.on_parameters_update:
       self.on_parameters_update(parameters)
   ```

2. **Proteger las llamadas a callbacks con bloques try-except**:
   ```python
   try:
       self.on_parameters_update(parameters)
   except Exception as e:
       self.logger.error(f"Error en callback: {e}", exc_info=True)
   ```

3. **Devolver valores de estado** para indicar si la operación tuvo éxito:
   ```python
   def set_parameters_update_callback(self, callback):
       # ...código...
       return True  # o False si hay error
   ```
```