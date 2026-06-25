"""
Fleet dynamics: movement, battery, charging logic.
"""

import numpy as np
from .config import *


class Unit:
    """Single ASR unit."""

    def __init__(self, uid, start_pos):
        self.uid = uid
        self.pos = np.array(start_pos, dtype=float)
        self.battery = E_MAX
        self.route = []          # list of node indices
        self.route_idx = 0       # current target in route
        self.charging = False
        self.active = True
        self.state = 'patrol'    # 'patrol', 'to_pad', 'charging'

    def step(self, nodes, pads, dt=SIM_DT):
        """Advance one timestep."""
        if not self.active:
            return

        if self.state == 'charging':
            self.battery = min(E_MAX, self.battery + E_CHARGE_RATE * (dt / 60.0))
            if self.battery >= E_MAX:
                self.state = 'patrol'
            return

        # Check if need to charge
        if self.battery <= E_THRESH and self.state != 'to_pad':
            self.state = 'to_pad'

        # Determine target
        if self.state == 'to_pad':
            # Go to nearest pad
            dists = np.linalg.norm(pads - self.pos, axis=1)
            target = pads[np.argmin(dists)]
        elif len(self.route) > 0:
            target = nodes[self.route[self.route_idx % len(self.route)]]
        else:
            # No route assigned, idle
            self.battery -= E_DRAIN_IDLE * (dt / 60.0)
            return

        # Move toward target
        diff = target - self.pos
        dist = np.linalg.norm(diff)
        step_dist = V_MAX * dt

        if dist <= step_dist:
            self.pos = target.copy()
            if self.state == 'to_pad':
                self.state = 'charging'
            elif self.state == 'patrol':
                self.route_idx = (self.route_idx + 1) % len(self.route)
        else:
            self.pos += (diff / dist) * step_dist

        # Drain battery
        self.battery -= E_DRAIN_MOVE * (dt / 60.0)
        self.battery = max(0, self.battery)


class Fleet:
    """Fleet of ASR units."""

    def __init__(self, n_units, start_positions):
        self.units = []
        for i in range(n_units):
            pos = start_positions[i % len(start_positions)]
            self.units.append(Unit(i, pos))

    def assign_routes(self, route_assignments):
        """route_assignments: list of lists of node indices per unit."""
        for i, unit in enumerate(self.units):
            if unit.active and i < len(route_assignments):
                unit.route = route_assignments[i]
                unit.route_idx = 0

    def step(self, nodes, pads, dt=SIM_DT):
        """Step all units."""
        for unit in self.units:
            unit.step(nodes, pads, dt)

    def get_positions(self):
        """Return positions of active units."""
        return np.array([u.pos for u in self.units if u.active])

    def disable_unit(self, idx):
        """Simulate unit going offline."""
        self.units[idx].active = False