import threading
import time
import math
from tkinter import *
import queue

import serial
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Canvia el numero del COM al que et surti al arduino
device = 'COM7'
ser = serial.Serial(device, baudrate=9600)

datos_grafica = queue.Queue()


def recepcion():
    i = 0
    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').rstrip()
                if not line:
                    continue

                trozos = line.split(':')

                # Trama 1: Temperatura i Humitat
                if trozos == "1" and len(trozos) >= 5:
                    print(line)
                    temperatura = float(trozos)
                    humedad = float(trozos)
                    datos_grafica.put(("datos", i, temperatura, humedad))
                    i = i + 1

                # Trama 2: Radar Ultrasons (2:angulo:distancia)
                elif trozos == "2" and len(trozos) >= 3:
                    try:
                        angulo = float(trozos)
                        distancia = float(trozos)
                        datos_grafica.put(("radar", angulo, distancia))
                    except ValueError:
                        pass

                # Trama 4: Mitjana
                elif trozos == "4" and len(trozos) >= 3:
                    print(line)
                    media = float(trozos)
                    datos_grafica.put(("media", max(0, i - 1), media))

                else:
                    print(line)

    except KeyboardInterrupt:
        print("Saliendo...")
    finally:
        ser.close()


def Iniciar():
    threadRecepcion = threading.Thread(target=recepcion, daemon=True)
    threadRecepcion.start()


def Parar():
    ser.write("Parar\n".encode('utf-8'))


def Reanudar():
    ser.write("Reanudar\n".encode('utf-8'))


def TerraCalcul():
    ser.write("TerraCalcul\n".encode('utf-8'))


def SatelitCalcul():
    ser.write("SatelitCalcul\n".encode('utf-8'))


def EnviarLimite():
    try:
        limite = float(limiteTemperatura.get())
        if not math.isfinite(limite):
            estadoLimite.config(text="Introduce un número válido", fg="red")
            return

        mensaje = "LimiteTemperatura:" + str(limite) + "\n"
        ser.write(mensaje.encode('utf-8'))
        estadoLimite.config(text="Límite enviado: " + str(limite) + " °C", fg="green")
    except ValueError:
        estadoLimite.config(text="Introduce una temperatura válida", fg="red")


def EnviarFrecuencia():
    try:
        segons = float(frecuenciaDatos.get())
        if not math.isfinite(segons) or segons < 1:
            estadoFrecuencia.config(text="Mínimo 1 segundo", fg="red")
            return

        milisegons = int(segons * 1000)
        mensaje = "Frecuencia:" + str(milisegons) + "\n"
        ser.write(mensaje.encode('utf-8'))
        estadoFrecuencia.config(text="Enviado: cada " + str(segons) + " s", fg="green")
    except ValueError:
        estadoFrecuencia.config(text="Introduce un número válido", fg="red")


# --- CONFIGURACIÓ FINESTRA PRINCIPAL ---
window = Tk()
window.title("Estación de Tierra - Satélite y Radar")
window.geometry("1520x680")

window.rowconfigure(0, weight=1)
window.rowconfigure(1, weight=1)
window.rowconfigure(2, weight=4)

window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=1)
window.columnconfigure(2, weight=1)
window.columnconfigure(3, weight=2)


tituloLabel = Label(window, text="DATOS SATÉLITE", font=("Helvetica", 35))
tituloLabel.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky=N + S + E + W)

iniciarButton = Button(window, text="INICIAR", bg='green', fg="white", font=("Helvetica", 20), command=Iniciar)
iniciarButton.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)

pararButton = Button(window, text="PARAR", bg='red', fg="white", font=("Helvetica", 20), command=Parar)
pararButton.grid(row=1, column=1, padx=5, pady=5, sticky=N + S + E + W)

reanudarButton = Button(window, text="REANUDAR", bg='blue', fg="white", font=("Helvetica", 20), command=Reanudar)
reanudarButton.grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky=N + S + E + W)


