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
                print(line)

                trozos = line.split(':')

                if trozos[0] == "1" and len(trozos) >= 5:
                    temperatura = float(trozos[2])
                    humedad = float(trozos[4])

                    datos_grafica.put(
                        ("datos", i, temperatura, humedad)
                    )
                    i = i + 1

                elif trozos[0] == "4" and len(trozos) >= 3:
                    media = float(trozos[2])

                    datos_grafica.put(
                        ("media", i-1, media)
                    )

    except KeyboardInterrupt:
        print("Saliendo...")
    finally:
        ser.close()



def Iniciar():
    threadRecepcion = threading.Thread(target=recepcion)
    threadRecepcion.start()


def Parar():
    mensaje = "Parar\n"
    ser.write(mensaje.encode('utf-8'))


def Reanudar():
    mensaje = "Reanudar\n"
    ser.write(mensaje.encode('utf-8'))


def TerraCalcul():
    mensaje = "TerraCalcul\n"
    ser.write(mensaje.encode('utf-8'))


def SatelitCalcul():
    mensaje = "SatelitCalcul\n"
    ser.write(mensaje.encode('utf-8'))


# CAMBIO: función para validar y enviar el límite de temperatura
def EnviarLimite():
    try:
        limite = float(limiteTemperatura.get())

        if not math.isfinite(limite):
            estadoLimite.config(text="Introduce un número válido", fg="red")
            return

        mensaje = "LimiteTemperatura:" + str(limite) + "\n"
        ser.write(mensaje.encode('utf-8'))

        estadoLimite.config(
            text="Límite enviado: " + str(limite) + " °C",
            fg="green"
        )

    except ValueError:
        estadoLimite.config(
            text="Introduce una temperatura válida",
            fg="red"
        )


def EnviarFrecuencia():
    try:
        segons = float(frecuenciaDatos.get())

        # El sensor DHT11 no pot llegir més ràpid d'1 vegada per segon
        if not math.isfinite(segons) or segons < 1:
            estadoFrecuencia.config(text="Mínimo 1 segundo", fg="red")
            return

        milisegons = int(segons * 1000)
        mensaje = "Frecuencia:" + str(milisegons) + "\n"
        ser.write(mensaje.encode('utf-8'))

        estadoFrecuencia.config(
            text="Enviado: cada " + str(segons) + " s",
            fg="green"
        )

    except ValueError:
        estadoFrecuencia.config(
            text="Introduce un número válido",
            fg="red"
        )



window = Tk()
# CAMBIO: ampliamos la ventana para colocar los controles junto a la gráfica
window.geometry("900x650")

window.rowconfigure(0, weight=1)
window.rowconfigure(1, weight=1)
window.rowconfigure(2, weight=4)

window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=1)
window.columnconfigure(2, weight=1)


tituloLabel = Label(
    window,
    text="DATOS SATÉLITE",
    font=("Helvetica", 35)
)
tituloLabel.grid(
    row=0, column=0, columnspan=5,
    padx=5, pady=5, sticky=N + S + E + W
)


iniciarButton = Button(
    window, text="INICIAR", bg='green', fg="white",
    font=("Helvetica", 20), command=Iniciar
)
iniciarButton.grid(
    row=1, column=0, padx=5, pady=5,
    sticky=N + S + E + W
)

pararButton = Button(
    window, text="PARAR", bg='red', fg="white",
    font=("Helvetica", 20), command=Parar
)
pararButton.grid(
    row=1, column=1, padx=5, pady=5,
    sticky=N + S + E + W
)

reanudarButton = Button(
    window, text="REANUDAR", bg='blue', fg="white",
    font=("Helvetica", 20), command=Reanudar
)
reanudarButton.grid(
    row=1, column=2, padx=5, pady=5,
    sticky=N + S + E + W
)


# CAMBIO: la gráfica ocupa las dos primeras columnas para dejar
# espacio a los nuevos controles en la columna de la derecha.
panel_grafica = Frame(window)
panel_grafica.grid(
    row=2, column=0, columnspan=2,
    padx=5, pady=5, sticky=N + S + E + W
)


# CAMBIO: panel situado al lado de las gráficas
panel_controles = LabelFrame(
    window,
    text="CONTROL DE CÁLCULO",
    font=("Helvetica", 12)
)
panel_controles.grid(
    row=2, column=2,
    padx=5, pady=5,
    sticky=N + S + E + W
)


# CAMBIO: botón para seleccionar el cálculo de la estación terrestre
terraButton = Button(
    panel_controles,
    text="CÁLCULO ESTACIÓN TIERRA",
    bg='orange',
    fg="white",
    font=("Helvetica", 11),
    command=TerraCalcul
)
terraButton.pack(fill=X, padx=5, pady=10)


