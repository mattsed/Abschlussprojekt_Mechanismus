import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import json
import os
import csv
from point import Point
#from link import Link
from mechanism import Mechanism
from animation import run_animation  # Importieren Sie die ausgelagerte Animationsfunktion

# JSON-Datei für gespeicherte Mechanismen
MECHANISM_FILE = "mechanisms.json"
CSV_FILE = "coordinates.csv"

# ---------------------------------------------------------------------
# UI: Mechanismus-Steuerung
# ---------------------------------------------------------------------
st.title("Ebener Mechanismus-Simulator")

# Mechanismus Nameingabe
mechanism_name = st.text_input("Mechanismus Name", value="")

# Punkteingabe
cx = st.number_input("c.x", value=0.0)
cy = st.number_input("c.y", value=0.0)

p0x = st.number_input("p0.x", value=-15.0)
p0y = st.number_input("p0.y", value=10.0)

# Mechanismus erstellen
c = Point(cx, cy, "c")
p0 = Point(p0x, p0y, "p0")

# Session State aktualisieren
if "mechanism" not in st.session_state:
    st.session_state.mechanism = Mechanism(c, p0)

mechanism = st.session_state.mechanism

# Update c and p0 coordinates if changed
if st.button("Aktualisiere c und p0"):
    mechanism.c.move_to(cx, cy)
    mechanism.p0.move_to(p0x, p0y)
    # Update the length of the link between c and p0
    mechanism.links[0].length = np.linalg.norm(mechanism.p0.position() - mechanism.c.position())
    st.success("Koordinaten von c und p0 wurden aktualisiert!")

# Punkteingabe für neue Punkte
st.header("Punkte hinzufügen")
new_point_name = st.text_input("Neuer Punkt Name", value="p1", key="new_point_name")
new_point_x = st.number_input("Neuer Punkt x", value=0.0, key="new_point_x")
new_point_y = st.number_input("Neuer Punkt y", value=0.0, key="new_point_y")

if st.button("Punkt hinzufügen", key="add_point"):
    new_point = Point(new_point_x, new_point_y, new_point_name)
    mechanism.points.append(new_point)
    st.success(f"Punkt '{new_point_name}' hinzugefügt!")

# Punkte verlinken
st.header("Punkte verlinken")   
point_names = [p.name for p in [mechanism.c, mechanism.p0] + mechanism.points]
point1_name = st.selectbox("Erster Punkt", point_names, key="link_point1")
point2_name = st.selectbox("Zweiter Punkt", point_names, key="link_point2")

if st.button("Link hinzufügen", key="add_link"):
    point1 = next(p for p in [mechanism.c, mechanism.p0] + mechanism.points if p.name == point1_name)
    point2 = next(p for p in [mechanism.c, mechanism.p0] + mechanism.points if p.name == point2_name)
    mechanism.add_link(point1, point2)
    st.success(f"Link zwischen '{point1_name}' und '{point2_name}' hinzugefügt!")

# Slider für die Winkelgeschwindigkeit hinzufügen
st.header("Winkelgeschwindigkeit einstellen")
angular_velocity = st.slider("Winkelgeschwindigkeit (Grad pro Sekunde)", 1.0, 10.0, 1.0, step=0.1)

# Auswahl des Punktes für die Bahnkurve
st.header("Bahnkurve anzeigen")
selected_point_name = st.selectbox("Wähle einen Punkt für die Bahnkurve", point_names, key="selected_point")

# Start/Stop Button
if "running" not in st.session_state:
    st.session_state.running = False
if st.button("Animation starten / stoppen"):
    st.session_state.running = not st.session_state.running

# Liste zur Speicherung der Bahnkurve
if "trajectory" not in st.session_state:
    st.session_state.trajectory = []

# ---------------------------------------------------------------------
# JSON Speichern/Laden mit Namensverwaltung
# ---------------------------------------------------------------------

# Lade vorhandene Mechanismen
if os.path.exists(MECHANISM_FILE):
    with open(MECHANISM_FILE, "r", encoding="utf-8") as f:
        try:
            stored_mechanisms = json.load(f)
        except json.JSONDecodeError:
            stored_mechanisms = {}
else:
    stored_mechanisms = {}

# Speichern
if st.button("Speichere Mechanismus"):
    stored_mechanisms[mechanism_name] = mechanism.to_dict()
    with open(MECHANISM_FILE, "w", encoding="utf-8") as f:
        json.dump(stored_mechanisms, f, ensure_ascii=False, indent=2)
    st.success(f"Mechanismus '{mechanism_name}' gespeichert!")

# Auswahl gespeicherter Mechanismen
selected_mechanism = st.selectbox("Lade gespeicherten Mechanismus", [""] + list(stored_mechanisms.keys()))

if st.button("Lade Mechanismus") and selected_mechanism:
    data = stored_mechanisms[selected_mechanism]
    st.session_state.mechanism = Mechanism.from_dict(data)
    st.session_state.running = False
    st.session_state.trajectory = []
    st.success(f"Mechanismus '{selected_mechanism}' geladen!")

# ---------------------------------------------------------------------
# Punkte anzeigen und löschen
# ---------------------------------------------------------------------
st.header("Angelegte Punkte")
for point in [mechanism.c, mechanism.p0] + mechanism.points:
    cols = st.columns([3, 1, 1])
    cols[0].write(f"{point.name}: ({point.x}, {point.y})")
    if point.name not in ["c", "p0"]:
        fixed = cols[1].checkbox("Fixiert", value=point.fixed, key=f"fixed_{point.name}")
        if fixed != point.fixed:
            point.fixed = fixed
    if cols[2].button("Löschen", key=f"delete_{point.name}"):
        mechanism.remove_point(point.name)
        st.experimental_rerun()

# ---------------------------------------------------------------------
# Links anzeigen und löschen
# ---------------------------------------------------------------------
st.header("Angelegte Links")
for i, link in enumerate(mechanism.links):
    cols = st.columns([3, 1])
    cols[0].write(f"Link: {link.p1.name} - {link.p2.name}")
    if cols[1].button("Löschen", key=f"delete_link_{link.p1.name}_{link.p2.name}_{i}"):
        mechanism.remove_link(link.p1.name, link.p2.name)
        st.experimental_rerun()

# ---------------------------------------------------------------------
# Animation
# ---------------------------------------------------------------------
plot_placeholder = st.empty()
run_animation(plot_placeholder, mechanism, angular_velocity, selected_point_name)

# ---------------------------------------------------------------------
# Save coordinates to CSV
# ---------------------------------------------------------------------
if st.button("Speichere Koordinaten zu CSV"):
    mechanism.save_coordinates_to_csv(angular_velocity)
    st.success("Koordinaten wurden in die CSV-Datei gespeichert!")
