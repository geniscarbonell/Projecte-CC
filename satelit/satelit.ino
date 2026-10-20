#include <DHT.h>
#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

#include <SoftwareSerial.h>
int i;
SoftwareSerial mySerial(10, 11); // RX, TX 

bool enviarDatos = true;


void setup() {
  Serial.begin(9600);
  dht.begin();

  mySerial.begin(9600);
  mySerial.println("Empezamos");
  i=1;
  
  pinMode(7, OUTPUT);
}
void loop() {
  if (enviarDatos == true){
   delay(2000);
   float h = dht.readHumidity();
   float t = dht.readTemperature();
   if (isnan(h) || isnan(t))
      mySerial.println("Error al leer el sensor DHT11");
   else {
      digitalWrite(7, HIGH);
      delay(500);
      digitalWrite(7, LOW);

      mySerial.print("T:");
      mySerial.print(t);
      mySerial.print(":");

      mySerial.print("H:");
      mySerial.println(h);
   
   }}
  
  if (mySerial.available()) {
    String mensaje = mySerial.readString();
    
    if (mensaje == "Parar") {
      enviarDatos = false;
      while (enviarDatos == false){
        mySerial.print("T:");
        mySerial.print(NAN);
        mySerial.print(":");

        mySerial.print("H:");
        mySerial.println(NAN);
      }
    }

    if (mensaje == "Reanudar") {
      enviarDatos = true;
      digitalWrite(7, HIGH);
      delay(500);
      digitalWrite(7, LOW);
    }
  }
}