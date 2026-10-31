# 3D High-Performance N-Body Gravitational Simulation

A real-time 3D gravitational N-Body simulation developed in **C++17 using OpenMP** for parallel computing, with a **Python-based interactive visualization dashboard** built using PyQt6 and VisPy.

This project explores parallel computing, shared-memory parallelism, CPU performance optimization, and real-time scientific visualization.

## Project Overview

The N-Body problem simulates the gravitational interactions between multiple particles. Every particle exerts a gravitational force on every other particle, making the direct computation computationally expensive as the number of particles increases.

This project implements a direct N-Body simulation and explores how OpenMP can accelerate its computation through multithreading.

### Key Features

- 3D gravitational simulation of interacting particles.
- Sequential and OpenMP-parallel implementations.
- Shared-memory parallelism using OpenMP.
- Configurable number of particles (10–5000).
- Adjustable OpenMP thread count.
- Real-time 3D particle visualization.
- Interactive dashboard built with PyQt6 and VisPy.
- Start, Pause, Reset, and Stop controls.
- Performance benchmarking and speedup analysis.
- Momentum conservation validation.

## Technologies Used

| Technology | Purpose |
|---|---|
| C++17 | Simulation implementation |
| OpenMP | CPU parallelization |
| Python | Visualization and process management |
| NumPy | Numerical data processing |
| VisPy | Real-time 3D visualization |
| PyQt6 | Interactive dashboard |
| Matplotlib | Static visualization and plots |
| GCC | C++ compilation |

## Project Structure

```text
nbody-hpc/
│
├── src/
│   ├── nbody_serial.cpp
│   ├── nbody_openmp.cpp
│   └── nbody_live.cpp
│
├── scripts/
│   └── visualize.py
│
├── results/
│   └── final_positions.csv
│
├── plots/
│   └── nbody_3d.png
│
├── benchmarks/
│   └── baseline.txt
│
├── live_visualization.py
│
└── README.md
```

## Mathematical Model

The gravitational acceleration acting on particle \(i\) is calculated as:

\[
\vec{a}_i =
G \sum_{j \ne i}
m_j
\frac{\vec{r}_j-\vec{r}_i}
{(|\vec{r}_j-\vec{r}_i|^2+\epsilon^2)^{3/2}}
\]

Where:

- \(G\) is the gravitational constant.
- \(m_j\) is the mass of particle \(j\).
- \(\vec{r}_i\) and \(\vec{r}_j\) are particle positions.
- \(\epsilon\) is the softening parameter, used to avoid singularities at very small distances.

The simulation uses **Symplectic Euler integration**:

\[
\vec{v}_i^{n+1}=\vec{v}_i^n+\vec{a}_i^n\Delta t
\]

\[
\vec{r}_i^{n+1}=\vec{r}_i^n+\vec{v}_i^{n+1}\Delta t
\]

The direct gravitational interaction algorithm has a computational complexity of:

\[
O(N^2)
\]

where \(N\) is the number of particles.

## Parallelization with OpenMP

The computationally intensive force calculation is parallelized using OpenMP.

```cpp
#pragma omp parallel for schedule(static)
for (int i = 0; i < N; i++) {
    // Calculate gravitational forces
}
```

Each thread calculates the acceleration of different particles.

Since each iteration writes to a different particle's acceleration, the outer loop can be parallelized without requiring synchronization for the acceleration calculations.

Particle updates are also parallelized using OpenMP.

The number of threads can be configured through the `OMP_NUM_THREADS` environment variable.

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/yash7756/nbody-hpc.git
cd nbody-hpc
```

### 2. Install the C++ compiler

Install GCC with OpenMP support.

For Windows, MSYS2 UCRT64 can be used.

Verify the compiler:

```bash
g++ --version
```

### 3. Compile the sequential implementation

```bash
g++ -O3 -std=c++17 src/nbody_serial.cpp -o nbody_serial.exe
```

Run:

```bash
./nbody_serial.exe
```

### 4. Compile the OpenMP implementation

```bash
g++ -O3 -std=c++17 -fopenmp src/nbody_openmp.cpp -o nbody_openmp.exe
```

Run with four threads:

```bash
export OMP_NUM_THREADS=4
./nbody_openmp.exe
```

Change the thread count to experiment with different configurations:

```bash
export OMP_NUM_THREADS=8
./nbody_openmp.exe
```

### 5. Compile the live simulation

```bash
g++ -O3 -std=c++17 -fopenmp -pthread src/nbody_live.cpp -o nbody_live.exe
```

Run with a configurable number of particles:

```bash
./nbody_live.exe 500
```

The supported particle count is between 10 and 5000.

### 6. Install Python dependencies

```bash
python -m pip install numpy vispy PyQt6 matplotlib
```

### 7. Launch the interactive visualization

```bash
python live_visualization.py
```

The Python dashboard launches the C++ simulation as a separate process and receives particle coordinates for real-time visualization.

## Interactive Dashboard

The dashboard provides the following controls:

| Control | Function |
|---|---|
| Start | Resume the simulation |
| Pause | Pause particle movement |
| Reset | Reinitialize particle positions |
| Stop | Stop the simulation |
| Particle Selector | Select the number of particles |
| Apply Particle Count | Restart the simulation with the selected particle count |

The OpenMP thread count can be changed in `live_visualization.py`:

```python
env["OMP_NUM_THREADS"] = "8"
```

## Preliminary Performance Results

Initial benchmarking was conducted with 500 particles and 500 simulation iterations.

The following values are preliminary median runtimes from five runs:

| Configuration | Median Runtime | Speedup |
|---|---:|---:|
| Serial | 0.9062 s | 1.00x |
| OpenMP – 1 thread | 0.9646 s | 0.94x |
| OpenMP – 2 threads | 0.5394 s | 1.68x |
| OpenMP – 4 threads | 0.4864 s | 1.86x |
| OpenMP – 8 threads | 0.3362 s | 2.70x |

Speedup is calculated as:

\[
S(p)=\frac{T_{\text{serial}}}{T_{\text{parallel}}}
\]

These are preliminary measurements, not definitive hardware performance results. Runtime variations can occur due to CPU scheduling, clock frequency, thermal conditions, and background processes.

The live visualization runtime is not directly comparable to these benchmarks because streaming coordinates and flushing output introduce additional overhead.

## Validation

The simulation includes a momentum conservation check.

The total momentum is calculated as:

\[
\vec{P}=\sum_{i=1}^{N}m_i\vec{v}_i
\]

In the initial tests, the difference between initial and final total momentum was approximately:

```text
5.54535e-18
```

This is consistent with floating-point round-off error and provides a useful numerical validation check.

## Learning Outcomes

Through this project, I explored:

- Computational complexity of the direct N-Body algorithm.
- Shared-memory parallel programming with OpenMP.
- Multithreading and workload distribution.
- CPU performance benchmarking.
- Parallel speedup and efficiency.
- Numerical integration and gravitational modelling.
- C++ and Python interoperability using subprocess communication.
- Real-time scientific visualization.

## Author

**Yash Ashok Ambole**

M.Sc. High Performance Computing & Quantum Computing  
Deggendorf Institute of Technology, Germany

GitHub: [@yash7756](https://github.com/yash7756)

---
