"""
Coverage freshness grid — tracks how recently each cell was patrolled..
"""

import numpy as np
from .config import *


class CoverageGrid:
    """Spatial freshness grid for coverage tracking."""

    def __init__(self):
        self.cols = int(CAMPUS_W / GRID_RES)
        self.rows = int(CAMPUS_H / GRID_RES)
        self.grid = np.zeros((self.rows, self.cols))
        self.building_mask = self._make_building_mask()

    def _make_building_mask(self):
        """True where buildings are (non-patrollable)."""
        mask = np.zeros((self.rows, self.cols), dtype=bool)
        for (bx, by, bw, bh) in BUILDINGS:
            c0 = int(bx / GRID_RES)
            c1 = int((bx + bw) / GRID_RES)
            r0 = int(by / GRID_RES)
            r1 = int((by + bh) / GRID_RES)
            mask[r0:r1, c0:c1] = True
        return mask

    def stamp(self, positions, radius=R_SENSE):
        """Stamp freshness around unit positions."""
        r_cells = int(radius / GRID_RES)
        for pos in positions:
            c = int(pos[0] / GRID_RES)
            r = int(pos[1] / GRID_RES)
            for dr in range(-r_cells, r_cells + 1):
                for dc in range(-r_cells, r_cells + 1):
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < self.rows and 0 <= cc < self.cols:
                        if abs(dr) + abs(dc) <= r_cells:
                            if not self.building_mask[rr, cc]:
                                self.grid[rr, cc] = F_STAMP

    def decay(self, dt=SIM_DT):
        """Decay freshness over time."""
        self.grid -= DECAY_RATE * dt
        self.grid = np.clip(self.grid, 0, 1)

    def get_coverage_pct(self):
        """Fraction of non-building cells above threshold."""
        valid = ~self.building_mask
        n_valid = np.sum(valid)
        if n_valid == 0:
            return 1.0
        n_covered = np.sum(self.grid[valid] > F_THRESH)
        return n_covered / n_valid

    def get_blind_spot_pct(self):
        """Fraction that are blind spots."""
        return 1.0 - self.get_coverage_pct()

    def reset(self):
        """Reset grid to zero."""
        self.grid = np.zeros((self.rows, self.cols))
