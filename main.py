import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import json

# ---------------------------------------------------------------
# (A) Hilfsklasse: Punkt
# ---------------------------------------------------------------
class Point:
    def __init__(self, x, y, name=""):
        self.x = x
        self.y = y
        self.name = name

    def position(self):
        return (self.x, self.y)

    def move_to(self, x, y):
        self.x = x
        self.y = y

# ---------------------------------------------------------------
# (B) Hilfsklasse: Link (Verbindungsstück mit fixer Länge)
# ---------------------------------------------------------------
class Link:
    def __init__(self, point1, point2):
        self.p1 = point1
        self.p2 = point2
        self.length = np.linalg.norm(np.array(self.p2.position()) - np.array(self.p1.position()))

    def enforce_length(self):
        vec = np.array(self.p2.position()) - np.array(self.p1.position())
        if np.linalg.norm(vec) == 0:
            return
        unit_vec = vec / np.linalg.norm(vec)
        new_pos = np.array(self.p1.position()) + self.length * unit_vec
        self.p2.move_to(*new_pos)

# ---------------------------------------------------------------
# (C) Hauptklasse: Mechanismus
# ---------------------------------------------------------------
class Mechanism:
    def __init__(self, c, p0, p1, p2):
        self.c = c  
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.links = [
            Link(c, p0),
            Link(p0, p1),
            Link(p1, p2)
        ]
        self.theta = 0.0

    def update_mechanism(self, step_size, coupler="p1"):
        """ Aktualisiert p0 durch Rotation um c und berechnet den Coupler """
        self.theta += np.radians(step_size)

        r = self.links[0].length  
        new_p0_x = self.c.x + r * np.cos(self.theta)
        new_p0_y = self.c.y + r * np.sin(self.theta)
        self.p0.move_to(new_p0_x, new_p0_y)

        if coupler == "p1":
            p1_new = circle_intersection(self.p0.position(), self.links[1].length,
                                         self.p2.position(), self.links[2].length)
            if p1_new is not None:
                self.p1.move_to(*p1_new)
        else:
            p2_new = circle_intersection(self.p0.position(), self.links[1].length,
                                         self.p1.position(), self.links[2].length)
            if p2_new is not None:
                self.p2.move_to(*p2_new)

        for link in self.links:
            link.enforce_length()

# ---------------------------------------------------------------
# (D) Hilfsfunktion: Schnitt zweier Kreise (Coupler-Berechnung)
# ---------------------------------------------------------------
def circle_intersection(centerA, rA, centerB, rB, pick_upper=True):
    A = np.array(centerA, dtype=float)
    B = np.array(centerB, dtype=float)
    d = np.linalg.norm(B - A)
    if d > rA + rB or d < abs(rA - rB):
        return None

    a = (rA**2 - rB**2 + d**2) / (2 * d)
    h = np.sqrt(max(rA**2 - a**2, 0.0))
    M = A + a * (B - A) / d
    dir_vec = (B - A) / d
    perp_vec = np.array([-dir_vec[1], dir_vec[0]])

    p_int_1 = M + h * perp_vec
    p_int_2 = M - h * perp_vec

    return p_int_1 if pick_upper else p_int_2

# ---------------------------------------------------------------------
# UI: Mechanismus-Steuerung
# ---------------------------------------------------------------------
st.set_page_config(layout="wide")
st.title("Simulation verschiedener Gelenk-Mechanismen")

# ---------------------------------------------------------------------
# (A) Eingabe: Punkte c (fix), p2 (fix), p0, p1
# ---------------------------------------------------------------------
with st.sidebar:
    st.markdown("# Konfiguration")   

# Fixe Punkte c und p2 (z. B. vom Nutzer definierbar)
    with st.expander("Antrieb"):
        cx = st.number_input("c.x (fix)", value=-30.0)
        cy = st.number_input("c.y (fix)", value=0.0)
        c = (cx, cy)
    with st.expander("Antriebskurbel??"):
        p2x = st.number_input("p2.x (fix)", value=0.0)
        p2y = st.number_input("p2.y (fix)", value=0.0)
        p2 = (p2x, p2y)
    with st.expander("test"):
        p0x = st.number_input("p0.x (Start)", value=-15.0)
        p0y = st.number_input("p0.y (Start)", value=10.0)
        p0_start = (p0x, p0y) 
    with st.expander("test"):
        p1x = st.number_input("p1.x (Start)", value=-10.0)
        p1y = st.number_input("p1.y (Start)", value=30.0)
        p1_start = (p1x, p1y)  

mechanism = Mechanism(Point(*c, "c"), Point(*p0_start, "p0"), Point(*p1_start, "p1"), Point(*p2, "p2"))



# Beliebig viele extra Gelenke 
if "extra_joints" not in st.session_state:
    st.session_state.extra_joints = {}  
    st.session_state.joint_count = 0    

if st.sidebar.button("➕ Gelenk hinzufügen") and st.session_state.joint_count < 20:
    joint_id = st.session_state.joint_count + 4  # IDs starten ab 4
    st.session_state.extra_joints[f"Gelenk {joint_id}"] = {"x": 0.0, "y": 0.0}
    st.session_state.joint_count += 1

