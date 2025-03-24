/*
Path: frontend/src/websocket-client.js
*/

import { io } from "socket.io-client";

const socket = io("http://localhost:5000");

socket.on("connect", () => {
  console.log("Conectado al servidor WebSocket");
});

socket.on("message", (data) => {
  console.log("Mensaje recibido del servidor:", data);
});

socket.on("disconnect", () => {
  console.log("Desconectado del servidor WebSocket");
});

export default socket;
