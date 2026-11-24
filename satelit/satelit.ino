#include <SoftwareSerial.h>
#include <Servo.h>
#include <DHT.h>

SoftwareSerial mySerial(10, 11);  // RX, TX

// Sensor temperatura i humitat
#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// Pins digitals LEDs
const int ledEnviamentPin = 7;
const int ledErrorPin = 4;

// Pins digitals Radar Ultrasons
const int trigPin = 9;
const int echoPin = 8;
const int servoPin = 12;

// Variables Radar (1 grau cada 50ms = 20 graus/segon -> envia 1 dada cada 10 graus)
Servo servoMotor;
float anguloActual = 0;
float angulo = 1.0; 
unsigned long duracionServo = 0;
const long intervalServo = 50;
unsigned long anterior = 0;
unsigned long anteriorEnvioRadar = 0;
const long intervalEnvioRadar = 500; // Enviament cada mig segon (500 ms)
float distancia = 0;

// Controls de temps de leds i sensor 
unsigned long nextHT = 0;
unsigned long nextTimeoutHT = 0;
unsigned long previousMillis = 0;
unsigned long previousLatido = 0;

unsigned long intervalEnviament = 2000;
const long intervalLed = 1000;
bool esperandoTimeout = false;
bool led = false;
const long latido = 6000;

bool enviarDatos = true;

// Declaracions per a calcular la mitjana
float temperaturas[10];
float contador = 0;
float media = 0;
float mediamax = 30;
int contadormax = 0;
int i = 0;
bool calcularMitjana = false;

// Simulació d'errors de transmissió (s'activa des de l'estació de terra)
bool simularError = false;


// Checksum: suma de tots els bytes del missatge, truncada a 1 byte (mòdul 256)
byte calcularChecksum(const String &msg) {
  byte suma = 0;
  for (unsigned int k = 0; k < msg.length(); k++) {
    suma += (byte)msg[k];   // el byte desborda i queda truncat automàticament
  }
  return suma;
}

// Envia un missatge amb el format  <missatge>*<checksum en hexadecimal>
void enviarMensaje(String msg) {
  // 1. Es calcula el checksum del missatge ORIGINAL
  byte cs = calcularChecksum(msg);

  // 2. Si la simulació està activa, s'altera el missatge DESPRÉS de calcular el checksum
  //    (aproximadament 1 de cada 3 missatges: es canvia 1 bit d'un caràcter a l'atzar)
  if (simularError && msg.length() > 0 && random(3) == 0) {
    int pos = random(msg.length());
    msg.setCharAt(pos, msg[pos] ^ 0x01);
  }

  // 3. Es transmet el missatge (potser alterat) amb el checksum original
  mySerial.print(msg);
  mySerial.print('*');
  if (cs < 16) mySerial.print('0');   // sempre 2 dígits hexadecimals
  mySerial.println(cs, HEX);
}


void setup() {
  
  Serial.begin(9600);
  mySerial.begin(9600);
  dht.begin();
  mySerial.setTimeout(10);
  randomSeed(analogRead(A0));   // A0 sense connectar -> llavor aleatòria
  
  pinMode(ledEnviamentPin, OUTPUT);
  pinMode(ledErrorPin, OUTPUT);

  // Configuració Radar
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  servoMotor.attach(servoPin);
  servoMotor.write(0);
}


void loop() {

  // 1. Recepción de órdenes de la estación Tierra
  if (mySerial.available()) {
    String mensaje = mySerial.readStringUntil('\n');
    mensaje.trim();

    if (mensaje == "Parar") {
      enviarDatos = false;
    }

    if (mensaje == "Reanudar") {
      enviarDatos = true;
    }

    if (mensaje == "SatelitCalcul") {
      calcularMitjana = true;
      i = 0;
      contadormax = 0;
    }

    if (mensaje == "TerraCalcul") {
      calcularMitjana = false;
      i = 0;
      contadormax = 0;
    }

    if (mensaje == "ErrorOn") {
      simularError = true;
    }

    if (mensaje == "ErrorOff") {
      simularError = false;
    }

    if (mensaje.startsWith("LimiteTemperatura:")) {
      mediamax = mensaje.substring(18).toFloat();
      contadormax = 0;
    }

    if (mensaje.startsWith("Frecuencia:")) {
      unsigned long novaFreq = mensaje.substring(11).toInt();
      if (novaFreq >= 1000) {
        intervalEnviament = novaFreq;
        nextHT = millis() + intervalEnviament;
      } 
    } 
  }

  // 2. Enviament de dades quan està actiu
  if (enviarDatos == true) {

    // --- PART RADAR ULTRASONS ---
    if (millis() - anterior >= 60) {
      anterior = millis();
      digitalWrite(trigPin, LOW);
      delayMicroseconds(2);
      digitalWrite(trigPin, HIGH);
      delayMicroseconds(10);
      digitalWrite(trigPin, LOW);

      distancia = pulseIn(echoPin, HIGH, 15000) * 0.034 / 2;
    }

    if (millis() - duracionServo >= intervalServo) {
      duracionServo = millis();
      anguloActual = anguloActual + angulo;

      if (anguloActual >= 180) {
        anguloActual = 180;
        angulo = -angulo;
      } else if (anguloActual <= 0) {
        anguloActual = 0;
        angulo = -angulo;
      }
      servoMotor.write((int)anguloActual);
    }

    // Enviament de dades del radar amb prefix "2:" cada mig segon (500 ms)
    if (millis() - anteriorEnvioRadar >= intervalEnvioRadar) {
      anteriorEnvioRadar = millis();
      enviarMensaje("2:" + String(anguloActual) + ":" + String(distancia));
    }

    // --- PART TEMPERATURA I HUMITAT ---
    if (millis() >= nextHT) {
      nextHT = millis() + intervalEnviament;

      float h = dht.readHumidity();
      float t = dht.readTemperature();

      if (isnan(h) || isnan(t)) {
        if (!esperandoTimeout) {
          esperandoTimeout = true;
          nextTimeoutHT = millis() + 5000;
        }
      } else {
        esperandoTimeout = false;
        led = true;

        digitalWrite(ledErrorPin, LOW);
        digitalWrite(ledEnviamentPin, HIGH);
        previousMillis = millis();

        enviarMensaje("1:T:" + String(t) + ":H:" + String(h));

        if (calcularMitjana) {
          temperaturas[i] = t;
          i++;

          if (i == 10) {
            contador = 0;
            for (int d = 0; d < 10; d++) {
              contador = contador + temperaturas[d];
            }

            media = contador / 10;
            enviarMensaje("4:Media:" + String(media));

            for (int j = 0; j < 9; j++) {
              temperaturas[j] = temperaturas[j + 1];
            }
            i = 9;

            if (media > mediamax) {
              contadormax++;
              if (contadormax == 3) {
                enviarMensaje("Límite temperatura");
                contadormax = 0;
              }
            } else {
              contadormax = 0;
            }
          }
        }
      }
    }

    if (esperandoTimeout && (millis() >= nextTimeoutHT)) {
      digitalWrite(ledErrorPin, HIGH);
    }
  }

  if (led && (millis() - previousMillis >= intervalLed)) {
    digitalWrite(ledEnviamentPin, LOW);
    led = false;
  }

  if (millis() - previousLatido >= latido) {
    previousLatido = millis();
    enviarMensaje("3:");
  }
}
