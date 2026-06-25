"""
Campus environment: patrol nodes, buildings, charging pads.
"""

import numpy as np
from .config import *


def point_in_building(x, y):
    """Check if point is inside any building."""
    for (bx, by, bw, bh) in BUILDINGS:
        if bx <= x <= bx + bw and by <= y <= by + bh:
            return True
    return False


def generate_patrol_nodes(seed=SEED):
    """Generate patrol node positions on jittered grid, avoiding buildings."""
    rng = np.random.default_rng(seed)
    nodes = []
    # Generate on a grid with jitter
    cols = 6
    rows = 5
    dx = CAMPUS_W / (cols + 1)
    dy = CAMPUS_H / (rows + 1)

    for i in range(1, cols + 1):
        for j in range(1, rows + 1):
            x = dx * i + rng.uniform(-30, 30)
            y = dy * j + rng.uniform(-30, 30)
            x = np.clip(x, 20, CAMPUS_W - 20)
            y = np.clip(y, 20, CAMPUS_H - 20)
            if not point_in_building(x, y):
                nodes.append([x, y])
            if len(nodes) >= N_PATROL_NODES:
                break
        if len(nodes) >= N_PATROL_NODES:
            break

    # Fill remaining if needed
    while len(nodes) < N_PATROL_NODES:
        x = rng.uniform(50, CAMPUS_W - 50)
        y = rng.uniform(50, CAMPUS_H - 50)
        if not point_in_building(x, y):
            nodes.append([x, y])

    return np.array(nodes[:N_PATROL_NODES])


def get_environment(seed=SEED):
    """Return full environment dict."""
    nodes = generate_patrol_nodes(seed)
    return {
        'nodes': nodes,
        'buildings': BUILDINGS,
        'pads': CHARGING_PADS,
        'campus_size': (CAMPUS_W, CAMPUS_H),
    }