#include <WiFi.h>
#include <WebServer.h>

// Configura el SSID y la contraseña de tu red WiFi
const char* ssid = "Aula tecnica";
const char* password = "Madygraf32";
const char* backupSSID = "Backup SSID";
const char* backupPassword = "BackupPassword";

const int maxAttempts = 5; // Número máximo de intentos de conexión
const unsigned long wifiTimeout = 10000; // Timeout para la conexión WiFi (10 segundos)

// Configura los pines de salida
const int pinOutput_ENA = 18; // enciende el motor con LOW
const int pinOutput_DIR = 19; // sentido de giro
const int pinOutput_PUL = 21; // pulso, debe tener 1000 microsegundos entre semiciclo positivo y negativo

const unsigned long pulseDuration = 1000; // Duración del pulso en milisegundos
const unsigned int pulseWidth = 500; // Ancho del pulso en microsegundos

WebServer server(80);
TaskHandle_t PulseTaskHandle = NULL;

// Función para conectar a WiFi
bool connectToWiFi(const char* ssid, const char* password) {
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");

    unsigned long startAttemptTime = millis();

    // Espera hasta que se conecte al WiFi con un timeout
    while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < wifiTimeout) {
        delay(500);
        Serial.print(".");
    }

    // Verifica si se conectó al WiFi
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nWiFi connected");
        Serial.print("IP address: ");
        Serial.println(WiFi.localIP());
        return true;
    } else {
        Serial.println("\nFailed to connect to WiFi");
        return false;
    }
}

// Función para intentar conectar a WiFi con reintentos
bool tryConnectToWiFi() {
    bool connected = false;
    int attempt = 0;

    // Intento de conexión principal
    while (!connected && attempt < maxAttempts) {
        connected = connectToWiFi(ssid, password);
        attempt++;
    }

    // Intento de conexión de respaldo
    if (!connected) {
        Serial.println("Attempting to connect to backup WiFi");
        attempt = 0;
        while (!connected && attempt < maxAttempts) {
            connected = connectToWiFi(backupSSID, backupPassword);
            attempt++;
        }
    }

    // Manejo del fallo total de conexión
    if (!connected) {
        Serial.println("Failed to connect to both WiFi networks.");
        // Implementar manejo de error adicional aquí, si es necesario
    }

    return connected;
}

// Función para manejar la generación de pulsos
void pulseTask(void* parameter) {
    unsigned long startTime = millis();
    while (millis() - startTime < pulseDuration) {
        digitalWrite(pinOutput_PUL, HIGH);
        delayMicroseconds(pulseWidth);
        digitalWrite(pinOutput_PUL, LOW);
        delayMicroseconds(pulseWidth);
    }

    // Apaga el motor después de 1 segundo
    digitalWrite(pinOutput_ENA, HIGH);
    Serial.println("Motor turned off after 1 second");

    // Detiene la tarea
    vTaskDelete(NULL);
}

// Función para habilitar el motor
void enableMotor(bool forward) {
    digitalWrite(pinOutput_DIR, forward ? LOW : HIGH);
    digitalWrite(pinOutput_ENA, LOW);
    Serial.println(forward ? "Motor Forward for 1 second" : "Motor Reverse for 1 second");

    // Crea una tarea para generar los pulsos
    xTaskCreate(
        pulseTask,          // Función de la tarea
        "PulseTask",        // Nombre de la tarea
        10000,              // Tamaño de la pila
        NULL,               // Parámetro de entrada
        1,                  // Prioridad de la tarea
        &PulseTaskHandle    // Puntero al manejador de la tarea
    );
}

// Manejadores de las rutas del servidor
void handleRoot() {
    server.send(200, "text/plain", "ESP32 Web Server");
}

void handleEnableMotorForward() {
    enableMotor(true);
    server.send(200, "text/plain", "Motor Forward");
}

void handleEnableMotorReverse() {
    enableMotor(false);
    server.send(200, "text/plain", "Motor Reverse");
}

// Configura los pines de salida y sus estados iniciales
void setupOutputPins() {
    pinMode(pinOutput_ENA, OUTPUT);
    pinMode(pinOutput_DIR, OUTPUT);
    pinMode(pinOutput_PUL, OUTPUT);

    // Configura los pines en estado inicial
    digitalWrite(pinOutput_ENA, HIGH); // El motor está apagado inicialmente
    digitalWrite(pinOutput_DIR, LOW);  // El sentido de giro es hacia adelante inicialmente
    digitalWrite(pinOutput_PUL, LOW);  // El pulso está en estado bajo inicialmente
}

// Configura las rutas del servidor
void setupServerRoutes() {
    server.on("/", handleRoot);
    server.on("/ena_f", handleEnableMotorForward);
    server.on("/ena_r", handleEnableMotorReverse);
}

void setup() {
    Serial.begin(115200);

    // Intentar conectar a WiFi
    bool connected = tryConnectToWiFi();

    // Continuar con la configuración incluso si la conexión falla
    setupOutputPins();
    setupServerRoutes();
    server.begin();
    Serial.println("HTTP server started");

    // Mensaje si la conexión WiFi falla
    if (!connected) {
        Serial.println("Running without WiFi connection.");
    }
}

void loop() {
    server.handleClient();
}
