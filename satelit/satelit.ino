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

float temperaturas[10];
float contador=0;
float media=0;
float mediamax=30;
int contadormax=0;
int i=0;



//Debe incorporarse a las gráficas que se muestran al usuario una que presente la evolución en el tiempo del valor medio de los 10 últimos 
//valores de temperatura. Además, el sistema debe mostrar una alarma al usuario en el caso de que se detecten tres valores medios 
//consecutivos superiores a un valor límite especificado por el usuario.



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

        temperaturas[i]=t;
        //càlcul de les mitjes
        if (i==9){
          contador=0;
          for (int d=0; d<10; d++){
            contador = contador+temperaturas[d]; 
          }
          media = contador/10;
          mySerial.print("4:");
          mySerial.print("Media:");
          mySerial.println(media);
          int j=0;
          for (int j = 0; j < 9; j++) {
          temperaturas[j] = temperaturas[j+1];
          }
          i=8;
          if (media>mediamax){
            contadormax++;
            if (contadormax==3){
              mySerial.println("Límite temperatura");
              contadormax=0;
            }
          }
        }
        

      i=i+1; 

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