import os
from datetime import datetime
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

simulando_error = False
errores_descartados = 0

LOG_FILE = "registro_eventos.txt"


def registrar_evento(tipo, descripcion):
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"{fecha_hora} | {tipo} | {descripcion}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(linea)
    except Exception as e:
        print("Error guardando evento:", e)
    try:
        window.after(0, actualizar_vista_eventos)
    except Exception:
        pass


def guardar_observacion():
    texto = entry_obs.get().strip()
    if texto:
        registrar_evento("Observacion", texto)
        entry_obs.delete(0, END)


def actualizar_vista_eventos(*args):
    if "txt_eventos" not in globals():
        return
    filtro_t = filtro_tipo.get()
    filtro_f = filtro_fecha.get().strip().lower()

    txt_eventos.config(state="normal")
    txt_eventos.delete("1.0", END)

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for linea in f:
                partes = linea.strip().split(" | ", 2)
                if len(partes) == 3:
                    fecha_h, tipo, desc = partes
                    if filtro_t != "Todos" and tipo != filtro_t:
                        continue
                    if filtro_f and filtro_f not in fecha_h.lower():
                        continue
                    txt_eventos.insert(END, f"[{fecha_h}] ({tipo}) {desc}\n")

    txt_eventos.see(END)
    txt_eventos.config(state="disabled")


def recepcion():
    i = 0
    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').rstrip()
                if not line:
                    continue

                trozos = line.split(':')

                # Trama 1: Temperatura i Humitat -> format "1:T:25.00:H:50.00"
                if trozos[0] == "1" and len(trozos) >= 5:
                    print(line)
                    try:
                        temperatura = float(trozos[2])
                        humedad = float(trozos[4])
                        datos_grafica.put(("datos", i, temperatura, humedad))
                        i = i + 1
                    except ValueError:
                        pass

                # Trama 2: Radar Ultrasons -> format "2:angulo:distancia"
                elif trozos[0] == "2" and len(trozos) >= 3:
                    try:
                        angulo = float(trozos[1])
                        distancia = float(trozos[2])
                        datos_grafica.put(("radar", angulo, distancia))
                    except ValueError:
                        pass

                # Trama 4: Mitjana -> format "4:Media:24.50"
                elif trozos[0] == "4" and len(trozos) >= 3:
                    print(line)
                    try:
                        media = float(trozos[2])
                        datos_grafica.put(("media", max(0, i - 1), media))
                    except ValueError:
                        pass

                # Trama 5: Error de checksum detectat per l'Arduino -> "5:ErrorChecksum:<missatge corrupte>"
                elif trozos[0] == "5":
                    print(line)
                    datos_grafica.put(("error",))
                    registrar_evento("Alarma", f"Mensaje corrupto descartado ({line})")

                # Alarma de temperatura excesiva desde Arduino/Satélite
                elif line == "Límite temperatura":
                    print(line)
                    registrar_evento("Alarma", "Temperatura excesiva (Límite superado)")

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
    registrar_evento("Comando", "Parar envío de datos")


def Reanudar():
    ser.write("Reanudar\n".encode('utf-8'))
    registrar_evento("Comando", "Reanudar envío de datos")


def TerraCalcul():
    ser.write("TerraCalcul\n".encode('utf-8'))
    registrar_evento("Comando", "Cálculo de media en Estación de Tierra")


def SatelitCalcul():
    ser.write("SatelitCalcul\n".encode('utf-8'))
    registrar_evento("Comando", "Cálculo de media en Satélite")


def AlternarError():
    global simulando_error
    simulando_error = not simulando_error

    if simulando_error:
        ser.write("ErrorOn\n".encode('utf-8'))
        errorButton.config(text="SIMULAR ERRORES: ON", bg='red')
        registrar_evento("Comando", "Activar simulación de errores (ErrorOn)")
    else:
        ser.write("ErrorOff\n".encode('utf-8'))
        errorButton.config(text="SIMULAR ERRORES: OFF", bg='gray')
        registrar_evento("Comando", "Desactivar simulación de errores (ErrorOff)")


