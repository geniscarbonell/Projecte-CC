# 🛰️ Projecte sistema satèl·lit · Grup 10

**✍️ Autors:** Ariadna Lidón, Hector Bolinches i Genís Carbonell

## Descripció

Sistema de telemetria format per un satèl·lit i una estació de terra que rep les dades i les mostra en una gràfica en temps real.

[Video explicatiu](https://drive.google.com/file/d/1YVK6f3NRIM-fzeQEjJVQF9k6bBLmN8r8/view?usp=sharing)

## 🏗️ Estructura del projecte

| Component | Funció |
|---|---|
| **Satèl·lit** | Un sensor de temperatura i humitat mesura les dades i les envia per port sèrie a l'estació de terra. Un sensor ultrasònic detecta els objectes propers i mostra els valors en una gràfica radar. |
| **Estació de terra** | Programa en Python que llegeix les dades i les representa en una gràfica. Permet iniciar, parar, reprendre la recepció, calcular mitjanes, valors màxims i avisar a l'usuari quan es detecta un error de comunicació o de detecció|


## ✅ Requisits

- 🤖 Arduino Uno, sensor DHT i LEDs
- 🐍Python 3.x amb les llibreries:
- ⚙️Servomotor y mòdul ultrasònic
```
  pip install pyserial matplotlib
```

## Com executar-ho

1. Carrega el codi del satèl·lit a l'Arduino 
2. Comprova el port COM a Arduino
3. Modifica la variable `COM` al codi de l'estació de terra amb aquest port
4. Tanca el Monitor Sèrie de l'Arduino IDE (si no, el port estarà ocupat)
5. Executa l'estació de terra:
```
   estacio_Terra.py
```
6. Usa els botons INICIAR, PARAR, REANUDAR CALCULAR MITJANA TEMPERATURA I HUMITAT I CANVIAR FREQÜÈNCIA D'ENVIAMENT DE DADES per controlar la recepció.

## 📢 Estat actual

- [x] Lectura de temperatura, humitat (DHT11) i distància (sensor ultrasònic amb servomotor)
- [x] Enviament de dades i ordres per port sèrie bidireccional (Satèl·lit ↔ Estació de Terra Arduino ↔ Python)
- [x] Gràfica en temps real (temperatura, humitat i mitjana) i radar d'ultrasons a l'estació de terra
- [x] Botons d'iniciar, parar i reprendre la recepció
- [x] Sistema de *Heartbeat* (batec cada 6 s) amb detecció i LED d'alarma per pèrdua de comunicació
- [x] Verificació d'integritat mitjançant *checksum* i botó de simulació d'errors amb comptador de trames descartades
- [x] Posar constants als `pinMode`
- [x] L'usuari pot escollir on es calcula la mitjana de les últimes 10 lectures (Satèl·lit o Terra) i establir un límit màxim de temperatura amb alarma sonora (*buzzer*)
- [x] L'usuari pot canviar el període d'enviament de dades de temperatura i humitat
- [x] Registre d'esdeveniments (`registro_eventos.txt`) amb desat d'ordres, alarmes, observacions manuals i filtres per tipus i data/hora
- [x] El codi està estructurat, indentat i amb comentaris clarificadors
- [ ] Fer que, en reprendre la recepció, la gràfica continuï amb l'eix del temps real en lloc de comptar mostres consecutives
- [ ] Completar al codi del satèl·lit la recepció de les ordres `ModoRastreo` i `Angulo:X` (ja preparades a la interfície de Python) per fixar un angle estàtic al radar
- [ ] Aplicar també el canvi de freqüència d'enviament a les dades del sensor de distància
