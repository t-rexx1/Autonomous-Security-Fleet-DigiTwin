"""
Main simulation runner — GA optimization + fleet simulation + visualization.
Run from repo root: python -m src.main_simulation
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import *
from src.environment import get_environment
from src.fleet_model import Fleet
from src.coverage_model import CoverageGrid
from src.genetic_algorithm import GA
from src.fitness import decode_routes
from src.visualization import (
    plot_coverage_heatmap, plot_routes, plot_convergence,
    plot_battery_history, plot_coverage_over_time
)


def run():
    print("=" * 60)
    print("  KNIGHTSCOPE FLEET DIGITAL TWIN")
    print("  GA-Optimized Patrol Route Allocation")
    print("=" * 60)

    # ─── Setup ─────────────────────────────────────────────
    env = get_environment()
    nodes = env['nodes']
    pads = env['pads']
    buildings = env['buildings']

    print(f"\n[ENV] Campus: {CAMPUS_W}x{CAMPUS_H}m | Nodes: {len(nodes)} | Pads: {len(pads)}")
    print(f"[FLEET] Units: {N_UNITS} | Speed: {V_MAX} m/s | Battery: {E_MAX}%")

    # ─── Phase 1: GA Optimization ─────────────────────────
    print(f"\n[GA] Running {N_GENERATIONS} generations, pop={POP_SIZE}...")
    ga = GA(nodes, N_UNITS, seed=SEED)
    best_chrom, best_cost = ga.run(N_GENERATIONS)
    print(f"[GA] Best cost: {best_cost:.1f}")

    routes = ga.get_best_routes()
    for i, r in enumerate(routes):
        print(f"  Unit {i+1}: {len(r)} nodes")

    # ─── Phase 2: Forward Simulation ──────────────────────────
    print(f"\n[SIM] Simulating {SIM_DURATION}s with disruption at t={DISRUPT_TIME}s...")

    start_positions = [pads[i % len(pads)] for i in range(N_UNITS)]
    fleet = Fleet(N_UNITS, start_positions)
    fleet.assign_routes(routes)

    coverage_grid = CoverageGrid()
    coverage_history = []
    battery_history = [[] for _ in range(N_UNITS)]
    frames = []  # for animation
    disrupted = False
    disrupt_step = int(DISRUPT_TIME / SIM_DT)

    n_steps = int(SIM_DURATION / SIM_DT)

    for step in range(n_steps):
        # Disruption event
        if step == disrupt_step and not disrupted:
            print(f"  [!] Disruption at t={DISRUPT_TIME}s — Unit {DISRUPT_UNIT+1} offline")
            fleet.disable_unit(DISRUPT_UNIT)
            disrupted = True

            active_units = sum(1 for u in fleet.units if u.active)
            print(f"  [GA] Re-optimizing for {active_units} units...")
            ga2 = GA(nodes, active_units, seed=SEED + 1)
            ga2.run(N_GEN_RECOVERY)
            new_routes = ga2.get_best_routes()

            route_idx = 0
            for unit in fleet.units:
                if unit.active:
                    unit.route = new_routes[route_idx]
                    unit.route_idx = 0
                    route_idx += 1

            ga.fitness_history.extend(ga2.fitness_history)

        # Step fleet
        fleet.step(nodes, pads, SIM_DT)

        # Stamp coverage
        active_positions = [u.pos for u in fleet.units if u.active]
        if active_positions:
            coverage_grid.stamp(np.array(active_positions))
        coverage_grid.decay(SIM_DT)

        # Record
        coverage_history.append(coverage_grid.get_coverage_pct())
        for i, unit in enumerate(fleet.units):
            battery_history[i].append(unit.battery)

        # Capture frame every 10 steps
        if step % 10 == 0:
            frames.append(coverage_grid.grid.copy())

    final_coverage = coverage_history[-1]
    print(f"\n[RESULT] Final coverage: {final_coverage*100:.1f}%")
    print(f"[RESULT] Blind spots: {(1-final_coverage)*100:.1f}%")

    # ─── Phase 3: Generate Plots ──────────────────────────
    print("\n[VIZ] Generating plots...")
    os.makedirs('results/figures', exist_ok=True)

    plot_coverage_heatmap(coverage_grid, buildings,
                         title=f"Coverage Heatmap (t={SIM_DURATION}s) — {final_coverage*100:.0f}% Covered",
                         save_path='results/figures/coverage_heatmap_final.png')

    plot_routes(nodes, routes, buildings, pads,
               title="GA-Optimized Patrol Routes (Pre-Disruption)",
               save_path='results/figures/patrol_routes.png')

    plot_convergence(ga.fitness_history,
                    disrupt_gen=N_GENERATIONS,
                    title="GA Convergence — Fitness vs Generation",
                    save_path='results/figures/ga_convergence.png')

    plot_battery_history(battery_history,
                        disrupt_time=DISRUPT_TIME,
                        save_path='results/figures/battery_soc.png')

    plot_coverage_over_time(coverage_history,
                           disrupt_time=DISRUPT_TIME,
                           save_path='results/figures/coverage_over_time.png')

    print("[VIZ] All plots saved to results/figures/")
    print("\n" + "=" * 60)
    print("  DONE")
    print("=" * 60)
    # Animation
    from src.visualization import generate_animation
    generate_animation(frames, buildings, save_path='results/animations/coverage_evolution.gif')


if __name__ == '__main__':
    run()