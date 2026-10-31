import numpy as np
import matplotlib.pyplot as plt

# Load simulation results
data = np.genfromtxt("results/final_positions.csv",delimiter=",",names=True)

x = data["x"]
y = data["y"]
z = data["z"]

# Create 3D plot
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection="3d")

scatter = ax.scatter(
    x, y, z,
    c=z,
    cmap="plasma",
    s=8,
    alpha=0.8
)

ax.set_title("3D N-Body Gravitational Simulation")
ax.set_xlabel("X Position")
ax.set_ylabel("Y Position")
ax.set_zlabel("Z Position")

fig.colorbar(scatter, ax=ax, label="Z Position", shrink=0.7)

plt.tight_layout()
plt.savefig("plots/nbody_3d.png", dpi=200)
plt.show()

print("Particles visualised:", len(x))
print("X range:", x.min(), "to", x.max())
print("Y range:", y.min(), "to", y.max())
print("Z range:", z.min(), "to", z.max())