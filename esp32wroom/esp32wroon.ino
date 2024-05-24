#include <WiFi.h>
#include <WebServer.h>

// Configura el SSID y la contraseña de tu red WiFi
const char* ssid = "Aula tecnica";
const char* password = "Madygraf32";

// Configura los pines de salida
const int pinOutput_ENA = 18; // enciende el motor con LOW
const int pinOutput_DIR = 19; // sentido de giro
const int pinOutput_PUL = 21; // pulso, debe tener 1000 microsegundos entre semiciclo positivo y negativo

WebServer server(80);

void handleRoot() {
  server.send(200, "text/plain", "ESP32 Web Server");
}

void handleOutputENAOn() {
  digitalWrite(pinOutput_ENA, LOW); // ENA se enciende con LOW
  server.send(200, "text/plain", "ENA ON");
}

void handleOutputENAOff() {
  digitalWrite(pinOutput_ENA, HIGH); // ENA se apaga con HIGH
  server.send(200, "text/plain", "ENA OFF");
}

void handleOutputDIROn() {
  digitalWrite(pinOutput_DIR, HIGH);
  server.send(200, "text/plain", "DIR ON");
}

void handleOutputDIROff() {
  digitalWrite(pinOutput_DIR, LOW);
  server.send(200, "text/plain", "DIR OFF");
}

void handlePulse() {
  // Generar pulsos de 1000 microsegundos durante 1 segundo
  unsigned long startTime = millis();
  while (millis() - startTime < 1000) {
    digitalWrite(pinOutput_PUL, HIGH);
    delayMicroseconds(500);
    digitalWrite(pinOutput_PUL, LOW);
    delayMicroseconds(500);
  }
  server.send(200, "text/plain", "Pulses Sent for 1 second");
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("WiFi connected");

  // Imprime la dirección IP obtenida
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  // Configura los pines de salida
  pinMode(pinOutput_ENA, OUTPUT);
  pinMode(pinOutput_DIR, OUTPUT);
  pinMode(pinOutput_PUL, OUTPUT);

  // Configura los pines en estado inicial
  digitalWrite(pinOutput_ENA, HIGH); // El motor está apagado inicialmente
  digitalWrite(pinOutput_DIR, LOW); // El sentido de giro es hacia adelante inicialmente
  digitalWrite(pinOutput_PUL, LOW); // El pulso está en estado bajo inicialmente

  server.on("/", handleRoot);
  server.on("/ena/on", handleOutputENAOn);
  server.on("/ena/off", handleOutputENAOff);
  server.on("/dir/on", handleOutputDIROn);
  server.on("/dir/off", handleOutputDIROff);
  server.on("/pulse", handlePulse);

  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient();
}
#include <WiFi.h>
#include <WebServer.h>

// Configura el SSID y la contraseña de tu red WiFi
const char* ssid = "Aula tecnica";
const char* password = "Madygraf32";

// Configura los pines de salida
const int pinOutput_ENA = 18; // enciende el motor con LOW
const int pinOutput_DIR = 19; // sentido de giro
const int pinOutput_PUL = 21; // pulso, debe tener 1000 microsegundos entre semiciclo positivo y negativo

WebServer server(80);

void handleRoot() {
  server.send(200, "text/plain", "ESP32 Web Server");
}

void handleOutputENAOn() {
  digitalWrite(pinOutput_ENA, LOW); // ENA se enciende con LOW
  server.send(200, "text/plain", "ENA ON");
}

void handleOutputENAOff() {
  digitalWrite(pinOutput_ENA, HIGH); // ENA se apaga con HIGH
  server.send(200, "text/plain", "ENA OFF");
}

void handleOutputDIROn() {
  digitalWrite(pinOutput_DIR, HIGH);
  server.send(200, "text/plain", "DIR ON");
}

void handleOutputDIROff() {
  digitalWrite(pinOutput_DIR, LOW);
  server.send(200, "text/plain", "DIR OFF");
}

void handlePulse() {
  // Generar pulsos de 1000 microsegundos durante 1 segundo
  unsigned long startTime = millis();
  while (millis() - startTime < 1000) {
    digitalWrite(pinOutput_PUL, HIGH);
    delayMicroseconds(500);
    digitalWrite(pinOutput_PUL, LOW);
    delayMicroseconds(500);
  }
  server.send(200, "text/plain", "Pulses Sent for 1 second");
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("WiFi connected");

  // Imprime la dirección IP obtenida
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  // Configura los pines de salida
  pinMode(pinOutput_ENA, OUTPUT);
  pinMode(pinOutput_DIR, OUTPUT);
  pinMode(pinOutput_PUL, OUTPUT);

  // Configura los pines en estado inicial
  digitalWrite(pinOutput_ENA, HIGH); // El motor está apagado inicialmente
  digitalWrite(pinOutput_DIR, LOW); // El sentido de giro es hacia adelante inicialmente
  digitalWrite(pinOutput_PUL, LOW); // El pulso está en estado bajo inicialmente

  server.on("/", handleRoot);
  server.on("/ena/on", handleOutputENAOn);
  server.on("/ena/off", handleOutputENAOff);
  server.on("/dir/on", handleOutputDIROn);
  server.on("/dir/off", handleOutputDIROff);
  server.on("/pulse", handlePulse);

  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient();
}
