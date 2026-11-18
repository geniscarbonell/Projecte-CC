import tkinter as tk
import math
import serial

# Conexión con Arduino (verifica que COM7 sea tu puerto)
arduino = serial.Serial("COM7", 9600, timeout=0.1)

# Ventana
ventana = tk.Tk()
ventana.title("Radar de ultrasonidos")

# Canvas donde dibujaremos
canvas = tk.Canvas(ventana, width=600, height=370, bg="black")
canvas.pack()

# Configuración del radar
cx = 300            # Coordenada x del centro
cy = 310            # Coordenada y del centro
radio_max = 200     # Radio máximo en píxeles
distancia_max = 50  # Distancia de referencia para las etiquetas (50 cm)


def dibujar_fondo():
    # 1. Dibujar los semicírculos de distancia
    for distancia in range(10, 51, 10):
        radio = distancia * radio_max / distancia_max
        canvas.create_arc(
            cx - radio, cy - radio,
            cx + radio, cy + radio,
            start=0, extent=180,
            style=tk.ARC,
            outline="white",
            width=2
        )
        canvas.create_text(
            cx + radio, cy + 15,
            text=str(distancia),
            font=("Arial", 10, "bold"),
            fill="white"
        )

    # 2. Dibujar las líneas de los ángulos
    for angulo in range(0, 181, 30):
        rad = math.radians(angulo)
        x = cx + radio_max * math.cos(rad)
        y = cy - radio_max * math.sin(rad)
        canvas.create_line(cx, cy, x, y, fill="white")

        # Etiquetas de los ángulos
        xt = cx + (radio_max + 22) * math.cos(rad)
        yt = cy - (radio_max + 22) * math.sin(rad)
        canvas.create_text(
            xt, yt,
            text=str(angulo) + "°",
            font=("Arial", 12, "bold"),
            fill="white"
        )

    # 3. Título
    canvas.create_text(
        cx, 45,
        text="RADAR PARA DETECCIÓN DE OBJETOS",
        font=("Helvetica", 18, "bold"),
        fill="white"
    )


# Dibujamos el fondo estático primero
dibujar_fondo()

# Creamos la línea roja del servo en la posición inicial (0 grados)
linea_servo = canvas.create_line(
    cx, cy, cx + radio_max, cy,
    fill="red", width=4
)


def actualizar_linea(angulo):
    rad = math.radians(angulo)
    x = cx + radio_max * math.cos(rad)
    y = cy - radio_max * math.sin(rad)
    canvas.coords(linea_servo, cx, cy, x, y)


def actualizar():
    # Leemos todos los datos acumulados en el búfer para evitar retrasos
    while arduino.in_waiting > 0:
        linea = arduino.readline().decode(errors="ignore").strip()
        if linea:
            # Toma el primer número antes de ":" (o el número entero si solo envías el ángulo)
            trozos = linea.split(":")
            try:
                angulo = float(trozos[0])
                actualizar_linea(angulo)
            except ValueError:
                pass

    ventana.after(15, actualizar)


actualizar()
ventana.mainloop()