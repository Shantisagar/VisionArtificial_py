# Documentación de Parámetros de Entrada

## Propósito
Este documento describe en detalle los parámetros de entrada utilizados por la aplicación, incluyendo su propósito, rangos válidos, valores por defecto y cómo afectan el procesamiento de la imagen.

## Parámetros

### Grados de Rotación
- **Descripción**: Controla la rotación de la imagen capturada en grados.
- **Rango Válido**: -180.0° a 180.0°
- **Valor por Defecto**: 0.0°
- **Impacto**: Rota la imagen procesada para compensar cualquier desalineación de la cámara. Un valor positivo rota la imagen en sentido horario, mientras que un valor negativo la rota en sentido antihorario.
- **Cuándo Ajustar**: Se debe ajustar cuando la imagen capturada no está alineada correctamente con respecto al horizonte o cuando se necesita una orientación específica para el procesamiento.

### Píxeles por Milímetro
- **Descripción**: Especifica la relación de escala entre píxeles en la imagen y milímetros en el mundo real.
- **Rango Válido**: Mayor que 0.1
- **Valor por Defecto**: 1.0
- **Impacto**: Este valor es crítico para realizar mediciones precisas en la imagen. Afecta directamente la conversión de distancias en píxeles a unidades reales (mm).
- **Cuándo Ajustar**: Se debe calibrar este valor cuando se cambia la distancia de la cámara al objeto, se modifica el zoom de la lente, o se requieren mediciones precisas.
- **Procedimiento de Calibración**: Colocar un objeto de dimensiones conocidas en el campo visual, medir su tamaño en píxeles y dividir por el tamaño real en mm.

### Altura (Ajuste Vertical)
- **Descripción**: Ajusta la posición vertical de la imagen procesada.
- **Rango Válido**: -1000.0 a 1000.0
- **Valor por Defecto**: 0.0
- **Impacto**: Desplaza la imagen hacia arriba o hacia abajo en el campo visual. Útil para centrar el área de interés.
- **Cuándo Ajustar**: Se debe modificar cuando el objeto de interés no está centrado verticalmente en la imagen.

### Horizontal (Desplazamiento Horizontal)
- **Descripción**: Ajusta la posición horizontal de la imagen procesada.
- **Rango Válido**: -1000.0 a 1000.0
- **Valor por Defecto**: 0.0
- **Impacto**: Desplaza la imagen hacia la izquierda o derecha en el campo visual. Útil para centrar el área de interés.
- **Cuándo Ajustar**: Se debe modificar cuando el objeto de interés no está centrado horizontalmente en la imagen.

## Interacciones entre Parámetros

Los parámetros pueden tener efectos combinados en el procesamiento de la imagen:

- **Rotación y Desplazamiento**: Después de aplicar una rotación, es posible que sea necesario ajustar los desplazamientos horizontal y vertical para mantener el objeto de interés centrado.
- **Píxeles por Milímetro y Mediciones**: La precisión de las mediciones depende directamente de la calibración correcta de los píxeles por milímetro.

## Recomendaciones

1. **Calibración Regular**: Se recomienda recalibrar los píxeles por milímetro cada vez que se modifique la configuración física de la cámara.
2. **Ajuste Incremental**: Para la rotación y los desplazamientos, es mejor hacer ajustes pequeños e incrementales para obtener la configuración óptima.
3. **Validación Visual**: Siempre verificar visualmente el efecto de los cambios de parámetros en la imagen procesada.
