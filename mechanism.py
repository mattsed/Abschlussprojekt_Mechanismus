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