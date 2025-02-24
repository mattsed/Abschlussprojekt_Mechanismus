import numpy as np

# Punktkoordinaten
p0 = np.array([0, 0])    # p0
p1 = np.array([10, 35])  # p1
p2 = np.array([-26.81, 10.72]) # p2


# Mittelpunkt des Kreises
c = np.array([-30, 0])

x = np.array([p0[0], p0[1],
              p1[0], p1[1],
              p2[0], p2[1]])

A = np.array([
    [1,  0, -1,  0,  0,  0],  
    [0,  1,  0, -1,  0,  0],  
    [0,  0,  1,  0, -1,  0],  
    [0,  0,  0,  1,  0, -1]   
])

# ----------------------------------------------------------
# BERECHNUNG DES DREHWINKELS phi ZWISCHEN c UND p2
# ----------------------------------------------------------
# Vektor vom Mittelpunkt c zum Punkt p2
r = p2 - c  # [(-25) - (-30), 10 - 0] = [5, 10]


# Wikel in Radiant:
phi = np.arctan2(r[1], r[0])  # arctan2(y, x)
# Winkel in Grad:
phi_deg = np.degrees(phi)

# ----------------------------------------------------------
# BERECHNUNG DER GLIEDERLÄNGEN
# ----------------------------------------------------------
# Matrix-Vektor-Multiplikation: Differenzen der Punktkoordinaten
l_hat = A @ x  # -> [-10, -35, 35, 25]

# Umformen zu 2D-Vektoren (x- und y-Differenzen)
L = l_hat.reshape(-1, 2)  

# Euklidische Norm jeder Zeile 
l = np.linalg.norm(L, axis=1) 

# ----------------------------------------------------------
# BERECHNUNG DES FEHLERS
# ----------------------------------------------------------
# Beispiel: Angenommene Soll- oder Referenzlängen (l_ref).
l_ref = np.array([36.4005, 41.9227])

# Fehlervektor: Differenz zwischen Ist-Längen und Referenz
e = l - l_ref  # z.B. [0, 1.0889]

error_norm = np.linalg.norm(e)

# ----------------------------------------------------------
# AUSGABEN
# ----------------------------------------------------------
print("Mittelpunkt c:", c)
print("Punkt p2:", p2)
print("Vektor r = p2 - c:", r)
print(f"Drehwinkel phi (in Radiant) = {phi:.4f}")
print(f"Drehwinkel phi (in Grad)    = {phi_deg:.2f}")
print("\nDifferenzvektor l_hat (x- und y-Differenzen aller Glieder):")
print(l_hat)
print("\nMatrix L (jeweils [Δx, Δy] pro Glied):")
print(L)
print("\nTatsächliche Längen der Glieder:")
print(l)
print("\nFehlervektor e = l - l_ref:")
print(e)
print("Summe der Fehlerquadrate =", np.sum(e**2))
print("Euklidische Norm des Fehlervektors =", error_norm)