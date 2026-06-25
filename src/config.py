"""
Knightscope Fleet Digital Twin --> Configuration
All system parameters (Λ) in one place.
Author: Aaditya Shrivastava
"""

import numpy as np

# Environment
CAMPUS_W = 800.0  # m
CAMPUS_H = 500.0  # m
N_PATROL_NODES = 27
N_CHARGING_PADS = 2

# Buildings: (x, y, width, height)
BUILDINGS = [
    (150, 100, 80, 60),
    (400, 200, 100, 80),
    (600, 350, 70, 50),
    (250, 350, 90, 70),
    (550, 80, 60, 60),
]

# Charging pad locations
CHARGING_PADS = np.array([
    [100.0, 250.0],
    [700.0, 250.0],
])

# ─── Fleet / Robot Specs ───────────────────────────────────
N_UNITS = 5
V_MAX = 1.5           # m/s (~3.4 mph, K5 spec)
E_MAX = 100.0         # % battery capacity
E_DRAIN_MOVE = 1.5    # %/min while moving
E_DRAIN_IDLE = 0.3    # %/min while idle
E_CHARGE_RATE = 5.0   # %/min at pad
E_THRESH = 22.0       # % --> divert to charger
R_SENSE = 25.0        # m sensor/coverage radius

# ─── Coverage Grid ─────────────────────────────────────────
GRID_RES = 8.0        # m per cell
DECAY_RATE = 0.03     # freshness decay per second
F_THRESH = 0.30       # below this = blind spot
F_STAMP = 1.0         # freshness set when unit passes

# ─── GA Parameters ─────────────────────────────────────────
POP_SIZE = 64
N_GENERATIONS = 200
P_CROSSOVER = 0.85
P_MUTATION = 0.15
P_BREAK_MUTATE = 0.20
TOURNAMENT_K = 3
N_ELITE = 2

# ─── Fitness Weights ──────────────────────────────────────
W_MAKESPAN = 1.0
W_TOTAL = 0.35
W_BALANCE = 1.1
W_ENERGY = 0.9
W_EMPTY = 1200.0

# ─── Simulation ───────────────────────────────────────────
SIM_DURATION = 600.0    # seconds to simulate per evaluation
SIM_DT = 1.0           # timestep (s)
D_MAX = 2600.0         # max route length on single charge (m)

# ─── Disruption ───────────────────────────────────────────
DISRUPT_TIME = 300.0   # second at which a unit drops
DISRUPT_UNIT = 2       # index of unit to drop
N_GEN_RECOVERY = 50    # GA generations for re-optimization

# ─── Random Seed ──────────────────────────────────────────
SEED = 42