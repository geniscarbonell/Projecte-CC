import threading
import time
import math
from tkinter import *
import queue

import serial
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



device = 'COM4'
ser = serial.Serial(device, baudrate=9600)

datos_grafica = queue.Queue()


def recepcion():



    temperaturas = []
    humedades = []

    eje_x = []
    i = 0

    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                print(line)
                trozos = line.split(':')
                eje_x.append(i)
                temperatura = float(trozos[1])
                temperaturas.append(temperatura)
                humedad = float(trozos[3])
                humedades.append(humedad)

                datos_grafica.put(
                    (eje_x[-1], temperatura, humedad)
                )

                i = i + 1

    except KeyboardInterrupt:
        print("Saliendo...")
    finally:
        ser.close()


def Iniciar():
    threadRecepcion = threading.Thread(target=recepcion)
    threadRecepcion.start()


def Parar():
    mensaje = "Parar"
    ser.write(mensaje.encode('utf-8'))


def Reanudar():
    mensaje = "Reanudar"
    ser.write(mensaje.encode('utf-8'))


window = Tk()
window.geometry("600x600")
window.rowconfigure(0, weight=1)
window.rowconfigure(1, weight=1)
window.rowconfigure(2, weight=4)
window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=1)
window.columnconfigure(2, weight=1)


tituloLabel = Label(
    window,
    text="DATOS SATÉLITE",
    font=("Comic Sans MS", 35)
)
tituloLabel.grid(
    row=0, column=0, columnspan=5,
    padx=5, pady=5, sticky=N + S + E + W
)


iniciarButton = Button(
    window, text="INICIAR", bg='green', fg="white",
    font=("Comic Sans MS", 20), command=Iniciar
)
iniciarButton.grid(
    row=1, column=0, padx=5, pady=5,
    sticky=N + S + E + W
)

pararButton = Button(
    window, text="PARAR", bg='red', fg="white",
    font=("Comic Sans MS", 20), command=Parar
)
pararButton.grid(
    row=1, column=1, padx=5, pady=5,
    sticky=N + S + E + W
)

reanudarButton = Button(
    window, text="REANUDAR", bg='blue', fg="white",
    font=("Comic Sans MS", 20), command=Reanudar
)
reanudarButton.grid(
    row=1, column=2, padx=5, pady=5,
    sticky=N + S + E + W
)


panel_grafica = Frame(window)
panel_grafica.grid(
    row=2, column=0, columnspan=3,
    padx=5, pady=5, sticky=N + S + E + W
)

figura = Figure(figsize=(6, 4), dpi=100)

eje_temperatura = figura.add_subplot(211)
eje_humedad = figura.add_subplot(212)

figura.subplots_adjust(hspace=0.65)

eje_temperatura.set_title("Temperatura")
eje_temperatura.set_ylabel("Temperatura (°C)")
eje_temperatura.set_xlim(0, 100)
eje_temperatura.set_ylim(20, 100)
eje_temperatura.set_xticks(range(0, 101, 20))
eje_temperatura.set_yticks(range(20, 101, 20))
eje_temperatura.grid(True)

eje_humedad.set_title("Humedad")
eje_humedad.set_xlabel("Tiempo (s)")
eje_humedad.set_ylabel("Humedad (%)")
eje_humedad.set_xlim(0, 100)
eje_humedad.set_ylim(0, 100)
eje_humedad.set_xticks(range(0, 101, 20))
eje_humedad.set_yticks(range(0, 101, 20))
eje_humedad.grid(True)

linea_temperatura, = eje_temperatura.plot([], [])
linea_humedad, = eje_humedad.plot([], [])

canvas = FigureCanvasTkAgg(figura, master=panel_grafica)
canvas.draw()
canvas.get_tk_widget().pack(fill=BOTH, expand=True)

eje_x = []
temperaturas = []
humedades = []



def actualizar_grafica():

    while not datos_grafica.empty():
        tiempo, temperatura, humedad = datos_grafica.get()

        eje_x.append(tiempo)
        temperaturas.append(temperatura)
        humedades.append(humedad)

    if eje_x:
        linea_temperatura.set_data(eje_x, temperaturas)
        linea_humedad.set_data(eje_x, humedades)

        eje_temperatura.set_xlim(0, max(100, eje_x[-1] + 1))
        eje_humedad.set_xlim(0, max(100, eje_x[-1] + 1))

        eje_temperatura.relim()
        eje_temperatura.autoscale_view(scalex=False, scaley=True)

        eje_humedad.relim()
        eje_humedad.autoscale_view(scalex=False, scaley=True)

        canvas.draw_idle()

    window.after(200, actualizar_grafica)



actualizar_grafica()

window.mainloop()
