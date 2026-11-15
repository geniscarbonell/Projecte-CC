const int trigPin = 9;
const int echoPin = 8;

unsigned long anterior = 0;

long duracion;
float distancia;

void setup() {

  Serial.begin(9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {

  if (millis() - anterior >= 50) {

    anterior = millis();
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);  //Esto, básicamente es como un gatillo, le dice que active el trigPin que, los 10 microsegundos son mínimamente necesarios para que se encienda
    digitalWrite(trigPin, LOW);

    /* mide cuantos microsegundos tarda en volver el eco, si en 15 milisegundos no detecta nada corta la espera para no congelar el programa
    tiene hasta 2,5 m de rango para detectar. multiplicamos el tiempo por 0,034 (velocidad sonido en cm/microsec) y divide entre 2 (ida y vuelta) */
    distancia = pulseIn(echoPin, HIGH, 15000) * 0.034 / 2; 
    Serial.println(distancia);
  }
}
