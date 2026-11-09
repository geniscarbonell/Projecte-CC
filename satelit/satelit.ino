#include <DHT.h>
#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

#include <SoftwareSerial.h>
SoftwareSerial mySerial(10, 11);  // RX, TX
unsigned long nextHT = 0;
unsigned long nextTimeoutHT = 0;
unsigned long previousMillis = 0;
unsigned long previousLatido = 0;
const long intervalLed = 1000;
bool esperandoTimeout = false;
bool led = false;
const long latido = 6000;

bool enviarDatos = true;


void setup() {
  Serial.begin(9600);
  mySerial.begin(9600);
  dht.begin();

  pinMode(7, OUTPUT);
  pinMode(4, OUTPUT);
}

void loop() {
  if (enviarDatos == true) {

    if (millis() >= nextHT) {
      nextHT = millis() + 2000;
      float h = dht.readHumidity();
      float t = dht.readTemperature();

      if (isnan(h) || isnan(t)) {
        if (!esperandoTimeout) {
          esperandoTimeout = true;
          nextTimeoutHT = millis() + 5000;  //5 segundos
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

  if (mySerial.available()) {
    String mensaje = mySerial.readString();

    if (mensaje == "Parar") {
      enviarDatos = false;
    }

    if (mensaje == "Reanudar") {
      enviarDatos = true;
    }
  }
}