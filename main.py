import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import json
import os
import csv
from point import Point
from mechanism import Mechanism
from animation import run_animation  # Importieren Sie die ausgelagerte Animationsfunktion

# JSON-Datei für gespeicherte Mechanismen
MECHANISM_FILE = "mechanisms.json"
CSV_FILE = "coordinates.csv"

# ---------------------------------------------------------------------
# UI: Mechanismus-Steuerung
# ---------------------------------------------------------------------
st.title("Ebener Mechanismus-Simulator")
st.sidebar.subheader("Mechanismus einstellen")
# Lade vorhandene Mechanismen
if os.path.exists(MECHANISM_FILE):
    with open(MECHANISM_FILE, "r", encoding="utf-8") as f:
        try:
            stored_mechanisms = json.load(f)
        except json.JSONDecodeError:
            stored_mechanisms = {}
else:
    stored_mechanisms = {}

# Auswahl gespeicherter Mechanismen
selected_mechanism = st.sidebar.selectbox("Lade gespeicherten Mechanismus", [""] + list(stored_mechanisms.keys()))

if st.sidebar.button("Lade Mechanismus") and selected_mechanism:
    data = stored_mechanisms[selected_mechanism]
    st.session_state.mechanism = Mechanism.from_dict(data)
    st.session_state.running = False
    st.session_state.trajectory = []
    st.session_state.initial_mechanism = Mechanism.from_dict(data)  # Speichere die initiale Mechanismus-Position
    st.sidebar.success(f"Mechanismus '{selected_mechanism}' geladen!")

# Button zum Löschen des Mechanismus
if st.sidebar.button("Lösche Mechanismus"):
    st.session_state.mechanism = Mechanism(Point(0, 0, "c"), Point(-15, 10, "p0"))
    st.session_state.trajectory = []
    st.sidebar.success("Mechanismus gelöscht!")

# Mechanismus Nameingabe
mechanism_name = st.sidebar.text_input("Mechanismus Name", value="")

# Punkteingabe
with st.sidebar.expander(f"C:"):
    cx = st.number_input("c.x", value=0.0)
    cy = st.number_input("c.y", value=0.0)

with st.sidebar.expander(f"P0:"):
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
if st.sidebar.button("Aktualisiere c und p0"):
    mechanism.c.move_to(cx, cy)
    mechanism.p0.move_to(p0x, p0y)
    # Update the length of the link between c and p0
    mechanism.links[0].length = np.linalg.norm(mechanism.p0.position() - mechanism.c.position())
    st.sidebar.success("Koordinaten von c und p0 wurden aktualisiert!")

# Punkteingabe für neue Punkte
st.sidebar.header("Punkte hinzufügen")
with st.sidebar.expander(f"Neuer Punkt:"):
    new_point_name = st.text_input("Neuer Punkt Name", value="p1", key="new_point_name")
    new_point_x = st.number_input("Neuer Punkt x", value=0.0, key="new_point_x")
    new_point_y = st.number_input("Neuer Punkt y", value=0.0, key="new_point_y")

    if st.sidebar.button("Punkt hinzufügen", key="add_point"):
        new_point = Point(new_point_x, new_point_y, new_point_name)
        mechanism.points.append(new_point)
        st.sidebar.success(f"Punkt '{new_point_name}' hinzugefügt!")

# Punkte verlinken
st.sidebar.header("Punkte verlinken")   
with st.sidebar.expander(f"Neue Verbindung:"):
    point_names = [p.name for p in [mechanism.c, mechanism.p0] + mechanism.points]
    point1_name = st.selectbox("Erster Punkt", point_names, key="link_point1")
    point2_name = st.selectbox("Zweiter Punkt", point_names, key="link_point2")

    if st.sidebar.button("Link hinzufügen", key="add_link"):
        point1 = next(p for p in [mechanism.c, mechanism.p0] + mechanism.points if p.name == point1_name)
        point2 = next(p for p in [mechanism.c, mechanism.p0] + mechanism.points if p.name == point2_name)
        mechanism.add_link(point1, point2)
        st.sidebar.success(f"Link zwischen '{point1_name}' und '{point2_name}' hinzugefügt!")

# Slider für die Winkelgeschwindigkeit hinzufügen
st.sidebar.header("Winkelgeschwindigkeit einstellen")
angular_velocity = st.sidebar.slider("Winkelgeschwindigkeit (Grad pro Sekunde)", 1.0, 15.0, 1.0, step=1.0)