if st.sidebar.button("🗑 Gelenk entfernen") and st.session_state.joint_count > 0:
    last_joint = f"Gelenk {st.session_state.joint_count + 3}"  # Letztes Gelenk berechnen
    if last_joint in st.session_state.extra_joints:
        del st.session_state.extra_joints[last_joint]  # Gelenk löschen
        st.session_state.joint_count -= 1  # Zähler anpassen

for joint_name, values in st.session_state.extra_joints.items():
    with st.sidebar.expander(joint_name):
        values["x"] = st.number_input(f"{joint_name} - X", value=values["x"], step=1.0)
        values["y"] = st.number_input(f"{joint_name} - Y", value=values["y"], step=1.0)








# ---------------------------------------------------------------------
# (B) Gliederlängen aus Anfangspositionen
# ---------------------------------------------------------------------
with st.sidebar:
    st.subheader("2) Gliederlängen (aus Startposition)")

    # 1) c -> p0
    L_c_p0 = np.linalg.norm(np.array(p0_start) - np.array(c))
    # 2) p0 -> p1
    L_p0_p1 = np.linalg.norm(np.array(p1_start) - np.array(p0_start))
    # 3) p1 -> p2
    L_p1_p2 = np.linalg.norm(np.array(p1_start) - np.array(p2))

    st.write(f"Länge c->p0 = {L_c_p0:.3f}")
    st.write(f"Länge p0->p1 = {L_p0_p1:.3f}")
    st.write(f"Länge p1->p2 = {L_p1_p2:.3f}")

# ---------------------------------------------------------------------
# (C) Coupler-Auswahl
# ---------------------------------------------------------------------
with st.sidebar:
    st.subheader("3) Coupler-Auswahl")
    coupler_options = ["p1", "p2"]
    coupler_choice = st.selectbox("Welcher Punkt soll der 'Coupler' sein? (p2 bleibt sonst fix)", coupler_options)
    # Wenn coupler_choice = "p1", dann wird p1 per Kreis-Schnitt bestimmt, p2 bleibt fix
    # Wenn coupler_choice = "p2", dann wird p2 per Kreis-Schnitt bestimmt, p1 bleibt fix

    # Um oben/unten Schnitt zu wählen
    pick_upper = st.checkbox("Oberen Schnittpunkt wählen?", value=True)

# ---------------------------------------------------------------------
# (D) Winkelsteuerung: p0 rotiert um c
# ---------------------------------------------------------------------
with st.sidebar:
    st.subheader("4) Animation/Steuerung")
    step_size = st.slider("Schrittweite (Grad pro Frame)", 1, 20, 5)
    if "theta" not in st.session_state:
        st.session_state.theta = 0.0
    if "running" not in st.session_state:
        st.session_state.running = False

    if st.button("Animation starten/stoppen"):
        st.session_state.running = not st.session_state.running

# ---------------------------------------------------------------------
# JSON Speichern/Laden
# ---------------------------------------------------------------------
with st.sidebar:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Speichere Einstellungen in JSON"):
            data = {
                "c": (c.x, c.y),
                "p2": (p2.x, p2.y),
                "p0": (p0.x, p0.y),
                "p1": (p1.x, p1.y),
                "theta": mechanism.theta,
                "step_size": step_size,
                "coupler_choice": coupler_choice
            }
            with open("mechanism.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            st.success("Einstellungen gespeichert!")

    with col2:
        if st.button("Lade Einstellungen aus JSON"):
            try:
                with open("mechanism.json", "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Erstelle Mechanismus mit geladenen Werten neu
                c = Point(*data["c"], "c")
                p2 = Point(*data["p2"], "p2")
                p0 = Point(*data["p0"], "p0")
                p1 = Point(*data["p1"], "p1")

                st.session_state.mechanism = Mechanism(c, p0, p1, p2)
                st.session_state.running = False
                st.success("Einstellungen geladen!")
            except FileNotFoundError:
                st.error("mechanism.json nicht gefunden.")
            except Exception as e:
                st.error(f"Fehler beim Laden: {e}")

# ---------------------------------------------------------------------
# Animation
# ---------------------------------------------------------------------
plot_placeholder = st.empty()
while st.session_state.running:
    mechanism.update_mechanism(step_size, coupler_choice)

    fig, ax = plt.subplots()
    points = [mechanism.c, mechanism.p0, mechanism.p1, mechanism.p2]
    xs = [p.x for p in points]
    ys = [p.y for p in points]

    ax.scatter(xs, ys, color="red")
    for p in points:
        ax.text(p.x + 0.3, p.y + 0.3, p.name, color="red")

    for link in mechanism.links:
        ax.plot([link.p1.x, link.p2.x], [link.p1.y, link.p2.y], color="blue", lw=2)
        
    ax.set_aspect("equal")
    ax.set_xlim(-60, 60)
    ax.set_ylim(-30, 60)
    plot_placeholder.pyplot(fig)

    time.sleep(0.1)
