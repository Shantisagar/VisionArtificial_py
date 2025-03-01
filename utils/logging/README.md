# Estrategia de Logging y Notificaciones

## Visión General

Este proyecto implementa una estrategia dual para el manejo de información:

1. **Sistema de Logging**: Enfocado en el registro técnico de eventos para depuración, monitoreo y auditoría.
2. **Sistema de Notificaciones**: Enfocado en presentar información relevante al usuario final.

## Separación de Responsabilidades

### Sistema de Logging (`LoggerConfigurator` y `LoggerFactory`)

- **Propósito**: Registrar información técnica detallada para desarrollo, depuración y monitoreo.
- **Destino**: Archivos de log y/o consola del sistema (no visibles directamente al usuario final).
- **Nivel de detalle**: Alto - incluye trazas, información de depuración, y detalles técnicos.
- **Persistencia**: Almacenamiento a largo plazo para análisis posterior.
- **Formato**: Estandarizado y optimizado para análisis técnico (timestamps, niveles, contexto, archivo y línea).

### Sistema de Notificaciones (`Notifier`)

- **Propósito**: Presentar información significativa y accionable al usuario final.
- **Destino**: Interfaz de usuario (GUI, consola, correo electrónico, etc.).
- **Nivel de detalle**: Bajo - solo información relevante para el usuario.
- **Persistencia**: Temporal - visible durante la interacción del usuario.
- **Formato**: Amigable para el usuario, posiblemente con elementos visuales.

## Uso Correcto

### Cuándo usar Logging:

- Registro de operaciones técnicas (conexiones a bases de datos, inicialización de componentes)
- Depuración de problemas (valores intermedios, flujo de ejecución)
- Registro de excepciones y errores internos
- Métricas y estadísticas de rendimiento

### Cuándo usar Notificaciones:

- Alertas y mensajes que requieren atención o acción del usuario
- Resultados de operaciones visibles para el usuario
- Estado de procesos relevantes para la experiencia del usuario
- Errores que el usuario necesita conocer para tomar acción

## Implementación

### Configuración del Logger

El sistema de logging se puede configurar de dos maneras:

#### 1. Configuración basada en JSON (Recomendada)
La aplicación intentará cargar la configuración desde un archivo JSON utilizando `logging.config.dictConfig`:

