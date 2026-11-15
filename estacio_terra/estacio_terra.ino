#include <SoftwareSerial.h>
SoftwareSerial mySerial(10, 11); // RX, TX

const int buzzerPin = 8;

unsigned long previousMillisStatus = 0;
unsigned long previousMillisComunicacio = 0; 
unsigned long previousMillisBuzzer = 0;

const long intervalLed = 1000; // Temps en milisegons que els leds estan encesos
const long intervalLedComunicacio = 7000; // Cada quant comprova si s'ha rebut el batec en milisegons
const long intervalBuzzer = 500; 

bool ledStatus = false;

void setup() {
   Serial.begin(9600);
   mySerial.begin(9600);
   
   // Reduïm l'espera del readString() per a no aturar durant molt temps el codi
   mySerial.setTimeout(10);
   Serial.setTimeout(10);
   
   pinMode(6, OUTPUT); // LED Status
   pinMode(4, OUTPUT); // LED Comunicació
   pinMode(buzzerPin, OUTPUT); // Buzzer
}

void loop() {

   if (mySerial.available()) {
      String data = mySerial.readStringUntil('\n'); 
      Serial.println(data); 

      // Encenem el LED de Status 
      if (data.startsWith("1")) {
         digitalWrite(6, HIGH);
         ledStatus = true;
         previousMillisStatus = millis(); 
      }

      data.trim(); // Esborra el \r i el \n del final

      // Heartbeat
      if (data.startsWith("3")) {
         digitalWrite(4, LOW);
         previousMillisComunicacio = millis(); 
      } 

      if (data.startsWith("L")) {
         tone(buzzerPin, 2000);
         previousMillisBuzzer = millis();
      }

   }

   // Control de temps per al LED de Status 
   if (ledStatus && (millis() - previousMillisStatus >= intervalLed)) {
      digitalWrite(6, LOW);
      ledStatus = false;
   }

   // Control de temps per al LED de fallo de comunicaió 
   if (millis() - previousMillisComunicacio >= intervalLedComunicacio) {
      digitalWrite(4, HIGH);
   }

   // Control de temps per al Buzzer 
   if (millis() - previousMillisBuzzer >= intervalBuzzer) {
      noTone(buzzerPin);
   }

   // Enviar al satèl·lit si la interfaz ha ordenat algo amb els botons
   if (Serial.available()) {
      String mensaje = Serial.readString(); 
      mySerial.print(mensaje);
   }
}
