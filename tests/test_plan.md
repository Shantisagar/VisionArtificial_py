# Plan de Pruebas - Interfaz Gráfica de VisionArtificial

## Pruebas Funcionales

### 1. Inicialización de la Aplicación
- [x] Verificar que la aplicación inicia correctamente con los valores predeterminados
- [x] Verificar que se establece conexión con la cámara web
- [x] Verificar que la interfaz gráfica se muestra correctamente

### 2. Controles de Parámetros
- [x] Verificar que todos los sliders funcionan correctamente
- [x] Verificar que los campos de entrada aceptan valores numéricos
- [ ] Verificar que se rechazan valores no numéricos o fuera de rango
- [x] Verificar que los tooltips aparecen al pasar el cursor sobre los controles
- [x] Verificar que los botones de ayuda muestran la información correcta

### 3. Actualización de Parámetros
- [ ] Verificar que los cambios en los sliders se aplican en tiempo real
- [ ] Verificar que los cambios en los campos de entrada se aplican al perder el foco o presionar Enter
- [ ] Verificar que el botón "Aplicar cambios" aplica todos los cambios a la vez
- [ ] Verificar que los cambios de parámetros afectan correctamente el procesamiento de video

### 4. Gestión de Valores Predeterminados
- [x] Verificar que el botón "Restaurar valores predeterminados" carga correctamente los valores desde la configuración
- [x] Verificar que el botón "Guardar como valores predeterminados" guarda correctamente los valores actuales
- [x] Verificar que después de reiniciar la aplicación, se cargan los valores guardados anteriormente

### 5. Interfaz de Usuario
- [x] Verificar que el video se muestra correctamente en el área designada
- [x] Verificar que las estadísticas de procesamiento se actualizan regularmente
- [x] Verificar que las notificaciones de estado se muestran correctamente
- [x] Verificar que la aplicación responde adecuadamente a cambios de tamaño de ventana

### 6. Cierre de la Aplicación
- [x] Verificar que la aplicación se cierra correctamente al hacer clic en el botón de cierre
- [x] Verificar que se liberan todos los recursos (cámara, hilos, etc.) al cerrar

## Pruebas de Usabilidad

### 1. Facilidad de Uso
- [ ] Evaluar si los controles son intuitivos y fáciles de entender
- [ ] Evaluar si la disposición de elementos en la interfaz es lógica
- [ ] Evaluar si la información de ayuda es clara y útil

### 2. Retroalimentación Visual
- [x] Evaluar si la aplicación proporciona retroalimentación adecuada sobre las acciones del usuario
- [x] Evaluar si los mensajes de error son claros y útiles

## Pruebas de Rendimiento

- [x] Evaluar el uso de CPU durante la operación normal
- [x] Evaluar el uso de memoria durante la operación prolongada
- [x] Evaluar la capacidad de respuesta de la interfaz durante el procesamiento de video

## Notas Adicionales

- Ambiente de pruebas: Especificar sistema operativo, versiones de Python y bibliotecas
- Dispositivos de captura: Especificar modelos de cámaras web utilizadas para las pruebas
- Condiciones de iluminación: Documentar las condiciones de iluminación durante las pruebas
