const int led1 = 13;  // LED en el pin 13 (Amarillo)
const int led2 = 12;  // LED en el pin 12 (Rojo)
const int led3 = 11;  // LED en el pin 11 (Verde)

int nextMillis1;
int nextMillis2;
int nextMillis3;

const long interval1 = 2000; // 2 segundos para el LED 13
const long interval2 = 3000; // 3 segundos para el LED 12
const long interval3 = 5000; // 5 segundos para el LED 11

bool stateLed1 = LOW;
bool stateLed2 = LOW;
bool stateLed3 = LOW; 

void setup() {
    
    Serial.begin(9600);

    pinMode(led1, OUTPUT);
    pinMode(led2, OUTPUT);
    pinMode(led3, OUTPUT);
    // primer instante en el que habrá que cambiar
    nextMillis1 = millis() + interval1;
    nextMillis2 = millis() + interval2;
    nextMillis3 = millis() + interval3;
}

void loop() {
    // Control del LED en el pin 13 (2 segundos)
    if (millis() >= nextMillis1) {
        // Ya toca cambiar
        if (stateLed1 == LOW)
             stateLed1 = HIGH;
        else
             stateLed1 = LOW;
        digitalWrite(led1, stateLed1);
        // Siguiente instante en el que habrá que cambiar
        nextMillis1 = millis() + interval1;
    }

    // Control del LED en el pin 12 (3 segundos)
    if (millis() >= nextMillis3) {
       if (stateLed3 == LOW)
             stateLed3 = HIGH;
        else
             stateLed3 = LOW;
        digitalWrite(led3, stateLed3);
        nextMillis3 = millis() + interval3;
    }

    //Serial.println("Segueixo aquí");
    //delay(10000);

        // Control del LED en el pin 11 (5 segundos)
    if (millis() >= nextMillis2) {
       if (stateLed2 == LOW)
             stateLed2 = HIGH;
        else
             stateLed2 = LOW;
        digitalWrite(led2, stateLed2);
        nextMillis2 = millis() + interval2;
    }
}