#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 20 13:50:15 2025
@author: mmoreira
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lecture des données RGB depuis le port série
avec interface Tkinter pour choisir le colorant
"""

import serial
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# ==============================
# CONFIGURATION PORT SÉRIE
# ==============================
PORT = "COM7"   
BAUDRATE = 9600

# ==============================
# VARIABLE GLOBALE COULEUR
# ==============================
colorant = None

# ==============================
# FONCTIONS TKINTER
# ==============================
def set_color(c):
    global colorant
    colorant = c
    label_color.config(text=f"Couleur sélectionnée : {c}")

def start_measurement():
    if colorant is None:
        messagebox.showwarning("Attention", "Veuillez choisir une couleur")
        return
    root.destroy()

# ==============================
# INTERFACE TKINTER
# ==============================
root = tk.Tk()
root.title("TP Spectrophotométrie")

root.configure(bg="lightblue")

tk.Label(root, 
    text="Choisissez la couleur du colorant", 
    font=("Arial", 12, "bold")
).pack(pady=10)

frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=5)

tk.Button(frame_buttons, text="Vert", width=10,
command=lambda: set_color("vert")).grid(row=0, column=0, padx=5)

tk.Button(frame_buttons, text="Jaune", width=10,
command=lambda: set_color("jaune")).grid(row=0, column=1, padx=5)

tk.Button(frame_buttons, text="Bleu", width=10,
command=lambda: set_color("bleu")).grid(row=0, column=2, padx=5)

tk.Button(frame_buttons, text="Rouge", width=10,
command=lambda: set_color("rouge")).grid(row=0, column=3, padx=5)

tk.Button(frame_buttons, text="Blanc", width=10,
command=lambda: set_color("blanc")).grid(row=0, column=4, padx=5)

label_color = tk.Label(root, text="Couleur sélectionnée : aucune")
label_color.pack(pady=10)

tk.Button(
    root,
    text="START",
    width=15,
    command=start_measurement
).pack(pady=15)

root.mainloop()

# ==============================
# LECTURE DES DONNÉES SÉRIE
# ==============================
ser = serial.Serial(PORT, BAUDRATE, timeout=1)
time.sleep(2)

data = []
print("Lecture des données en cours...")

try:
    while True:
        line = ser.readline().decode('utf-8').strip()
        if line:
            cycle, r, g, b, sensor = line.split(',')
            cycle = int(cycle)
            r = int(r)
            g = int(g)
            b = int(b)
            sensor = int(sensor)

        if cycle > 0:
            print("Arrêt de la lecture.")
            break

        data.append([cycle, r, g, b, sensor])
        print(f"Cycle={cycle} | R={r} G={g} B={b} | Mesure={sensor}")

except KeyboardInterrupt:
    print("Lecture interrompue")

ser.close()

# ==============================
# DATAFRAME + SAUVEGARDE
# ==============================
df = pd.DataFrame(
    data,
    columns=['cycle', 'R', 'G', 'B', 'SensorValue']
)

date_str = datetime.now().strftime("%Y%m%d_%H%M%S")

filename = f"rgb_sensor_data_{colorant}_{date_str}.csv"
df.to_csv(filename, index=False)

print(f"Données sauvegardées dans {filename}")

# ==============================
# PRÉPARATION COULEURS LED
# ==============================
rgb_colors = df[['R', 'G', 'B']].values / 255.0
color_bar = rgb_colors.reshape(1, rgb_colors.shape[0], 3)

# ==============================
# FIGURE
# ==============================
fig, (ax1, ax2) = plt.subplots(
    2, 1,
    figsize=(10, 5),
    gridspec_kw={'height_ratios': [4, 0.6]},
    sharex=True
)

ax1.scatter(
    df.index,
    df['SensorValue'],
    c=rgb_colors,
    s=18
)

ax1.set_ylabel("Intensité")
ax1.set_title(f"Spectre mesuré – colorant {colorant}")
ax1.grid(True)
ax1.set_ylim(0, df['SensorValue'].max() * 1.1)

ax2.imshow(color_bar, aspect='auto')
ax2.set_yticks([])
ax2.set_xlabel("Indice de balayage couleur (LED RGB)")

plt.tight_layout()
plt.show()