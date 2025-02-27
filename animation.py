import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time
from PIL import Image

def run_animation(plot_placeholder, mechanism, angular_velocity, selected_point_name):
    """Lässt den Mechanismus animiert laufen und speichert nach 360° ein GIF in der Sidebar."""

    fig, ax = plt.subplots()
    points = [mechanism.c, mechanism.p0] + mechanism.points

    scatter = ax.scatter([], [], color="red")
    text_labels = {p.name: ax.text(p.x, p.y, p.name, color="red") for p in points}
    lines = {link: ax.plot([], [], color="blue", lw=2)[0] for link in mechanism.links}
    trajectory_line, = ax.plot([], [], color="green", lw=1)

    c, p0 = mechanism.c, mechanism.p0
    radius = np.linalg.norm([p0.x - c.x, p0.y - c.y])
    circle = plt.Circle((c.x, c.y), radius, color='red', linestyle='--', fill=False)
    ax.add_artist(circle)

    ax.set_aspect("equal")
    ax.set_xlim(-100, 100)
    ax.set_ylim(-100, 100)

    # Liste zur Speicherung der GIF-Frames
    frames = []
    initial_theta = mechanism.theta  
    gif_created = False  # Sicherstellen, dass das GIF nur einmal erstellt wird

    while st.session_state.running:
        mechanism.update_mechanism(np.radians(angular_velocity))

        xs = [p.x for p in points]
        ys = [p.y for p in points]

        scatter.set_offsets(np.c_[xs, ys])
        for p in points:
            text_labels[p.name].set_position((p.x + 0.3, p.y + 0.3))

        for link, line in lines.items():
            line.set_data([link.p1.x, link.p2.x], [link.p1.y, link.p2.y])

        selected_point = next(p for p in points if p.name == selected_point_name)
        st.session_state.trajectory.append((selected_point.x, selected_point.y))
        traj_xs, traj_ys = zip(*st.session_state.trajectory)
        trajectory_line.set_data(traj_xs, traj_ys)

        plot_placeholder.pyplot(fig)

        # Frame speichern
        fig.canvas.draw()
        fig.canvas.flush_events()
        image = np.array(fig.canvas.renderer.buffer_rgba())
        frames.append(Image.fromarray(image))

        # Prüfen, ob eine volle Umdrehung abgeschlossen wurde
        if abs((mechanism.theta - initial_theta) % (2 * np.pi)) < np.radians(angular_velocity) and not gif_created:
            print("Volle Umdrehung abgeschlossen! Speichere GIF...")
            gif_filename = "mechanism_animation.gif"

            if frames:
                print("Speichere GIF mit", len(frames), "Frames.")
                frames[0].save(
                    gif_filename,
                    save_all=True,
                    append_images=frames[1:],
                    duration=50,  # Geschwindigkeit des GIFs
                    loop=0
                )

                # GIF in der Sidebar anzeigen
                st.sidebar.image(gif_filename, caption="Mechanismus-Animation", use_container_width=True)

                # Download-Button direkt in der Sidebar anzeigen
                st.sidebar.download_button(
                    label="GIF herunterladen",
                    data=open(gif_filename, "rb").read(),
                    file_name=gif_filename,
                    mime="image/gif"
                )

                gif_created = True  # Verhindert mehrfaches Speichern des GIFs

        time.sleep(0.01)