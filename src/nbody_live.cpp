#include <omp.h>

#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <fstream>
#include <chrono>
#include <iomanip>
#include <atomic>
#include <thread>
#include <string>
using namespace std;

// Simulation parameters
const int N = 500;
const int ITERATIONS = 500;

const double G = 1.0;
const double DT = 0.01;
const double SOFTENING = 0.1;

atomic<bool> paused(true);
atomic<bool> reset_requested(false);
atomic<bool> stop_requested(false);

struct Particle {
    double x, y, z;

    double vx, vy, vz;

    double ax, ay, az;

    double mass;
};

void initialize(vector<Particle>& particles) {

    mt19937 generator(42);

    uniform_real_distribution<double> position(-5.0, 5.0);
    uniform_real_distribution<double> velocity(-0.1, 0.1);

    for (int i = 0; i < N; i++) {

        Particle p;

        p.x = position(generator);
        p.y = position(generator);
        p.z = position(generator);

        p.vx = velocity(generator);
        p.vy = velocity(generator);
        p.vz = velocity(generator);

        p.ax = 0.0;
        p.ay = 0.0;
        p.az = 0.0;

        p.mass = 1.0 / N;

        particles[i] = p;
    }
}

void calculate_forces(vector<Particle>& particles) {

    #pragma omp parallel for schedule(static)
    for (int i = 0; i < N; i++) {

        double ax = 0.0;
        double ay = 0.0;
        double az = 0.0;

        for (int j = 0; j < N; j++) {

            if (i == j)
                continue;

            double dx = particles[j].x - particles[i].x;
            double dy = particles[j].y - particles[i].y;
            double dz = particles[j].z - particles[i].z;

            double distance_squared =
                dx * dx + dy * dy + dz * dz
                + SOFTENING * SOFTENING;

            double distance_cubed =
                distance_squared * sqrt(distance_squared);

            double force_factor =
                G * particles[j].mass / distance_cubed;

            ax += force_factor * dx;
            ay += force_factor * dy;
            az += force_factor * dz;
        }

        particles[i].ax = ax;
        particles[i].ay = ay;
        particles[i].az = az;
    }
}

void update_particles(vector<Particle>& particles) {

    #pragma omp parallel for schedule(static)
    for (int i = 0; i < N; i++) {

        particles[i].vx += particles[i].ax * DT;
        particles[i].vy += particles[i].ay * DT;
        particles[i].vz += particles[i].az * DT;

        particles[i].x += particles[i].vx * DT;
        particles[i].y += particles[i].vy * DT;
        particles[i].z += particles[i].vz * DT;
    }
}

struct Momentum {
    double px = 0.0;
    double py = 0.0;
    double pz = 0.0;
};

Momentum calculate_momentum(const vector<Particle>& particles) {

    Momentum total;

    for (int i = 0; i < N; i++) {

        total.px += particles[i].mass * particles[i].vx;
        total.py += particles[i].mass * particles[i].vy;
        total.pz += particles[i].mass * particles[i].vz;
    }

    return total;
}
// Save final particle positions
void save_results(const vector<Particle>& particles) {

    ofstream file("results/final_positions.csv");

    if (!file.is_open()) {
        cerr << "Error: Could not create output file!\n";
        return;
    }

    file << "x,y,z,mass\n";

    file << setprecision(10);

    for (const auto& p : particles) {
        file << p.x << ","
             << p.y << ","
             << p.z << ","
             << p.mass << "\n";
    }

    file.close();
}


// Main function

int main() {

    vector<Particle> particles(N);

    initialize(particles);

    Momentum initial_momentum =
        calculate_momentum(particles);

    cerr << "OpenMP threads: "
         << omp_get_max_threads() << "\n";

    cerr << "Waiting for simulation commands...\n";

    // Listen for commands from Python
    thread command_thread([]() {

        string command;

        while (cin >> command) {

            if (command == "PAUSE") {
                paused = true;
                cerr << "Simulation paused\n";
            }

            else if (command == "RESUME") {
                paused = false;
                cerr << "Simulation resumed\n";
            }

            else if (command == "RESET") {
                reset_requested = true;
                cerr << "Reset requested\n";
            }

            else if (command == "STOP") {
                stop_requested = true;
                break;
            }
        }
    });

    command_thread.detach();

    int step = 0;

    auto start = chrono::steady_clock::now();

    // Continuous simulation
    while (!stop_requested) {

        // Reset simulation
        if (reset_requested.exchange(false)) {

            initialize(particles);

            initial_momentum =
                calculate_momentum(particles);

            step = 0;
        }

        // Pause simulation
        if (paused) {

            this_thread::sleep_for(
                chrono::milliseconds(10)
            );

            continue;
        }

        calculate_forces(particles);
        update_particles(particles);

        // Stream positions to Python
        if (step % 2 == 0) {

            for (int i = 0; i < N; i++) {

                cout << particles[i].x << " "
                     << particles[i].y << " "
                     << particles[i].z << "\n";
            }

            cout << "END_FRAME\n";
            cout.flush();

            // Limit frame production rate
            this_thread::sleep_for(
                chrono::milliseconds(16)
            );
        }

        step++;
    }

    auto stop = chrono::steady_clock::now();

    Momentum final_momentum =
        calculate_momentum(particles);

    double runtime =
        chrono::duration<double>(stop - start).count();

    double dx = final_momentum.px - initial_momentum.px;
    double dy = final_momentum.py - initial_momentum.py;
    double dz = final_momentum.pz - initial_momentum.pz;

    double momentum_error =
        sqrt(dx*dx + dy*dy + dz*dz);

    cerr << "\nSimulation stopped\n";
    cerr << "Momentum difference: "
         << momentum_error << "\n";

    cerr << "Execution time: "
         << runtime << " seconds\n";

    save_results(particles);

    return 0;
}
