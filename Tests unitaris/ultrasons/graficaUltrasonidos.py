
import tkinter as tk
import math

# Ventana
ventana = tk.Tk()
ventana.title("Radar de ultrasonidos")

# Canvas donde dibujaremos, creamos un lienzo, "ventana" indica que dibujaremos dentro de la ventana
canvas = tk.Canvas(ventana, width=600, height=370, bg="black") 
canvas.pack()

# Configuración del radar
cx = 300 #Coordenada x del centro
cy = 310 #Cordenada y del centro
radio_max = 200 #El radio máximo en los píxeles de la pantalla
distancia_max = 50 #El radio al que expresará un objeto a max distancia, QUE ESTABLECEREMOS COMO 50cm


def dibujar_radar(medidas, actual): #medidas: todas las mediciones que queremos representar

    canvas.delete("all") #Se borra todo para que no se acumulen los dibujos anteriores

    # 1. Dibujar los semicírculos de distancia
    for distancia in range(10, 51, 10): #esto va de 10 < 50 de 10 en 10 (10,20,30,40,50)

        radio = distancia * radio_max / distancia_max #resultado en píxeles

        canvas.create_arc( #funcion que permite crear arcos
            cx-radio, cy-radio, #limite izquierdo y limite superior
            cx+radio, cy+radio, #limite derecho y limite inferior
            start=0, extent=180, #Comienza en el angulo 0 hasta el 180
            style=tk.ARC, #Controno del arco
            outline="white", #la línea de color gris
            width = 5
        )

        canvas.create_text(
            cx + radio, cy + 15, #+15 porque en tkinter el eje y crece en negativo
            text=str(distancia), #distancia en texto
            font=("Arial", 10, "bold"),
            fill =("White")
        )

    # 2. Dibujar las líneas de los ángulos
    for angulo in range(0, 181, 30): #Del 0 al 180 yendo de 30 en 30

        rad = math.radians(angulo)

        x = cx + radio_max * math.cos(rad)
        y = cy - radio_max * math.sin(rad)

        canvas.create_line(cx, cy, x, y, fill="white",) #dibuja la linea desde el centro a donde toca

        # Etiquetas de los ángulos
        xt = cx + (radio_max + 22) * math.cos(rad)
        yt = cy - (radio_max + 22) * math.sin(rad)

        canvas.create_text(
            xt, yt,
            text=str(angulo) + "°", #Simplemente crear el texto con los angulos
            font=("Arial", 12, "bold"),
            fill = ("White")
        )

    # 3. Dibujar la línea amarilla de mediciones
    puntos = [] #Creamos una lista vacía

    for angulo, distancia in medidas:

        rad = math.radians(angulo)
        r = distancia * radio_max / distancia_max

        x = cx + r * math.cos(rad) 
        y = cy - r * math.sin(rad) 

        puntos.extend([x, y]) #mete los valores en puntos, añade elementos a la lista vamos

    if len(puntos) >= 4:
        canvas.create_line(
            *puntos,
            fill="gold",
            width=2
        ) #Se crean las lineas conectando los puntos de donde se detecta el objeto

    # 4. Dibujar la última medición en verde
    angulo, distancia = actual

    rad = math.radians(angulo)
    r = distancia * radio_max / distancia_max

    x = cx + r * math.cos(rad)
    y = cy - r * math.sin(rad)

    canvas.create_line(
        cx, cy, x, y,
        fill="red",
        width=4
    )

    canvas.create_oval(
        x-4, y-4, x+4, y+4,
        fill="blue",
        width = 50,
        outline= ''
    ) #creamos un óvalo pequeñito en el extremo de la linea

    # Título
    canvas.create_text(
        cx, 45,
        text="RADAR PARA DETECCIÓN DE OBJETOS",
        font=("Helvetica", 20),
        fill=("White")
    )


# Mediciones de prueba: (ángulo, distancia)
medidas = [
    (100, 49),
    (90, 35),
    (65, 32),
    (50, 40),
    (50, 25)
]

# Última medición
actual = (100, 49)

dibujar_radar(medidas, actual)

ventana.mainloop()
