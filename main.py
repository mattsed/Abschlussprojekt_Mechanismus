import streamlit as st
import numpy as np
import json

st.title("Mechanismus-Definition und Berechnung")

# -------------------------------
# (A) EINGABE DER PUNKTE UND GLIEDER
# -------------------------------
num_points = st.number_input("Anzahl Gelenkpunkte:", min_value=1, value=3, step=1)

points = []
for i in range(num_points):
    x_val = st.number_input(f"X-Koordinate für Punkt {i}", value=0.0, key=f"px_{i}")
    y_val = st.number_input(f"Y-Koordinate für Punkt {i}", value=0.0, key=f"py_{i}")
    points.append((x_val, y_val))

num_links = st.number_input("Anzahl Glieder:", min_value=0, value=2, step=1)

links = []
for j in range(num_links):
    p1 = st.selectbox(f"Glied {j} - Punkt 1:", range(num_points), key=f"p1_{j}")
    p2 = st.selectbox(f"Glied {j} - Punkt 2:", range(num_points), key=f"p2_{j}")
    links.append((p1, p2))

st.write("**Definierte Gelenkpunkte:**", points)
st.write("**Definierte Glieder:**", links)

# -------------------------------
# (B) SPEICHERN IN JSON
# -------------------------------
if st.button("Speichere Einstellungen in JSON"):
    data = {
        "points": points,    # Liste von (x,y)-Tupeln
        "links": links       # Liste von (index1, index2)-Tupeln
    }
    with open("mechanism.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    st.success("Einstellungen in 'mechanism.json' gespeichert!")

# -------------------------------
# (C) LADEN AUS JSON UND BERECHNUNG
# -------------------------------
if st.button("Lade Einstellungen aus JSON und führe Berechnung durch"):
    try:
        with open("mechanism.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        loaded_points = data["points"]
        loaded_links = data["links"]
        
        st.write("**Geladene Punkte:**", loaded_points)
        st.write("**Geladene Glieder:**", loaded_links)

        # Erzeuge den Vektor x aus den geladenen Punkten
        # x = [x0, y0, x1, y1, x2, y2, ...]
        x_list = []
        for (px, py) in loaded_points:
            x_list.extend([px, py])
        x = np.array(x_list, dtype=float)

        # Dynamisch die A-Matrix aus den Links bauen
        # Bei n Punkten haben wir 2n Dimensionen (x und y für jeden Punkt).
        # Bei m Gliedern entstehen 2m Zeilen (pro Glied eine x- und eine y-Differenz).
        n = len(loaded_points)
        m = len(loaded_links)
        A = np.zeros((2*m, 2*n))

        for row_index, (i, j) in enumerate(loaded_links):
            # X-Differenz
            A[2*row_index,   2*i]   = 1
            A[2*row_index,   2*j]   = -1
            # Y-Differenz
            A[2*row_index+1, 2*i+1] = 1
            A[2*row_index+1, 2*j+1] = -1

        # Matrix-Vektor-Multiplikation -> l_hat
        l_hat = A @ x

        # Jede Zeile (x,y) -> reshape in 2D: (m, 2)
        L = l_hat.reshape(m, 2)

        # Euklidische Norm -> tatsächliche Längen
        lengths = np.linalg.norm(L, axis=1)

        st.write("**Ermittelte Gliederlängen (Ist):**", lengths)

        # Optional: Beispiel-Soll-Längen (nur, wenn wir m=2 haben)
        if m == 2:
            l_ref = np.array([36.4005, 41.9227])  # Beispielwerte
            e = lengths - l_ref
            error_norm = np.linalg.norm(e)
            
            st.write("**Fehlervektor e (Ist - Soll):**", e)
            st.write("**Summe der Fehlerquadrate:**", np.sum(e**2))
            st.write("**Euklidische Norm des Fehlervektors:**", error_norm)
        else:
            st.info("Für mehr als 2 Glieder ist kein Beispiel-Soll-Vektor definiert.")

    except FileNotFoundError:
        st.error("Die Datei 'mechanism.json' wurde nicht gefunden. Bitte zuerst speichern!")
    except KeyError as e:
        st.error(f"Fehlender Schlüssel in JSON: {e}")
    except Exception as e:
        st.error(f"Ein unbekannter Fehler ist aufgetreten: {e}")