# CAMBIO: botón para seleccionar el cálculo del satélite
satelitButton = Button(
    panel_controles,
    text="CÁLCULO SATÉLITE",
    bg='purple',
    fg="white",
    font=("Helvetica", 11),
    command=SatelitCalcul
)
satelitButton.pack(fill=X, padx=5, pady=10)


# CAMBIO: apartado para introducir el límite de temperatura
limiteLabel = Label(
    panel_controles,
    text="Límite de temperatura (°C):",
    font=("Helvetica", 11)
)
limiteLabel.pack(padx=5, pady=10)


# CAMBIO: variable que guarda el límite escrito por el usuario
limiteTemperatura = StringVar()

limiteEntrada = Entry(
    panel_controles,
    textvariable=limiteTemperatura,
    font=("Helvetica", 14),
    justify=CENTER
)
limiteEntrada.pack(fill=X, padx=5, pady=5)


# CAMBIO: botón que envía el límite al Arduino terrestre
enviarLimiteButton = Button(
    panel_controles,
    text="ENVIAR LÍMITE",
    bg='blue',
    fg="white",
    font=("Helvetica", 11),
    command=EnviarLimite
)
enviarLimiteButton.pack(fill=X, padx=5, pady=10)


# CAMBIO: etiqueta para mostrar si el límite se ha enviado correctamente
estadoLimite = Label(
    panel_controles,
    text="",
    font=("Helvetica", 10)
)
estadoLimite.pack(padx=5, pady=5)

# Apartat per introduir la freqüència d'enviament
frecuenciaLabel = Label(
    panel_controles,
    text="Frecuencia de envío (s):",
    font=("Helvetica", 11)
)
frecuenciaLabel.pack(padx=5, pady=10)

frecuenciaDatos = StringVar()

frecuenciaEntrada = Entry(
    panel_controles,
    textvariable=frecuenciaDatos,
    font=("Helvetica", 14),
    justify=CENTER
)
frecuenciaEntrada.pack(fill=X, padx=5, pady=5)

enviarFrecuenciaButton = Button(
    panel_controles,
    text="ENVIAR FRECUENCIA",
    bg='teal',
    fg="white",
    font=("Helvetica", 11),
    command=EnviarFrecuencia
)
enviarFrecuenciaButton.pack(fill=X, padx=5, pady=10)

estadoFrecuencia = Label(
    panel_controles,
    text="",
    font=("Helvetica", 10)
)
estadoFrecuencia.pack(padx=5, pady=5)



figura = Figure(figsize=(6, 4), dpi=100)

# Un únic gràfic (1 fila, 1 columna, posició 1)
eje_unico = figura.add_subplot(111)

eje_unico.set_title("Temperatura, Humedad y Media")
eje_unico.set_xlabel("Tiempo (s)")
eje_unico.set_ylabel("Valor (°C / %)")
eje_unico.set_xlim(0, 100)
eje_unico.set_ylim(0, 100)
eje_unico.set_xticks(range(0, 101, 20))
eje_unico.set_yticks(range(0, 101, 20))
eje_unico.grid(True)

# Les tres línies dins del mateix eix amb etiquetes per a la llegenda
linea_temperatura, = eje_unico.plot([], [], color='blue', label='Temperatura (°C)')
linea_humedad, = eje_unico.plot([], [], color='green', label='Humedad (%)')
linea_media, = eje_unico.plot([], [], color='red', label='Media')

eje_unico.legend()

canvas = FigureCanvasTkAgg(figura, master=panel_grafica)
canvas.draw()
canvas.get_tk_widget().pack(fill=BOTH, expand=True)

eje_x = []
temperaturas = []
humedades = []
eje_x_media = []
medias = []


def actualizar_grafica():
    while not datos_grafica.empty():
        dato = datos_grafica.get()

        if dato[0] == "datos":
            tiempo = dato[1]
            temperatura = dato[2]
            humedad = dato[3]

            eje_x.append(tiempo)
            temperaturas.append(temperatura)
            humedades.append(humedad)

        if dato[0] == "media":
            tiempo = dato[1]
            media = dato[2]

            eje_x_media.append(tiempo)
            medias.append(media)

    if eje_x:
        linea_temperatura.set_data(eje_x, temperaturas)
        linea_humedad.set_data(eje_x, humedades)
        eje_unico.set_xlim(0, max(100, eje_x[-1] + 1))

    if eje_x_media:
        linea_media.set_data(eje_x_media, medias)

    if eje_x or eje_x_media:
        eje_unico.relim()
        eje_unico.autoscale_view(scalex=False, scaley=True)

    canvas.draw_idle()
    window.after(200, actualizar_grafica)


actualizar_grafica()

window.mainloop()
