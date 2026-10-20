#include <SoftwareSerial.h>
int i;
SoftwareSerial mySerial(10, 11); // RX, TX 
unsigned long nextMillis = 500;


void setup() {
   Serial.begin(9600);
   mySerial.println("Empezamos");
   mySerial.begin(9600);
   i=1;

   Serial.println("Empezamos la recepción");
}
void loop() {
   if (mySerial.available()) {
      String data = mySerial.readString();
      Serial.print(data);
   }
   
   delay (3000);
   mySerial.print("Envío a: ");
   mySerial.println(i);
   i=i+1;

    
}

