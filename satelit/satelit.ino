#include <SoftwareSerial.h>
SoftwareSerial mySerial(10, 11);  // RX, TX

// Sensor temperatura i humitat
#include <DHT.h>
#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// Pins digitals


// Controls de temps de leds i sensor 
unsigned long nextHT = 0;
unsigned long nextTimeoutHT = 0;
unsigned long previousMillis = 0;
unsigned long previousLatido = 0;

unsigned long intervalEnviament = 2000; // Per defecte cada 2 segons
const long intervalLed = 1000;
bool esperandoTimeout = false;
bool led = false;
const long latido = 6000;


bool enviarDatos = true;

// Declaracions per a clacular la mitjana
float temperaturas[10];
float contador = 0;
float media = 0;
float mediamax = 30;
int contadormax = 0;
int i = 0;
bool calcularMitjana = false;



void setup() {

  Serial.begin(9600);
  mySerial.begin(9600);
  dht.begin();

  // Reduïm el timeout que es genera al llegir els strings
  mySerial.setTimeout(10);
  
  pinMode(7, OUTPUT);
  pinMode(4, OUTPUT);
}



void loop() {

  // Recepción de órdenes de la estación Tierra
  if (mySerial.available()) {
    String mensaje = mySerial.readStringUntil('\n');
    mensaje.trim();

    if (mensaje == "Parar") {
      enviarDatos = false;
    }

    if (mensaje == "Reanudar") {
      enviarDatos = true;
    }

    // Seleccionar dónde se realiza el cálculo
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




    // CAMBIO: recibir el nuevo límite de temperatura desde Tierra
    if (mensaje.startsWith("LimiteTemperatura:")) {
      mediamax = mensaje.substring(18).toFloat();
      contadormax = 0;

      Serial.print("Nuevo límite de temperatura: ");
      Serial.println(mediamax);
    }

        // Rebre la nova freqüència d'enviament (en mil·lisegons)
    if (mensaje.startsWith("Frecuencia:")) {
      unsigned long novaFreq = mensaje.substring(11).toInt();

      if (novaFreq >= 1000) { // Protecció: el sensor DHT11 necessita mínim 1 segon
        intervalEnviament = novaFreq;
        nextHT = millis() + intervalEnviament;
      } 
    } 
  }

  if (enviarDatos == true) {

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

        digitalWrite(4, LOW);
        digitalWrite(7, HIGH);

        previousMillis = millis();

        mySerial.print("1:");
        mySerial.print("T:");
        mySerial.print(t);
        mySerial.print(":");
        mySerial.print("H:");
        mySerial.println(h);

        // Cálculo de la media en el satélite
        if (calcularMitjana) {

          temperaturas[i] = t;
          i++;

          if (i == 10) {

            contador = 0;

            for (int d = 0; d < 10; d++) {
              contador = contador + temperaturas[d];
            }

            media = contador / 10;

            mySerial.print("4:");
            mySerial.print("Media:");
            mySerial.println(media);

            // Desplazar las temperaturas para conservar las 9 últimas
            for (int j = 0; j < 9; j++) {
              temperaturas[j] = temperaturas[j + 1];
            }

            i = 9;

            // CAMBIO: comprobar el límite configurable
            if (media > mediamax) {
              contadormax++;

              if (contadormax == 3) {
                mySerial.println("Límite temperatura");
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
      digitalWrite(4, HIGH);
    }
  }

  if (led && (millis() - previousMillis >= intervalLed)) {
    digitalWrite(7, LOW);
    led = false;
  }

  if (millis() - previousLatido >= latido) {
    previousLatido = millis();
    mySerial.println("3:");
  }
}
