import re
import sys

import matplotlib
import numpy as np

# Backend interactivo (igual que en la versión 2D)
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt  # noqa: E402
from mpl_toolkits.mplot3d import Axes3D  # noqa: E402,F401  (registra la proyección 3d)
import serial  # noqa: E402

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
PUERTO = 'COM5'
BAUDIOS = 9600
R_EARTH = 6371000  # Radio de la Tierra en metros

# Misma expresión regular que en orbita2d.py
regex = re.compile(r"Position: \(X: ([\d\.-]+) m, Y: ([\d\.-]+) m, Z: ([\d\.-]+) m\)")

# ---------------------------------------------------------------------------
# Datos
# ---------------------------------------------------------------------------
x_vals, y_vals, z_vals = [], [], []

# ---------------------------------------------------------------------------
# Figura 3D
# ---------------------------------------------------------------------------
plt.ion()
plt.rcParams['grid.color'] = '#555555'  # rejilla tenue sobre fondo negro
fig = plt.figure(figsize=(8, 8), facecolor='black')
ax = fig.add_subplot(111, projection='3d', facecolor='black')

# Estilo "espacio": fondo negro con ejes, marcas y etiquetas en blanco
for eje in (ax.xaxis, ax.yaxis, ax.zaxis):
    eje.set_pane_color((0, 0, 0, 1))
    eje.pane.set_edgecolor('#888888')
    eje.line.set_color('white')
    eje.label.set_color('white')
ax.tick_params(colors='white')

# Tierra: esfera en alambre
u = np.linspace(0, 2 * np.pi, 36)
v = np.linspace(0, np.pi, 18)
xe = R_EARTH * np.outer(np.cos(u), np.sin(v))
ye = R_EARTH * np.outer(np.sin(u), np.sin(v))
ze = R_EARTH * np.outer(np.ones_like(u), np.cos(v))
ax.plot_wireframe(xe, ye, ze, color='deepskyblue', alpha=0.35, linewidth=0.5)

# Ecuador de la Tierra resaltado
theta = np.linspace(0, 2 * np.pi, 200)
ax.plot(R_EARTH * np.cos(theta), R_EARTH * np.sin(theta), np.zeros_like(theta),
        color='orange', linewidth=1.2, label='Ecuador')

# Órbita y último punto
orbit_plot, = ax.plot([], [], [], '-', color='deepskyblue', linewidth=1,
                      marker='o', markersize=2,
                      label='Órbita del satélite')
last_point_plot, = ax.plot([], [], [], 'ro', markersize=7, label='Último punto')

# Límites iniciales (cubo simétrico)
lim = 7e6
ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)
ax.set_zlim(-lim, lim)
ax.set_box_aspect((1, 1, 1))  # ejes con la misma escala

ax.set_xlabel('X (metros)')
ax.set_ylabel('Y (metros)')
ax.set_zlabel('Z (metros)')
ax.set_title('Órbita del satélite en 3D', color='white')
ax.legend(loc='upper right', facecolor='black', edgecolor='#888888',
          labelcolor='white')

# ---------------------------------------------------------------------------
# Cierre de ventana
# ---------------------------------------------------------------------------
window_closed = False


def on_close(event):
    global window_closed
    print("Ventana cerrada")
    window_closed = True


fig.canvas.mpl_connect('close_event', on_close)

# ---------------------------------------------------------------------------
# Puerto serie
# ---------------------------------------------------------------------------
ser = serial.Serial(PUERTO, BAUDIOS, timeout=1)

# ---------------------------------------------------------------------------
# Bucle principal
# ---------------------------------------------------------------------------
try:
    while not window_closed:
        if ser.in_waiting <= 0:
            plt.pause(0.01)  # mantiene la ventana viva y rotable sin saturar la CPU
            continue

        line = ser.readline().decode('utf-8', errors='ignore').rstrip()

        match = regex.search(line)
        if not match:
            continue

        x = float(match.group(1))
        y = float(match.group(2))
        z = float(match.group(3))
        print(f"X: {x}, Y: {y}, Z: {z}")

        x_vals.append(x)
        y_vals.append(y)
        z_vals.append(z)

        # Actualizar órbita y último punto
        orbit_plot.set_data_3d(x_vals, y_vals, z_vals)
        last_point_plot.set_data_3d([x], [y], [z])

        # Ampliar los límites (cubo) si el satélite se sale
        max_abs = max(abs(x), abs(y), abs(z))
        if max_abs > lim:
            lim = max_abs * 1.1
            ax.set_xlim(-lim, lim)
            ax.set_ylim(-lim, lim)
            ax.set_zlim(-lim, lim)
            print(f"Límites actualizados: ±{lim:.3e} m")

        fig.canvas.draw_idle()
        plt.pause(0.001)  # procesa eventos (permite girar la vista con el ratón)
finally:
    ser.close()

# Mostrar la gráfica final cuando termine
if not window_closed:
    plt.ioff()
    plt.show()