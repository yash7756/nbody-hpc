# 3D High-Performance N-Body Gravitational Simulation

A real-time 3D gravitational N-Body simulation developed using **C++17 and OpenMP** for parallel computing, with a **Python-based interactive visualization dashboard** built using PyQt6 and VisPy.

This project explores parallel computing, shared-memory parallelism, CPU performance optimization, numerical simulation, and real-time scientific visualization.

## Project Overview

The N-Body problem simulates the gravitational interactions between multiple particles. Every particle exerts a gravitational force on every other particle, making the direct computation computationally expensive as the number of particles increases.

This project implements a direct N-Body simulation using two approaches:

- Sequential implementation using C++.
- Parallel implementation using OpenMP.

The project also includes a real-time 3D visualization dashboard that communicates with the C++ simulation to display particle movement interactively.

## Key Features

- 3D gravitational simulation of interacting particles.
- Sequential and OpenMP-parallel implementations.
- Shared-memory parallelism using OpenMP.
- Configurable particle count (10–5000).
- Adjustable OpenMP thread count.
- Real-time 3D particle visualization.
- Interactive dashboard built with PyQt6 and VisPy.
- Start, Pause, Reset, and Stop controls.
- Performance benchmarking and speedup analysis.
- Momentum conservation validation.
- C++ and Python integration through subprocess communication.

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

### 1. Gravitational Acceleration

The gravitational acceleration acting on particle \(i\), due to all other particles, is calculated using Newton's law of universal gravitation with gravitational softening:

$$
\vec{a}_i =
G \sum_{\substack{j=1 \\ j \neq i}}^{N}
m_j
\frac{\vec{r}_j-\vec{r}_i}
{\left(
\left|\vec{r}_j-\vec{r}_i\right|^2+\epsilon^2
\right)^{3/2}}
$$

Where:

- \(G\) is the gravitational constant.
- \(m_j\) is the mass of particle \(j\).
- \(\vec{r}_i\) is the position vector of particle \(i\).
- \(\vec{r}_j\) is the position vector of particle \(j\).
- \(\epsilon\) is the gravitational softening parameter, used to avoid singularities when particles approach each other.
- \(N\) is the total number of particles.

### 2. Symplectic Euler Integration

The simulation uses the **Symplectic Euler integration method** to update particle velocities and positions at each timestep.

**Velocity update:**

$$
\vec{v}_i^{\,n+1}
=
\vec{v}_i^{\,n}
+
\vec{a}_i^{\,n}\Delta t
$$

**Position update:**

$$
\vec{r}_i^{\,n+1}
=
\vec{r}_i^{\,n}
+
\vec{v}_i^{\,n+1}\Delta t
$$

Where:

- \(\vec{v}_i^{\,n}\) is the velocity at timestep \(n\).
- \(\vec{a}_i^{\,n}\) is the acceleration at timestep \(n\).
- \(\vec{r}_i^{\,n}\) is the position at timestep \(n\).
- \(\Delta t\) is the simulation timestep.

### 3. Computational Complexity

The direct N-Body algorithm calculates gravitational interactions between every pair of particles.

The computational complexity per timestep is:

$$
T(N)=O(N^2)
$$

For \(K\) simulation timesteps:

$$
T(N,K)=O(KN^2)
$$

This quadratic complexity makes the N-Body problem computationally expensive for large particle counts.

## Parallelization with OpenMP

The computationally intensive gravitational force calculation is parallelized using OpenMP.

The outer loop distributes particle calculations across multiple CPU threads:

```cpp
#pragma omp parallel for schedule(static)
for (int i = 0; i < N; i++) {
    // Calculate gravitational forces
}
```

Each thread calculates the acceleration of different particles.

Since each iteration writes to a different particle's acceleration, the outer loop can be parallelized without requiring synchronization between iterations for these acceleration updates.

Particle position and velocity updates are also parallelized using OpenMP.

