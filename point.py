import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import json
import os
import csv
from scipy.optimize import minimize

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