# Auswahl des Punktes für die Bahnkurve
st.sidebar.header("Bahnkurve anzeigen")
selected_point_name = st.sidebar.selectbox("Wähle einen Punkt für die Bahnkurve", point_names, key="selected_point")

# Liste zur Speicherung der Bahnkurve
if "trajectory" not in st.session_state:
    st.session_state.trajectory = []

# ---------------------------------------------------------------------
# JSON Speichern/Laden mit Namensverwaltung
# ---------------------------------------------------------------------

# Speichern
if st.sidebar.button("Punkt übernehmen"):
    stored_mechanisms[mechanism_name] = mechanism.to_dict()
    with open(MECHANISM_FILE, "w", encoding="utf-8") as f:
        json.dump(stored_mechanisms, f, ensure_ascii=False, indent=2)
    st.sidebar.success(f"Mechanismus '{mechanism_name}' gespeichert!")

# ---------------------------------------------------------------------
# Punkte anzeigen und löschen
# ---------------------------------------------------------------------

st.sidebar.header("hinzugefügte Punkte:")
for point in [mechanism.c, mechanism.p0] + mechanism.points:
   with st.sidebar: 
        cols = st.columns([3, 1, 1])
        cols[0].write(f"{point.name}: ({point.x}, {point.y})")

        if point.name not in ["c", "p0"]:
            fixed = cols[1].checkbox("Fixieren", value=point.fixed, key=f"fixed_{point.name}")
            if fixed != point.fixed:
                point.fixed = fixed
                
        if cols[2].button("Löschen", key=f"delete_{point.name}"):
            mechanism.remove_point(point.name)
            st.experimental_rerun()

# ---------------------------------------------------------------------
# Links anzeigen und löschen
# ---------------------------------------------------------------------
st.sidebar.header("Hinzugefügte Links:")
link_data = []
for i, link in enumerate(mechanism.links):
    link_data.append({
        "Link": f"{link.p1.name} - {link.p2.name}",
        "Länge": f"{link.length:.2f}"
    })

if link_data:
    df_links = pd.DataFrame(link_data)
    st.sidebar.dataframe(df_links, height=300)  # Höhe der Tabelle angepasst

    # Button zum Herunterladen der Stückliste als CSV
    csv = df_links.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="Stückliste als CSV herunterladen",
        data=csv,
        file_name='stueckliste.csv',
        mime='text/csv',
    )
else:
    st.sidebar.error("Keine Links im Mechanismus vorhanden.")

# ---------------------------------------------------------------------
# Ausgangsposition anzeigen
# ---------------------------------------------------------------------
def display_initial_position(mechanism):
    fig, ax = plt.subplots()
    points = [mechanism.c, mechanism.p0] + mechanism.points
    xs = [p.x for p in points]
    ys = [p.y for p in points]

    ax.scatter(xs, ys, color="red")
    for p in points:
        ax.text(p.x + 0.3, p.y + 0.3, p.name, color="red")

    for link in mechanism.links:
        ax.plot([link.p1.x, link.p2.x], [link.p1.y, link.p2.y], color="blue", lw=2)

    # Zeichne den gestrichelten roten Kreis um c
    c = mechanism.c
    p0 = mechanism.p0
    radius = np.linalg.norm([p0.x - c.x, p0.y - c.y])
    circle = plt.Circle((c.x, c.y), radius, color='red', linestyle='--', fill=False)
    ax.add_artist(circle)

    ax.set_aspect("equal")
    ax.set_xlim(-100, 100)
    ax.set_ylim(-100, 100)
    st.pyplot(fig)

# Ausgangsposition anzeigen
st.header("Ausgangsposition des Systems")
display_initial_position(mechanism)

# Animation
plot_placeholder = st.empty()

# Start/Stop Button
if "running" not in st.session_state:
    st.session_state.running = False

if st.button("Animation starten / stoppen"):
    st.session_state.running = not st.session_state.running
    if not st.session_state.running:
        plot_placeholder.empty()

run_animation(plot_placeholder, mechanism, angular_velocity, selected_point_name)

# Reset Button
if st.button("Reset Ausgangsposition"):
    st.session_state.running = False  # Stoppe die Animation
    st.session_state.mechanism = Mechanism.from_dict(st.session_state.initial_mechanism.to_dict())  # Mechanismus zurücksetzen
    
    # Aktualisiere die Darstellung
    plot_placeholder.empty()  # Vorheriges Bild leeren
    st.empty()  # Entferne den Plot der Animation
    st.header("Ausgangsposition des Systems")
    display_initial_position(st.session_state.initial_mechanism)  # Ausgangsposition erneut anzeigen

    st.success("Ausgangsposition zurückgesetzt!")