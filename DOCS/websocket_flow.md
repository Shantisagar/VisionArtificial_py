# Flujo WebSocket

## Conexión
1. El cliente se conecta al servidor WebSocket.
2. El evento `connect` es manejado por el servidor.

## Eventos Principales
- **connect**: Se ejecuta cuando un cliente se conecta.
- **disconnect**: Se ejecuta cuando un cliente se desconecta.
- **message**: Maneja mensajes enviados por el cliente.

## Ejemplo de Mensajes
### Mensaje del Cliente
```json
{
  "type": "message",
  "content": "Hola, servidor"
}
```

### Respuesta del Servidor
```json
{
  "type": "response",
  "content": "Mensaje recibido en el servidor"
}
```