# --- 1. PANELL ESQUERRA: GRÀFICA TEMP/HUMITAT ---
panel_grafica = Frame(window)
panel_grafica.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=N + S + E + W)

figura = Figure(figsize=(5.5, 4), dpi=100)
eje_unico = figura.add_subplot(111)

eje_unico.set_title("Temperatura, Humedad y Media")
eje_unico.set_xlabel("Tiempo (s)")
eje_unico.set_ylabel("Valor (°C / %)")
eje_unico.set_xlim(0, 100)
eje_unico.set_ylim(0, 100)
eje_unico.set_xticks(range(0, 101, 20))
eje_unico.set_yticks(range(0, 101, 20))
eje_unico.grid(True)

linea_temperatura, = eje_unico.plot([], [], color='blue', label='Temperatura (°C)')
linea_humedad, = eje_unico.plot([], [], color='green', label='Humedad (%)')
linea_media, = eje_unico.plot([], [], color='red', label='Media')
eje_unico.legend()

canvas = FigureCanvasTkAgg(figura, master=panel_grafica)
canvas.draw()
canvas.get_tk_widget().pack(fill=BOTH, expand=True)


# --- 2. PANELL CENTRAL: CONTROLS ---
panel_controles = LabelFrame(window, text="CONTROL DE CÁLCULO", font=("Helvetica", 12))
panel_controles.grid(row=2, column=2, padx=5, pady=5, sticky=N + S + E + W)

terraButton = Button(panel_controles, text="CÁLCULO ESTACIÓN TIERRA", bg='orange', fg="white", font=("Helvetica", 11), command=TerraCalcul)
terraButton.pack(fill=X, padx=5, pady=10)

satelitButton = Button(panel_controles, text="CÁLCULO SATÉLITE", bg='purple', fg="white", font=("Helvetica", 11), command=SatelitCalcul)
satelitButton.pack(fill=X, padx=5, pady=10)

limiteLabel = Label(panel_controles, text="Límite de temperatura (°C):", font=("Helvetica", 11))
limiteLabel.pack(padx=5, pady=10)

limiteTemperatura = StringVar()
limiteEntrada = Entry(panel_controles, textvariable=limiteTemperatura, font=("Helvetica", 14), justify=CENTER)
limiteEntrada.pack(fill=X, padx=5, pady=5)

enviarLimiteButton = Button(panel_controles, text="ENVIAR LÍMITE", bg='blue', fg="white", font=("Helvetica", 11), command=EnviarLimite)
enviarLimiteButton.pack(fill=X, padx=5, pady=10)

estadoLimite = Label(panel_controles, text="", font=("Helvetica", 10))
estadoLimite.pack(padx=5, pady=5)

frecuenciaLabel = Label(panel_controles, text="Frecuencia de envío (s):", font=("Helvetica", 11))
frecuenciaLabel.pack(padx=5, pady=10)

frecuenciaDatos = StringVar()
frecuenciaEntrada = Entry(panel_controles, textvariable=frecuenciaDatos, font=("Helvetica", 14), justify=CENTER)
frecuenciaEntrada.pack(fill=X, padx=5, pady=5)

enviarFrecuenciaButton = Button(panel_controles, text="ENVIAR FRECUENCIA", bg='teal', fg="white", font=("Helvetica", 11), command=EnviarFrecuencia)
enviarFrecuenciaButton.pack(fill=X, padx=5, pady=10)

estadoFrecuencia = Label(panel_controles, text="", font=("Helvetica", 10))
estadoFrecuencia.pack(padx=5, pady=5)


# --- 3. PANELL DRETA: ESCÀNER D'ULTRASONS ---
panel_radar = LabelFrame(window, text="ESCÁNER ULTRASONIDOS", font=("Helvetica", 12))
panel_radar.grid(row=2, column=3, padx=5, pady=5, sticky=N + S + E + W)

canvas_radar = Canvas(panel_radar, width=600, height=370, bg="black")
canvas_radar.pack(expand=True, fill=BOTH, padx=5, pady=5)

