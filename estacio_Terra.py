import threading
from tkinter import *

import serial
import matplotlib.pyplot as plt

device = 'COM7'
ser = serial.Serial(device, baudrate=9600)



def recepcion ():
    
    plt.ion()
    plt.axis([0,100,20,100])
    temperaturas = []
    humedades = []

    eje_x = []
    i = 0

    try: 
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                print (line)
                trozos = line.split (':')
                eje_x.append (i) 
                temperatura = float(trozos[1])
                temperaturas.append(temperatura)
                humedad = float(trozos[3])
                humedades.append(humedad)
                plt.plot(eje_x,temperaturas)
                plt.plot(eje_x,humedades)

                plt.title(str(i))
                i = i+1
                plt.draw()
                plt.pause(0.5)

    except KeyboardInterrupt:
        print ("Saliendo...")
    finally:
        ser.close()

def Iniciar():
    threadRecepcion = threading.Thread (target = recepcion)
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
window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=1)
window.columnconfigure(2, weight=1)


tituloLabel = Label(window, text = "DATOS SATÉLITE", font=("Comic Sans MS", 35))
tituloLabel.grid(row=0, column=0, columnspan=5, padx=5, pady=5, sticky=N + S + E + W)


iniciarButton = Button(window, text="INICIAR", bg='green', fg="white",font=("Comic Sans MS", 20), command=Iniciar)
iniciarButton.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)
pararButton = Button(window, text="PARAR", bg='red', fg="white", font=("Comic Sans MS", 20), command=Parar)
pararButton.grid(row=1, column=1, padx=5, pady=5, sticky=N + S + E + W)
reanudarButton = Button(window, text="REANUDAR", bg='blue', fg="white", font=("Comic Sans MS", 20), command = Reanudar)
reanudarButton.grid(row=1, column=2, padx=5, pady=5, sticky=N + S + E + W)


window.mainloop()