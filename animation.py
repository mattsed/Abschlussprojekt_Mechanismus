import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time

def run_animation(plot_placeholder, mechanism, angular_velocity, selected_point_name):
    fig, ax = plt.subplots()
    
    # Plot initial position
    points = [mechanism.c, mechanism.p0] + mechanism.points
    xs = [p.x for p in points]
    ys = [p.y for p in points]

    ax.scatter(xs, ys, color="red")
    for p in points:
        ax.text(p.x + 0.3, p.y + 0.3, p.name, color="red")

    for link in mechanism.links:
        ax.plot([link.p1.x, link.p2.x], [link.p1.y, link.p2.y], color="blue", lw=2)

    # Draw the dashed red circle around c
    c = mechanism.c
    p0 = mechanism.p0
    radius = np.linalg.norm([p0.x - c.x, p0.y - c.y])
    circle = plt.Circle((c.x, c.y), radius, color='red', linestyle='--', fill=False)
    ax.add_artist(circle)

    ax.set_aspect("equal")
    ax.set_xlim(-100, 100)
    ax.set_ylim(-100, 100)
    
    while st.session_state.running:
        mechanism.update_mechanism(angular_velocity)  # Verwenden Sie den Wert des Sliders

        fig, ax = plt.subplots()
        points = [mechanism.c, mechanism.p0] + mechanism.points
        xs = [p.x for p in points]
        ys = [p.y for p in points]

        ax.scatter(xs, ys, color="red")
        for p in points:
            ax.text(p.x + 0.3, p.y + 0.3, p.name, color="red")

        for link in mechanism.links:
            ax.plot([link.p1.x, link.p2.x], [link.p1.y, link.p2.y], color="blue", lw=2)

        # Bahnkurve des ausgewählten Punktes aktualisieren
        selected_point = next(p for p in points if p.name == selected_point_name)
        st.session_state.trajectory.append((selected_point.x, selected_point.y))
        traj_xs, traj_ys = zip(*st.session_state.trajectory)
        ax.plot(traj_xs, traj_ys, color="green", lw=1)

        # Zeichne den gestrichelten roten Kreis um c
        c = mechanism.c
        p0 = mechanism.p0
        radius = np.linalg.norm([p0.x - c.x, p0.y - c.y])
        circle = plt.Circle((c.x, c.y), radius, color='red', linestyle='--', fill=False)
        ax.add_artist(circle)

        ax.set_aspect("equal")
        ax.set_xlim(-100, 100)
        ax.set_ylim(-100, 100)
        plot_placeholder.pyplot(fig)

        time.sleep(0.01)