def EnviarLimite():
    try:
        limite = float(limiteTemperatura.get())
        if not math.isfinite(limite):
            estadoLimite.config(text="Introduce un número válido", fg="red")
            return

        mensaje = "LimiteTemperatura:" + str(limite) + "\n"
        ser.write(mensaje.encode('utf-8'))
        estadoLimite.config(text="Límite enviado: " + str(limite) + " °C", fg="green")
        registrar_evento("Comando", f"Nuevo límite de temperatura: {limite} °C")
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
        registrar_evento("Comando", f"Nueva frecuencia de envío: {segons} s")
    except ValueError:
        estadoFrecuencia.config(text="Introduce un número válido", fg="red")


def ActivarRastreo():
    ser.write("ModoRastreo\n".encode('utf-8'))
    estadoRadar.config(text="Modo: Rastreo continuo", fg="green")
    registrar_evento("Comando", "Sensor distancia en modo rastreo")


def EnviarAngulo():
    try:
        ang = float(anguloRadarVar.get())
        if not math.isfinite(ang) or ang < 0 or ang > 180:
            estadoRadar.config(text="Ángulo entre 0° y 180°", fg="red")
            return

        mensaje = "Angulo:" + str(ang) + "\n"
        ser.write(mensaje.encode('utf-8'))
        estadoRadar.config(text=f"Modo: Fijo en {ang}°", fg="blue")
        registrar_evento("Comando", f"Orientación fija del sensor a {ang}°")
    except ValueError:
        estadoRadar.config(text="Introduce un ángulo válido", fg="red")



# --- CONFIGURACIÓ FINESTRA PRINCIPAL ---
window = Tk()
window.title("Estación de Tierra - Satélite y Radar")
window.update_idletasks()
window.attributes("-fullscreen", True)
window.bind("<Escape>", lambda e: window.attributes("-fullscreen", False))
window.bind("<F11>", lambda e: window.attributes("-fullscreen", not window.attributes("-fullscreen")))

window.rowconfigure(0, weight=1)
window.rowconfigure(1, weight=1)
window.rowconfigure(2, weight=4)
window.rowconfigure(3, weight=2)

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
reanudarButton.grid(row=1, column=2, padx=5, pady=5, sticky=N + S + E + W)

# Prova del checksum: botó per simular errors al satèl·lit + comptador de missatges descartats
panel_test = Frame(window)
panel_test.grid(row=1, column=3, padx=5, pady=5, sticky=N + S + E + W)

errorButton = Button(panel_test, text="SIMULAR ERRORES: OFF", bg='gray', fg="white", font=("Helvetica", 14), command=AlternarError)
errorButton.pack(fill=BOTH, expand=True)

erroresLabel = Label(panel_test, text="Mensajes descartados: 0", font=("Helvetica", 12))
erroresLabel.pack(fill=X)


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
panel_controles = LabelFrame(window, text="CONTROL DE CÁLCULO Y SENSORES", font=("Helvetica", 12))
panel_controles.grid(row=2, column=2, padx=5, pady=5, sticky=N + S + E + W)

terraButton = Button(panel_controles, text="CÁLCULO ESTACIÓN TIERRA", bg='orange', fg="white", font=("Helvetica", 11), command=TerraCalcul)
terraButton.pack(fill=X, padx=5, pady=5)

satelitButton = Button(panel_controles, text="CÁLCULO SATÉLITE", bg='purple', fg="white", font=("Helvetica", 11), command=SatelitCalcul)
satelitButton.pack(fill=X, padx=5, pady=5)

limiteLabel = Label(panel_controles, text="Límite de temperatura (°C):", font=("Helvetica", 10))
limiteLabel.pack(padx=5, pady=(6, 2))

limiteTemperatura = StringVar()
limiteEntrada = Entry(panel_controles, textvariable=limiteTemperatura, font=("Helvetica", 12), justify=CENTER)
limiteEntrada.pack(fill=X, padx=5, pady=2)

enviarLimiteButton = Button(panel_controles, text="ENVIAR LÍMITE", bg='blue', fg="white", font=("Helvetica", 10), command=EnviarLimite)
enviarLimiteButton.pack(fill=X, padx=5, pady=4)

estadoLimite = Label(panel_controles, text="", font=("Helvetica", 9))
estadoLimite.pack(padx=5)

frecuenciaLabel = Label(panel_controles, text="Frecuencia de envío (s):", font=("Helvetica", 10))
frecuenciaLabel.pack(padx=5, pady=(6, 2))

frecuenciaDatos = StringVar()
frecuenciaEntrada = Entry(panel_controles, textvariable=frecuenciaDatos, font=("Helvetica", 12), justify=CENTER)
frecuenciaEntrada.pack(fill=X, padx=5, pady=2)

