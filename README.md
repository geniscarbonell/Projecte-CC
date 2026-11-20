# 🛰️ Projecte sistema satèl·lit · Grup 10

**✍️ Autors:** Ariadna Lidón, Hector Bolinches i Genís Carbonell

## Descripció

Sistema de telemetria format per un satèl·lit i una estació de terra que rep les dades i les mostra en una gràfica en temps real.

[Video explicatiu]

##🏗️ Estructura del projecte

| Component | Funció |
|---|---|
| **Satèl·lit** | Un sensor de temperatura i humitat mesura les dades i les envia per port sèrie a l'estació de terra. Un sensor ultrasònic detecta els objectes propers i mostra els valors en una gràfica radar. |
| **Estació de terra** | Programa en Python que llegeix les dades i les representa en una gràfica. Permet iniciar, parar, reprendre la recepció, calcular mitjanes, valors màxims i avisar a l'usuari quan es detecta un error de comunicació o de detecció|


##✅ Requisits

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

##📢 Estat actual

- [x] Lectura de temperatura i humitat amb el sensor
- [x] Enviament de dades per port sèrie
- [x] Gràfica a l'estació de terra
- [x] Botons d'iniciar, parar i reprendre
- [x] Heartbeat
- [x] Tests unitàris
- [x] Posar constants als pinmodes
- [ ] Fer que, en reprendre la recepció, la gràfica continuï des d'on tocava
- [x] L'usuari pot escollir on es calculara la mitja de les últimes 10 dades de temperatura, i establir un valor màxim
- [x] L'usuari pot canviar el periode d'enviament de dades de temperatura, humitat i distància
- [x] El codi està estructurat, identat i amb comentaris clarificadors
- [x] El usuari pot posar el sensor de distància en mode rastreig i establir una orientació determinada per el sensor
