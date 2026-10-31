
import os
import sys
import time
import queue
import threading
import subprocess

import numpy as np

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel
)

from PyQt6.QtCore import QTimer

from vispy import app, scene


# ---------------- CONFIGURATION ----------------

PROJECT_DIR = r"C:\Users\HP\Documents\nbody-hpc"
EXECUTABLE = os.path.join(PROJECT_DIR, "nbody_live.exe")

N = 500

frame_queue = queue.Queue(maxsize=2)

# Select PyQt6 as VisPy backend
app.use_app("pyqt6")


# ---------------- START C++ PROCESS ----------------

env = os.environ.copy()
env["OMP_NUM_THREADS"] = "4"
env["PATH"] = r"C:\msys64\ucrt64\bin;" + env["PATH"]

process = subprocess.Popen(
    [EXECUTABLE],
    cwd=PROJECT_DIR,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=None,
    text=True,
    bufsize=1,
    env=env
)


# ---------------- COMMAND HANDLER ----------------

def send_command(command):

    if process.poll() is None:

        try:
            process.stdin.write(command + "\n")
            process.stdin.flush()

            print("Command:", command)

        except (BrokenPipeError, OSError):
            print("C++ process is not accepting commands.")


# ---------------- READ C++ FRAMES ----------------

def read_cpp_output():

    positions = []

    for line in process.stdout:

        line = line.strip()

        if line == "END_FRAME":

            if len(positions) == N:

                frame = np.array(
                    positions,
                    dtype=np.float32
                )

                if frame_queue.full():

                    try:
                        frame_queue.get_nowait()
                    except queue.Empty:
                        pass

                frame_queue.put(frame)

            positions = []

        else:

            try:
                coordinates = [
                    float(x) for x in line.split()
                ]

                if len(coordinates) == 3:
                    positions.append(coordinates)

            except ValueError:
                continue


reader_thread = threading.Thread(
    target=read_cpp_output,
    daemon=True
)

reader_thread.start()


# ---------------- CREATE VISPY CANVAS ----------------

canvas = scene.SceneCanvas(
    keys="interactive",
    title="HPC N-Body Simulation",
    size=(1100, 700),
    show=False,
    bgcolor="black"
)

view = canvas.central_widget.add_view()

view.camera = scene.TurntableCamera(
    fov=45,
    elevation=25,
    azimuth=45,
    distance=20
)

particles = scene.visuals.Markers()
view.add(particles)


# ---------------- QT APPLICATION ----------------

qt_app = QApplication.instance() or QApplication(sys.argv)

window = QMainWindow()
window.setWindowTitle("HPC N-Body Simulation Dashboard")
window.resize(1200, 850)

central_widget = QWidget()
main_layout = QVBoxLayout(central_widget)


# Add VisPy canvas
main_layout.addWidget(canvas.native, stretch=1)


# ---------------- CONTROL BUTTONS ----------------

button_layout = QHBoxLayout()

start_button = QPushButton("Start")
pause_button = QPushButton("Pause")
reset_button = QPushButton("Reset")
stop_button = QPushButton("Stop")

button_layout.addWidget(start_button)
button_layout.addWidget(pause_button)
button_layout.addWidget(reset_button)
button_layout.addWidget(stop_button)

main_layout.addLayout(button_layout)


# ---------------- STATUS DISPLAY ----------------

status_label = QLabel("Status: Paused")
fps_label = QLabel("FPS: 0")
particle_label = QLabel("Particles: 500")

info_layout = QHBoxLayout()

info_layout.addWidget(status_label)
info_layout.addWidget(fps_label)
info_layout.addWidget(particle_label)

main_layout.addLayout(info_layout)


# ---------------- BUTTON ACTIONS ----------------

def start_simulation():

    send_command("RESUME")
    status_label.setText("Status: Running")


def pause_simulation():

    send_command("PAUSE")
    status_label.setText("Status: Paused")


def reset_simulation():

    send_command("RESET")
    status_label.setText("Status: Reset requested")


def stop_simulation():

    send_command("STOP")
    status_label.setText("Status: Stopping")

    stop_button.setEnabled(False)


start_button.clicked.connect(start_simulation)
pause_button.clicked.connect(pause_simulation)
reset_button.clicked.connect(reset_simulation)
stop_button.clicked.connect(stop_simulation)


# ---------------- FPS AND RENDERING ----------------

displayed_frames = 0
last_fps_time = time.perf_counter()


def update_visualization():

    global displayed_frames
    global last_fps_time

    latest_frame = None

    while not frame_queue.empty():

        try:
            latest_frame = frame_queue.get_nowait()

        except queue.Empty:
            break

    if latest_frame is not None:

        particles.set_data(
            latest_frame,
            face_color=(0.2, 0.7, 1.0, 1.0),
            edge_color=None,
            size=5
        )

        displayed_frames += 1

    current_time = time.perf_counter()

    if current_time - last_fps_time >= 1.0:

        fps = displayed_frames / (
            current_time - last_fps_time
        )

        fps_label.setText(f"FPS: {fps:.1f}")

        displayed_frames = 0
        last_fps_time = current_time


timer = QTimer()
timer.timeout.connect(update_visualization)
timer.start(16)


# ---------------- DISPLAY WINDOW ----------------

window.setCentralWidget(central_widget)
window.show()


# ---------------- CLEANUP ----------------

def cleanup():

    if process.poll() is None:

        send_command("STOP")

        try:
            process.wait(timeout=3)

        except subprocess.TimeoutExpired:
            process.terminate()


qt_app.aboutToQuit.connect(cleanup)


if __name__ == "__main__":

    qt_app.exec()