The number of threads can be configured through the `OMP_NUM_THREADS` environment variable.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yash7756/nbody-hpc.git
cd nbody-hpc
```

### 2. Install the C++ Compiler

Install GCC with OpenMP support.

For Windows, MSYS2 UCRT64 can be used.

Verify the compiler installation:

```bash
g++ --version
```

### 3. Compile the Sequential Implementation

```bash
g++ -O3 -std=c++17 src/nbody_serial.cpp -o nbody_serial.exe
```

Run:

```bash
./nbody_serial.exe
```

### 4. Compile the OpenMP Implementation

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

### 5. Compile the Live Simulation

```bash
g++ -O3 -std=c++17 -fopenmp -pthread src/nbody_live.cpp -o nbody_live.exe
```

Run with a configurable number of particles:

```bash
./nbody_live.exe 500
```

The supported particle count is between 10 and 5000.

### 6. Install Python Dependencies

```bash
python -m pip install numpy vispy PyQt6 matplotlib
```

### 7. Launch the Interactive Visualization

```bash
python live_visualization.py
```

The Python dashboard launches the C++ simulation as a separate process and receives particle coordinates for real-time visualization.

## Interactive Dashboard

The interactive dashboard provides the following controls:

| Control | Function |
|---|---|
| Start | Resume the simulation |
| Pause | Pause particle movement |
| Reset | Reinitialize particle positions |
| Stop | Stop the simulation |
| Particle Selector | Select the number of particles |
| Apply Particle Count | Restart the simulation with the selected particle count |

### Configuring OpenMP Threads

The OpenMP thread count can be changed in `live_visualization.py`:

```python
env["OMP_NUM_THREADS"] = "8"
```

This allows experimentation with different thread configurations without modifying the C++ implementation.

## Preliminary Performance Results

Initial benchmarking was conducted using:

- Number of particles: 500
- Simulation iterations: 500
- Optimization level: `-O3`
- Benchmark repetitions: 5 runs

The following values represent the median execution time from five runs:

| Configuration | Median Runtime | Speedup |
|---|---:|---:|
| Serial | 0.9062 s | 1.00x |
| OpenMP – 1 thread | 0.9646 s | 0.94x |
| OpenMP – 2 threads | 0.5394 s | 1.68x |
| OpenMP – 4 threads | 0.4864 s | 1.86x |
| OpenMP – 8 threads | 0.3362 s | 2.70x |

### Speedup Calculation

Parallel speedup measures how much faster the parallel implementation executes compared to the sequential implementation.

$$
S(p)=
\frac{T_{\text{serial}}}
{T_{\text{parallel}}(p)}
$$

Where:

- \(S(p)\) is the speedup using \(p\) threads.
- \(T_{\text{serial}}\) is the execution time of the sequential implementation.
- \(T_{\text{parallel}}(p)\) is the execution time of the parallel implementation using \(p\) threads.
- \(p\) is the number of OpenMP threads.

For the eight-thread configuration:

$$
S(8)=
\frac{0.906195}{0.336241}
\approx 2.70
$$

This indicates approximately **2.70x speedup** compared with the sequential implementation.

### Parallel Efficiency

Parallel efficiency measures how effectively the available threads are utilized.

$$
E(p)=\frac{S(p)}{p}\times 100\%
$$

For eight threads:

$$
E(8)=\frac{2.70}{8}\times 100
\approx 33.75\%
$$

These are preliminary measurements, not definitive hardware performance results. Runtime variations can occur due to CPU scheduling, clock frequency, thermal conditions, and background processes.

The live visualization runtime is not directly comparable to these benchmarks because streaming coordinates and flushing output introduce additional overhead.

## Validation

The simulation includes a momentum conservation check.

### Total Linear Momentum

The total linear momentum of the particle system is calculated as:

$$
\vec{P}=
\sum_{i=1}^{N}m_i\vec{v}_i
$$

Where:

- \(m_i\) is the mass of particle \(i\).
- \(\vec{v}_i\) is the velocity vector of particle \(i\).
- \(N\) is the total number of particles.

### Momentum Conservation Check

Momentum conservation is checked by comparing the initial and final total momentum:

$$
\Delta P=
\left\|
\vec{P}_{\text{final}}
-
\vec{P}_{\text{initial}}
\right\|
$$

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
