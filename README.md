# Projecte sistema satèl·lit · Grup 10

**Autors:** Ariadna Lidón, Hector Bolinches i Genís Carbonell

## Descripció

Sistema de telemetria format per un satèl·lit (Arduino amb sensor) i una estació de terra (ordinador) que rep les dades i les mostra en una gràfica en temps real.

## Estructura del projecte

| Component | Funció |
|---|---|
| **Satèl·lit** | Un sensor de temperatura i humitat (`<model del sensor>`) mesura les dades i les envia per port sèrie a l'estació de terra. |
| **Estació de terra** | Programa en Python que llegeix les dades i les representa en una gràfica. Permet **iniciar**, **parar** i **reprendre** la recepció. |

```
Sensor → Arduino (satèl·lit) → port sèrie (9600 baud) → Python (estació de terra) → gràfica
```

## Format de les dades

L'Arduino envia una línia de text per mostra, per exemple:

```
T:25.3:H:60.1
```

on `T` és la temperatura (°C) i `H` la humitat relativa (%).

## Requisits

- Arduino `<model>` i sensor `<model>`
- Python 3.x amb les llibreries:
```
  pip install pyserial matplotlib
```
  (Tkinter ja ve inclòs amb Python a Windows.)

## Com executar-ho

1. Carrega el codi del satèl·lit a l'Arduino (`<carpeta/fitxer>`).
2. Comprova el port COM de l'Arduino a l'Administrador de dispositius.
3. Modifica la variable `PUERTO` al codi de l'estació de terra amb aquest port.
4. Tanca el Monitor Sèrie de l'Arduino IDE (si no, el port estarà ocupat).
5. Executa l'estació de terra:
```
   python Claude.py
```
6. Usa els botons **INICIAR**, **PARAR** i **REANUDAR** per controlar la recepció.

## Estat actual

- [x] Lectura de temperatura i humitat amb el sensor
- [x] Enviament de dades per port sèrie
- [x] Gràfica a l'estació de terra
- [x] Botons d'iniciar, parar i reprendre
- [ ] Eliminar els `delay()` dels codis d'Arduino (substituir-los per `millis()`)
- [ ] Fer que, en reprendre la recepció, la gràfica continuï des d'on tocava

## Millores futures

- Guardar les dades en un fitxer CSV
- Mostrar els valors actuals en etiquetes