cx = 300
cy = 340
radio_max = 220
distancia_max = 50

puntos_verdes = []
ultima_deteccion = time.time()


def dibujar_fondo_radar():
    for distancia in range(10, 51, 10):
        radio = distancia * radio_max / distancia_max
        canvas_radar.create_arc(
            cx - radio, cy - radio,
            cx + radio, cy + radio,
            start=0, extent=180,
            style=ARC,
            outline="white",
            width=2
        )
        canvas_radar.create_text(
            cx + radio, cy + 15,
            text=str(distancia),
            font=("Arial", 10, "bold"),
            fill="white"
        )

    for angulo in range(0, 181, 30):
        rad = math.radians(angulo)
        x = cx + radio_max * math.cos(rad)
        y = cy - radio_max * math.sin(rad)
        canvas_radar.create_line(cx, cy, x, y, fill="white")

        xt = cx + (radio_max + 22) * math.cos(rad)
        yt = cy - (radio_max + 22) * math.sin(rad)
        canvas_radar.create_text(
            xt, yt,
            text=str(angulo) + "°",
            font=("Arial", 11, "bold"),
            fill="white"
        )

    canvas_radar.create_text(
        cx, 40,
        text="RADAR PARA DETECCIÓN DE OBJETOS",
        font=("Helvetica", 15, "bold"),
        fill="white"
    )


dibujar_fondo_radar()

linea_servo = canvas_radar.create_line(
    cx, cy, cx + radio_max, cy,
    fill="red", width=4
)


def actualizar_radar(angulo, distancia):
    global ultima_deteccion
    rad = math.radians(angulo)

    x_servo = cx + radio_max * math.cos(rad)
    y_servo = cy - radio_max * math.sin(rad)
    canvas_radar.coords(linea_servo, cx, cy, x_servo, y_servo)

    if 0 < distancia <= distancia_max:
        ultima_deteccion = time.time()

        r = distancia * radio_max / distancia_max
        x_obj = cx + r * math.cos(rad)
        y_obj = cy - r * math.sin(rad)

        nuevo_punto = canvas_radar.create_oval(
            x_obj - 5, y_obj - 5,
            x_obj + 5, y_obj + 5,
            fill="lime", outline="lime"
        )
        puntos_verdes.append(nuevo_punto)

        if len(puntos_verdes) > 5:
            punto_antiguo = puntos_verdes.pop(0)
            canvas_radar.delete(punto_antiguo)

    canvas_radar.tag_raise(linea_servo)


eje_x = []
temperaturas = []
humedades = []
eje_x_media = []
medias = []


def actualizar_grafica():
    actualizado_dht = False

    while not datos_grafica.empty():
        dato = datos_grafica.get()

        if dato[0] == "datos":
            eje_x.append(dato[1])
            temperaturas.append(dato[2])
            humedades.append(dato[3])
            actualizado_dht = True

        elif dato[0] == "media":
            eje_x_media.append(dato[1])
            medias.append(dato[2])
            actualizado_dht = True

        elif dato[0] == "radar":
            actualizar_radar(dato[1], dato[2])

    if actualizado_dht:
        if eje_x:
            linea_temperatura.set_data(eje_x, temperaturas)
            linea_humedad.set_data(eje_x, humedades)
            eje_unico.set_xlim(0, max(100, eje_x[-1] + 1))

        if eje_x_media:
            linea_media.set_data(eje_x_media, medias)

        eje_unico.relim()
        eje_unico.autoscale_view(scalex=False, scaley=True)
        canvas.draw_idle()

    # Esborrar punts si passen 9 segons (1 escombrat complet) sense deteccions
    if puntos_verdes and (time.time() - ultima_deteccion >= 9.0):
        for punto in puntos_verdes:
            canvas_radar.delete(punto)
        puntos_verdes.clear()

    window.after(50, actualizar_grafica)

actualizar_grafica()
window.mainloop()