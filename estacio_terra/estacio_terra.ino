#include <SoftwareSerial.h>
SoftwareSerial mySerial(10, 11); // RX, TX

// Pins digitals  
const int ledStatusPin = 6;
const int ledComunicacioPin = 4;
const int buzzerPin = 8;

// Controls de temps de leds i buzzer
unsigned long previousMillisStatus = 0;
unsigned long previousMillisComunicacio = 0; 
unsigned long previousMillisBuzzer = 0;

const long intervalLed = 1000; 
const long intervalLedComunicacio = 7000; 
const long intervalBuzzer = 500; 

bool ledStatus = false;
bool calcularMitjana = false;

// Declaracions per a calcular la mitjana aquí
float temperaturas[10];
float contador = 0;
float media = 0;
float mediamax = 30;
int contadormax = 0;
int i = 0;



void setup() {

   Serial.begin(9600);
   mySerial.begin(9600);
   
   // Reduïm el timeout que es genera al llegir els strings
   mySerial.setTimeout(10);
   Serial.setTimeout(10);
   
   pinMode(ledStatusPin, OUTPUT); // LED Status
   pinMode(ledComunicacioPin, OUTPUT); // LED Comunicació
   pinMode(buzzerPin, OUTPUT); // Buzzer
}



void loop() {

   // 1. RECEPCIÓ DEL SATÈL·LIT
   if (mySerial.available()) {
      String data = mySerial.readStringUntil('\n'); 
      Serial.println(data); 
      data.trim(); 

      // Led status i calcul de mitjana local
      if (data.startsWith("1:")) {
         digitalWrite(ledStatusPin, HIGH);
         ledStatus = true;
         previousMillisStatus = millis(); 

         if (calcularMitjana == true) {
            int inici = data.indexOf(":T:");
            if (inici != -1) {
               inici += 3;
               int fi = data.indexOf(":", inici);
               
               temperaturas[i] = data.substring(inici, fi).toFloat();

               if (i == 9) {
                  contador = 0;

                  for (int d = 0; d < 10; d++)
                     contador = contador + temperaturas[d]; 
                  
                  media = contador / 10;
                  Serial.print("4:Media:");
                  Serial.println(media);

                  for (int j = 0; j < 9; j++) 
                     temperaturas[j] = temperaturas[j + 1];
                  i = 8;

                  if (media > mediamax) {
                     contadormax++;
                     if (contadormax == 3) {
                        Serial.println("Límite temperatura");
                        tone(buzzerPin, 2000);        
                        previousMillisBuzzer = millis();
                        contadormax = 0;
                     }
                  } else {
                     contadormax = 0;
                  }
               }
               i = i + 1; 
            }
         }
      }

      // Heartbeat
      if (data.startsWith("3:")) {
         digitalWrite(ledComunicacioPin, LOW);
         previousMillisComunicacio = millis(); 
      } 

      // Alarma si es supera el límit de temperatura
      if (data == "Límite temperatura") {
         tone(buzzerPin, 2000);
         previousMillisBuzzer = millis();
      }
   }

   // Control de temps per al LED de Status 
   if (ledStatus && (millis() - previousMillisStatus >= intervalLed)) {
      digitalWrite(ledStatusPin, LOW);
      ledStatus = false;
   }

   // Control de temps per al LED de fallo de comunicació 
   if (millis() - previousMillisComunicacio >= intervalLedComunicacio) {
      digitalWrite(ledComunicacioPin, HIGH);
   }

   // Control de temps per al Buzzer 
   if (millis() - previousMillisBuzzer >= intervalBuzzer) {
      noTone(buzzerPin);
   }



   // 2. RECEPCIÓ DES DE PYTHON
   if (Serial.available()) {
      String mensaje = Serial.readStringUntil('\n'); 
      mensaje.trim();
      mySerial.println(mensaje);

      // Calcular la mitjana aquí
      if (mensaje == "TerraCalcul") {
         calcularMitjana = true;
         i = 0;
         contadormax = 0;
      }

      // Actualització del nou límit de temperatura
      if (mensaje.startsWith("LimiteTemperatura:")) {
         mediamax = mensaje.substring(18).toFloat();
         contadormax = 0;
      }

      // Transferir el calcul de la mitjana al satelit
      if (mensaje == "SatelitCalcul") {
         calcularMitjana = false;
         contadormax = 0;
      }
   }
}
