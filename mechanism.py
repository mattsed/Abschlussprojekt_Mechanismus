import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import json
import os
import csv
from scipy.optimize import minimize
from point import Point
from link import Link

CSV_FILE = "mechanism_coordinates.csv"  # Fehlende Konstante hinzugefügt

class Mechanism:
    def __init__(self, c, p0, clockwise=True):
        self.c = c  
        self.p0 = p0
        self.links = [Link(c, p0)]
        self.theta = 0.0
        self.points = []
        self.clockwise = clockwise  # True für Uhrzeigersinn, False für Gegenuhrzeigersinn

    def update_mechanism(self, step_size_radians):
    
        self.theta += (-1 if self.clockwise else 1) * step_size_radians
        self.theta = self.theta % (2 * np.pi)  # Begrenzung auf 0 bis 2π für eine volle Umdrehung

        r = self.links[0].length  
        new_p0 = np.array([self.c.x + r * np.cos(self.theta), self.c.y + r * np.sin(self.theta)])

        try:
            self.p0.move_to(*new_p0)
        except Exception as e:
            print(f"Fehler beim Bewegen von p0: {e}")

        if self.points:
            self.optimize_lengths()

    def optimize_lengths(self): 
        def error_function(coords):
            coords = coords.reshape(-1, 2)  # Umwandlung in (N, 2)-Array für schnellere Verarbeitung
            for i, point in enumerate(self.points):
                point.move_to(*coords[i])  
            
            return sum((np.linalg.norm(link.p2.position() - link.p1.position()) - link.length) ** 2 for link in self.links)
        
        if not self.points:
            return  # Falls keine Punkte vorhanden sind, nichts optimieren

        initial_positions = np.array([[p.x, p.y] for p in self.points]).flatten()

        result = minimize(error_function, initial_positions, method='Powell')
        
        if result.success:
            optimized_positions = result.x.reshape(-1, 2)
            for point, new_pos in zip(self.points, optimized_positions):
                point.move_to(*new_pos)
        else:
            print(f"Optimierung fehlgeschlagen: {result.message}")

    def add_link(self, point1, point2):
        if any((link.p1 == point1 and link.p2 == point2) or (link.p1 == point2 and link.p2 == point1) for link in self.links):
            print("Link existiert bereits!")
            return
        self.links.append(Link(point1, point2))

    def remove_link(self, point1_name, point2_name):
        self.links = [link for link in self.links if not ((link.p1.name == point1_name and link.p2.name == point2_name) or (link.p1.name == point2_name and link.p2.name == point1_name))]

    def remove_point(self, point_name):
        self.points = [p for p in self.points if p.name != point_name]
        self.links = [link for link in self.links if link.p1.name != point_name and link.p2.name != point_name]
        self.optimize_lengths()  # Nach Entfernen eines Punkts Längen anpassen

    def save_coordinates_to_csv(self, step_size_degrees):
        step_size_radians = np.radians(step_size_degrees)  # Umwandlung nur einmal
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Angle (degrees)", "Point", "x", "y"])
            for angle in range(0, 360, step_size_degrees):
                self.theta = np.radians(angle)  # Direkt in Radiant setzen
                self.update_mechanism(0)  # Update ohne Änderung der Rotation
                writer.writerow([angle, "p0", self.p0.x, self.p0.y])
                for point in self.points:
                    writer.writerow([angle, point.name, point.x, point.y])

    def to_dict(self):
        return {
            "c": (self.c.x, self.c.y),
            "p0": (self.p0.x, self.p0.y),
            "theta": self.theta,
            "clockwise": self.clockwise,  # Fehlende Eigenschaft hinzugefügt
            "points": [(p.x, p.y, p.name, p.fixed) for p in self.points],
            "links": [(link.p1.name, link.p2.name) for link in self.links],
        }

    @classmethod
    def from_dict(cls, data):
        c = Point(*data["c"], "c")
        p0 = Point(*data["p0"], "p0")
        clockwise = data.get("clockwise", True)  # Standardwert True falls nicht vorhanden
        mechanism = cls(c, p0, clockwise)
        mechanism.theta = data["theta"]
        mechanism.points = [Point(x, y, name, fixed) for x, y, name, fixed in data["points"]]
        for p1_name, p2_name in data["links"]:
            p1 = next(p for p in [mechanism.c, mechanism.p0] + mechanism.points if p.name == p1_name)
            p2 = next(p for p in [mechanism.c, mechanism.p0] + mechanism.points if p.name == p2_name)
            mechanism.add_link(p1, p2)
        return mechanism
