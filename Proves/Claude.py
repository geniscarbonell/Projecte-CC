import tkinter as tk
import serial
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

PUERTO = 'COM7'
VENTANA = 100          # nº de muestras visibles
PERIODO_MS = 100       # cada cuánto se consulta el puerto

ser = serial.Serial(PUERTO, baudrate=9600, timeout=0.1)

eje_x, temperaturas, humedades = [], [], []
i = 0
corriendo = False


def leer():
    global i
    if corriendo:
        actualizado = False
        while ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').rstrip()
            trozos = line.split(':')
            try:
                t = float(trozos[1])
                h = float(trozos[3])
            except (IndexError, ValueError):
                continue  # línea incompleta o con otro formato
            print(line)
            eje_x.append(i)
            temperaturas.append(t)
            humedades.append(h)
            i += 1
            actualizado = True

        if actualizado:
            linea_t.set_data(eje_x, temperaturas)
            linea_h.set_data(eje_x, humedades)
            ax.set_xlim(max(0, i - VENTANA), max(VENTANA, i))
            ax.set_title(f"Muestra {i}")
            canvas.draw_idle()

    window.after(PERIODO_MS, leer)


def Iniciar():
    global corriendo
    ser.reset_input_buffer()
    corriendo = True


def Parar():
    global corriendo
    corriendo = False


def Reanudar():
    global corriendo
    ser.reset_input_buffer()   # descarta lo acumulado durante la pausa
    corriendo = True


def cerrar():
    global corriendo
    corriendo = False
    ser.close()
    window.destroy()


window = tk.Tk()
window.geometry("700x750")
window.rowconfigure(0, weight=0)
window.rowconfigure(1, weight=0)
window.rowconfigure(2, weight=1)
for c in range(3):
    window.columnconfigure(c, weight=1)

tk.Label(window, text="DATOS SATÉLITE", font=("Comic Sans MS", 30)).grid(
    row=0, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

tk.Button(window, text="INICIAR", bg='green', fg="white",
          font=("Comic Sans MS", 16), command=Iniciar).grid(
    row=1, column=0, padx=5, pady=5, sticky="nsew")
tk.Button(window, text="PARAR", bg='red', fg="white",
          font=("Comic Sans MS", 16), command=Parar).grid(
    row=1, column=1, padx=5, pady=5, sticky="nsew")
tk.Button(window, text="REANUDAR", bg='blue', fg="white",
          font=("Comic Sans MS", 16), command=Reanudar).grid(
    row=1, column=2, padx=5, pady=5, sticky="nsew")

# Gráfica incrustada
fig = Figure(figsize=(6, 4))
ax = fig.add_subplot(111)
ax.set_ylim(20, 100)
ax.set_xlim(0, VENTANA)
linea_t, = ax.plot([], [], label="Temperatura")
linea_h, = ax.plot([], [], label="Humedad")
ax.legend(loc="upper right")

canvas = FigureCanvasTkAgg(fig, master=window)
canvas.get_tk_widget().grid(row=2, column=0, columnspan=3, sticky="nsew")

window.protocol("WM_DELETE_WINDOW", cerrar)
window.after(PERIODO_MS, leer)
window.mainloop()