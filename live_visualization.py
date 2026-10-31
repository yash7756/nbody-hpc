
import os
import subprocess
import threading
import queue

import numpy as np
from vispy import app, scene


# Project configuration
PROJECT_DIR = r"C:\Users\HP\Documents\nbody-hpc"
EXECUTABLE = os.path.join(PROJECT_DIR, "nbody_live.exe")

N = 500

# Queue for transferring frames from C++ reader to VisPy
frame_queue = queue.Queue(maxsize=2)


# Launch the C++ simulation
env = os.environ.copy()
env["OMP_NUM_THREADS"] = "4"
env["PATH"] = r"C:\msys64\ucrt64\bin;" + env["PATH"]
process = subprocess.Popen(
    [EXECUTABLE],
    cwd=PROJECT_DIR,
    stdout=subprocess.PIPE,
    stderr=None,
    text=True,
    bufsize=1,
    env=env
)


# Read frames in a background thread
def read_cpp_output():

    positions = []
    frame_count = 0

    for line in process.stdout:

        line = line.strip()

        if line == "END_FRAME":

            if len(positions) == N:
                frame = np.array(positions, dtype=np.float32)

                frame_count += 1

                print(
                    f"Received frame {frame_count}: "
                    f"{frame.shape}, "
                    f"min={frame.min():.3f}, "
                    f"max={frame.max():.3f}"
                )

                if frame_queue.full():
                    try:
                        frame_queue.get_nowait()
                    except queue.Empty:
                        pass

                frame_queue.put(frame)

            else:
                print("Invalid frame size:", len(positions))

            positions = []

        else:
            try:
                coordinates = [float(x) for x in line.split()]

                if len(coordinates) == 3:
                    positions.append(coordinates)

            except ValueError:
                continue

    print("C++ output stream ended.")

reader_thread = threading.Thread(
    target=read_cpp_output,
    daemon=True
)

reader_thread.start()


# Create the 3D visualization window
canvas = scene.SceneCanvas(
    keys="interactive",
    title="Live 3D N-Body Simulation - OpenMP",
    size=(1000, 700),
    show=True,
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


# Update visualization using received C++ frames
def update(event):

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


timer = app.Timer(
    interval=1 / 60,
    connect=update,
    start=True
)


if __name__ == "__main__":

    try:
        app.run()

    finally:
        if process.poll() is None:
            process.terminate()
