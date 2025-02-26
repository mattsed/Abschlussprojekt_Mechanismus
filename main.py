import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import json
import os
import csv
from scipy.optimize import minimize

# JSON-Datei für gespeicherte Mechanismen
MECHANISM_FILE = "mechanisms.json"
CSV_FILE = "coordinates.csv"

# ---------------------------------------------------------------
# (A) Hilfsklasse: Punkt
# ---------------------------------------------------------------
class Point:
    def __init__(self, x, y, name="", fixed=False):
        self.x = x
        self.y = y
        self.name = name
        self.fixed = fixed

    def position(self):
        return np.array([self.x, self.y])

    def move_to(self, x, y):
        if not self.fixed:
            self.x = x
            self.y = y

# ---------------------------------------------------------------
# (B) Hilfsklasse: Link (Verbindungsstück mit fixer Länge)
# ---------------------------------------------------------------
class Link:
    def __init__(self, point1, point2):
        self.p1 = point1
        self.p2 = point2
        self.length = np.linalg.norm(self.p2.position() - self.p1.position())

    def enforce_length(self):
        vec = self.p2.position() - self.p1.position()
        if np.linalg.norm(vec) == 0:
            return
        unit_vec = vec / np.linalg.norm(vec)
        new_pos = self.p1.position() + self.length * unit_vec
        self.p2.move_to(*new_pos)

# ---------------------------------------------------------------
# (C) Hauptklasse: Mechanismus
# ---------------------------------------------------------------
class Mechanism:
    def __init__(self, c, p0):
        self.c = c  
        self.p0 = p0
        self.links = [Link(c, p0)]
        self.theta = 0.0
        self.points = []

    def update_mechanism(self, step_size):
        """ Aktualisiert p0 durch Rotation um c """
        self.theta += np.radians(step_size)

        r = self.links[0].length  
        new_p0_x = self.c.x + r * np.cos(self.theta)
        new_p0_y = self.c.y + r * np.sin(self.theta)
        self.p0.move_to(new_p0_x, new_p0_y)

        self.optimize_lengths()

    def optimize_lengths(self): 
        def error_function(coords):
            error = 0
            for i, point in enumerate(self.points):
                x, y = coords[2 * i], coords[2 * i + 1]
                point.move_to(x, y)
            for link in self.links:
                error += (np.linalg.norm(link.p2.position() - link.p1.position()) - link.length) ** 2
            return error
        
        initial_positions = []
        for point in self.points:
            initial_positions.extend([point.x, point.y])

        result = minimize(error_function, initial_positions, method='Powell')
        optimized_positions = result.x

        for i, point in enumerate(self.points):
            point.move_to(optimized_positions[2 * i], optimized_positions[2 * i + 1])

    def add_link(self, point1, point2):
        self.links.append(Link(point1, point2))

    def remove_link(self, point1_name, point2_name):
        self.links = [link for link in self.links if not ((link.p1.name == point1_name and link.p2.name == point2_name) or (link.p1.name == point2_name and link.p2.name == point1_name))]

    def remove_point(self, point_name):
        self.points = [p for p in self.points if p.name != point_name]
        self.links = [link for link in self.links if link.p1.name != point_name and link.p2.name != point_name]

    def save_coordinates_to_csv(self, step_size):
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Angle (degrees)", "Point", "x", "y"])
            for angle in range(0, 360, step_size):
                self.theta = np.radians(angle)
                self.update_mechanism(0)  # Update mechanism without changing theta
                writer.writerow([angle, "p0", self.p0.x, self.p0.y])
                for point in self.points:
                    writer.writerow([angle, point.name, point.x, point.y])

    def to_dict(self):
        return {
            "c": (self.c.x, self.c.y),
            "p0": (self.p0.x, self.p0.y),
            "theta": self.theta,
            "points": [(p.x, p.y, p.name, p.fixed) for p in self.points],
            "links": [(link.p1.name, link.p2.name) for link in self.links],
        }

    @classmethod
    def from_dict(cls, data):
        c = Point(*data["c"], "c")
        p0 = Point(*data["p0"], "p0")
        mechanism = cls(c, p0)
        mechanism.theta = data["theta"]
        mechanism.points = [Point(x, y, name, fixed) for x, y, name, fixed in data["points"]]
        for p1_name, p2_name in data["links"]:
            p1 = next(p for p in [mechanism.c, mechanism.p0] + mechanism.points if p.name == p1_name)
            p2 = next(p for p in [mechanism.c, mechanism.p0] + mechanism.points if p.name == p2_name)
            mechanism.add_link(p1, p2)
        return mechanism

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

step_size = st.slider("Schrittweite (Grad)", 1, 20, 5)

# Start/Stop Button
if "running" not in st.session_state:
    st.session_state.running = False
if st.button("Animation starten / stoppen"):
    st.session_state.running = not st.session_state.running

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
while st.session_state.running:
    mechanism.update_mechanism(step_size)

    fig, ax = plt.subplots()
    points = [mechanism.c, mechanism.p0] + mechanism.points
    xs = [p.x for p in points]
    ys = [p.y for p in points]

    ax.scatter(xs, ys, color="red")
    for p in points:
        ax.text(p.x + 0.3, p.y + 0.3, p.name, color="red")

    for link in mechanism.links:
        ax.plot([link.p1.x, link.p2.x], [link.p1.y, link.p2.y], color="blue", lw=2)
        
    ax.set_aspect("equal")
    ax.set_xlim(-100, 100)
    ax.set_ylim(-100, 100)
    plot_placeholder.pyplot(fig)

    time.sleep(0.1)

# ---------------------------------------------------------------------
# Save coordinates to CSV
# ---------------------------------------------------------------------
if st.button("Speichere Koordinaten zu CSV"):
    mechanism.save_coordinates_to_csv(step_size)
    st.success("Koordinaten wurden in die CSV-Datei gespeichert!")
