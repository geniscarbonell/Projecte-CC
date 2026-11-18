import tkinter as tk
import math
import serial
import time

# Conexión con Arduino (asegúrate de cerrar el Monitor Serie de Arduino antes de ejecutar esto)
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
distancia_max = 50  # Distancia máxima en cm

# Variables para los puntos verdes y el temporizador
puntos_verdes = []
ultima_deteccion = time.time()


def dibujar_fondo():
    # 1. Semicírculos de distancia
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

    # 2. Líneas de los ángulos
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


# Dibujamos el fondo estático una sola vez
dibujar_fondo()

# Creamos la línea roja del servo en la posición inicial (0 grados)
linea_servo = canvas.create_line(
    cx, cy, cx + radio_max, cy,
    fill="red", width=4
)


def actualizar_radar(angulo, distancia):
    global ultima_deteccion
    rad = math.radians(angulo)

    # 1. Mover la línea roja del servo
    x_servo = cx + radio_max * math.cos(rad)
    y_servo = cy - radio_max * math.sin(rad)
    canvas.coords(linea_servo, cx, cy, x_servo, y_servo)

    # 2. Si detecta un objeto dentro de 50 cm, dibujar punto verde y reiniciar temporizador
    if 0 < distancia <= distancia_max:
        ultima_deteccion = time.time()

        r = distancia * radio_max / distancia_max
        x_obj = cx + r * math.cos(rad)
        y_obj = cy - r * math.sin(rad)

        nuevo_punto = canvas.create_oval(
            x_obj - 5, y_obj - 5,
            x_obj + 5, y_obj + 5,
            fill="lime", outline="lime"
        )
        puntos_verdes.append(nuevo_punto)

        # Mantener máximo 5 puntos: al entrar el 6º se borra el 1º
        if len(puntos_verdes) > 5:
            punto_antiguo = puntos_verdes.pop(0)
            canvas.delete(punto_antiguo)

    # Mantener la línea roja siempre por encima de los puntos
    canvas.tag_raise(linea_servo)


def actualizar():
    while arduino.in_waiting > 0:
        linea = arduino.readline().decode(errors="ignore").strip()
        if linea:
            trozos = linea.split(":")
            if len(trozos) == 2:
                try:
                    angulo = float(trozos[0])
                    distancia = float(trozos[1])
                    actualizar_radar(angulo, distancia)
                except ValueError:
                    pass

    # Comprobar si han pasado 5 segundos desde la última detección
    if puntos_verdes and (time.time() - ultima_deteccion >= 5.0):
        for punto in puntos_verdes:
            canvas.delete(punto)
        puntos_verdes.clear()

    ventana.after(15, actualizar)


actualizar()
ventana.mainloop()