enviarFrecuenciaButton = Button(panel_controles, text="ENVIAR FRECUENCIA", bg='teal', fg="white", font=("Helvetica", 10), command=EnviarFrecuencia)
enviarFrecuenciaButton.pack(fill=X, padx=5, pady=4)

estadoFrecuencia = Label(panel_controles, text="", font=("Helvetica", 9))
estadoFrecuencia.pack(padx=5)

# Controles de orientación del sensor de distancia (Radar)
rastreoButton = Button(panel_controles, text="MODO RASTREO (BARRIDO)", bg='#2e7d32', fg="white", font=("Helvetica", 10), command=ActivarRastreo)
rastreoButton.pack(fill=X, padx=5, pady=(8, 3))

frame_angulo = Frame(panel_controles)
frame_angulo.pack(fill=X, padx=5, pady=2)

Label(frame_angulo, text="Ángulo (0-180°):", font=("Helvetica", 10)).pack(side=LEFT)
anguloRadarVar = StringVar()
Entry(frame_angulo, textvariable=anguloRadarVar, font=("Helvetica", 11), width=6, justify=CENTER).pack(side=LEFT, padx=4)
Button(frame_angulo, text="FIJAR", bg='#1565c0', fg="white", font=("Helvetica", 10), command=EnviarAngulo).pack(side=LEFT, fill=X, expand=True)

estadoRadar = Label(panel_controles, text="Modo: Rastreo continuo", fg="green", font=("Helvetica", 9))
estadoRadar.pack(padx=5, pady=2)



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


# --- 4. PANELL INFERIOR: REGISTRE D'EVENTS (APARTAT 6.4) ---
panel_eventos = LabelFrame(window, text="REGISTRO DE EVENTOS", font=("Helvetica", 12))
panel_eventos.grid(row=3, column=0, columnspan=4, padx=5, pady=5, sticky=N + S + E + W)

frame_obs = Frame(panel_eventos)
frame_obs.pack(fill=X, padx=5, pady=3)

Label(frame_obs, text="Observación usuario:", font=("Helvetica", 10, "bold")).pack(side=LEFT)
entry_obs = Entry(frame_obs, font=("Helvetica", 10))
entry_obs.pack(side=LEFT, fill=X, expand=True, padx=5)
entry_obs.bind("<Return>", lambda e: guardar_observacion())
Button(frame_obs, text="Guardar observación", bg="#2e7d32", fg="white", font=("Helvetica", 10), command=guardar_observacion).pack(side=LEFT)

frame_filtros = Frame(panel_eventos)
frame_filtros.pack(fill=X, padx=5, pady=3)

Label(frame_filtros, text="Filtrar por tipo:", font=("Helvetica", 10)).pack(side=LEFT)
filtro_tipo = StringVar(value="Todos")
menu_tipo = OptionMenu(frame_filtros, filtro_tipo, "Todos", "Comando", "Alarma", "Observacion", command=actualizar_vista_eventos)
menu_tipo.pack(side=LEFT, padx=5)

Label(frame_filtros, text="Filtrar por día/hora (ej. 2026-11-24 o 10:53):", font=("Helvetica", 10)).pack(side=LEFT, padx=(15, 5))
filtro_fecha = StringVar()
filtro_fecha.trace_add("write", actualizar_vista_eventos)
Entry(frame_filtros, textvariable=filtro_fecha, font=("Helvetica", 10), width=22).pack(side=LEFT)

frame_lista_ev = Frame(panel_eventos)
frame_lista_ev.pack(fill=BOTH, expand=True, padx=5, pady=3)

scroll_ev = Scrollbar(frame_lista_ev)
scroll_ev.pack(side=RIGHT, fill=Y)

txt_eventos = Text(frame_lista_ev, height=6, font=("Consolas", 10), state="disabled", yscrollcommand=scroll_ev.set)
txt_eventos.pack(side=LEFT, fill=BOTH, expand=True)
scroll_ev.config(command=txt_eventos.yview)

actualizar_vista_eventos()


eje_x = []
temperaturas = []
humedades = []
eje_x_media = []
medias = []


def actualizar_grafica():
    global errores_descartados
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

        elif dato[0] == "error":
            errores_descartados += 1
            erroresLabel.config(text="Mensajes descartados: " + str(errores_descartados))

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