#include <SoftwareSerial.h>
SoftwareSerial mySerial(10, 11); // RX, TX

unsigned long previousMillisStatus = 0;
unsigned long previousMillisComunicacio = 0; 

const long intervalLed = 1000;
const long intervalLedComunicacio = 7000; // Cada quant comprova si s'ha rebut el batec

bool ledStatus = false;

void setup() {
   Serial.begin(9600);
   mySerial.begin(9600);
   
   // Reduïm l'espera del readString() perquè els LEDs s'apaguin a temps
   mySerial.setTimeout(10);
   Serial.setTimeout(10);
   
   pinMode(6, OUTPUT); // LED Status
   pinMode(4, OUTPUT); // LED Comunicació
}

void loop() {

   if (mySerial.available()) {
      String data = mySerial.readStringUntil('\n'); 
      Serial.println(data); 

      // Encenem el LED de Status (Pin 6)
      if (data.startsWith("1")) {
         digitalWrite(6, HIGH);
         ledStatus = true;
         previousMillisStatus = millis(); 
      }

      data.trim(); // Esborra el \r i el \n del final

      if (data.startsWith("3")) {
         digitalWrite(4, LOW);
         previousMillisComunicacio = millis(); 
      } 
   }

   // Control de temps per al LED de Status (Pin 6)
   if (ledStatus && (millis() - previousMillisStatus >= intervalLed)) {
      digitalWrite(6, LOW);
      ledStatus = false;
   }

   // Control de temps per al LED de fallo de comunicaió (Pin 4)
   if (millis() - previousMillisComunicacio >= intervalLedComunicacio) {
      digitalWrite(4, HIGH);
   }

   // Enviar al satèl·lit si la interfaz ha ordenat algo amb els botons
   if (Serial.available()) {
      String mensaje = Serial.readString(); 
      mySerial.print(mensaje);
   }
}
