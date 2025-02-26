import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import json
import os
import csv
from scipy.optimize import minimize
#from point import Point 

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