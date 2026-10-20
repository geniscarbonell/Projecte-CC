#include <SoftwareSerial.h>
SoftwareSerial mySerial(10, 11); // RX, TX 
unsigned long nextMillis = 500;

void setup() {
   Serial.begin(9600);
   mySerial.begin(9600);
   
   pinMode(6, OUTPUT);
}

void loop() {
   if (mySerial.available()) {
      String data = mySerial.readString();
      Serial.print(data);

      digitalWrite(6, HIGH);
      delay(200);
      digitalWrite(6, LOW);
   }

   if (Serial.available()) {
      String mensaje = Serial.readString();
      mySerial.print(mensaje);
   }
}