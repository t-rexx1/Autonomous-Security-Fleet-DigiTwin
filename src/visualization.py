"""
Visualization: heatmaps, convergence plots, route maps.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
from .config import *


# Custom colormap: red (blind) → amber → cyan (fresh)
CMAP_COVERAGE = LinearSegmentedColormap.from_list(
    'coverage', ['#FF5470', '#F5A623', '#00E5C8']
)

COLORS_UNITS = ['#00E5C8', '#F5A623', '#FF5470', '#8B5CF6', '#3B82F6']


def plot_coverage_heatmap(grid, buildings, title="Coverage Heatmap", save_path=None):
    """Plot coverage freshness grid."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 6), facecolor='#080B11')
    ax.set_facecolor('#080B11')

    im = ax.imshow(grid.grid, origin='lower', cmap=CMAP_COVERAGE,
                   vmin=0, vmax=1, aspect='auto',
                   extent=[0, CAMPUS_W, 0, CAMPUS_H])

    # Buildings
    for (bx, by, bw, bh) in buildings:
        rect = patches.Rectangle((bx, by), bw, bh,
                                  facecolor='#1a1f2e', edgecolor='#5E7187', lw=1)
        ax.add_patch(rect)

    ax.set_title(title, color='#CBD8E8', fontsize=14, fontfamily='monospace')
    ax.set_xlabel('X (m)', color='#5E7187')
    ax.set_ylabel('Y (m)', color='#5E7187')
    ax.tick_params(colors='#5E7187')

    cbar = plt.colorbar(im, ax=ax, fraction=0.03)
    cbar.set_label('Freshness', color='#CBD8E8')
    cbar.ax.tick_params(colors='#5E7187')

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, facecolor='#080B11', bbox_inches='tight')
    plt.close()


def plot_routes(nodes, routes, buildings, pads, title="Patrol Routes", save_path=None):
    """Plot assigned routes on campus map."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 6), facecolor='#080B11')
    ax.set_facecolor('#080B11')

    # Buildings
    for (bx, by, bw, bh) in buildings:
        rect = patches.Rectangle((bx, by), bw, bh,
                                  facecolor='#1a1f2e', edgecolor='#5E7187', lw=1)
        ax.add_patch(rect)

    # Charging pads
    ax.scatter(pads[:, 0], pads[:, 1], marker='s', s=120,
              c='#F5A623', zorder=5, label='Charging Pads')

    # Routes
    for i, route in enumerate(routes):
        if len(route) < 2:
            continue
        color = COLORS_UNITS[i % len(COLORS_UNITS)]
        route_pts = nodes[route + [route[0]]]  # close the loop
        ax.plot(route_pts[:, 0], route_pts[:, 1], '-o',
                color=color, markersize=4, lw=1.5, alpha=0.8,
                label=f'Unit {i+1}')

    # All nodes
    ax.scatter(nodes[:, 0], nodes[:, 1], c='#CBD8E8', s=20, zorder=4, alpha=0.5)

    ax.set_xlim(0, CAMPUS_W)
    ax.set_ylim(0, CAMPUS_H)
    ax.set_title(title, color='#CBD8E8', fontsize=14, fontfamily='monospace')
    ax.legend(loc='upper right', facecolor='#0d1117', edgecolor='#5E7187',
              labelcolor='#CBD8E8', fontsize=8)
    ax.tick_params(colors='#5E7187')

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, facecolor='#080B11', bbox_inches='tight')
    plt.close()


def plot_convergence(fitness_history, disrupt_gen=None, title="GA Convergence", save_path=None):
    """Plot fitness vs generation."""
    fig, ax = plt.subplots(1, 1, figsize=(8, 5), facecolor='#080B11')
    ax.set_facecolor('#080B11')

    ax.plot(fitness_history, color='#00E5C8', lw=2)

    if disrupt_gen is not None:
        ax.axvline(disrupt_gen, color='#FF5470', ls='--', lw=1.5, label='Unit Disrupted')
        ax.legend(facecolor='#0d1117', edgecolor='#5E7187', labelcolor='#CBD8E8')

    ax.set_xlabel('Generation', color='#5E7187')
    ax.set_ylabel('Cost Π(Λ)', color='#5E7187')
    ax.set_title(title, color='#CBD8E8', fontsize=14, fontfamily='monospace')
    ax.tick_params(colors='#5E7187')
    ax.grid(True, alpha=0.15, color='#5E7187')

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, facecolor='#080B11', bbox_inches='tight')
    plt.close()


def plot_battery_history(battery_history, disrupt_time=None, save_path=None):
    """Plot battery SOC over time for each unit."""
    fig, ax = plt.subplots(1, 1, figsize=(8, 5), facecolor='#080B11')
    ax.set_facecolor('#080B11')

    for i, hist in enumerate(battery_history):
        color = COLORS_UNITS[i % len(COLORS_UNITS)]
        ax.plot(hist, color=color, lw=1.5, alpha=0.8, label=f'Unit {i+1}')

    ax.axhline(E_THRESH, color='#FF5470', ls=':', lw=1, alpha=0.7, label='Charge Threshold')

    if disrupt_time:
        ax.axvline(disrupt_time, color='#FF5470', ls='--', lw=1.5)

    ax.set_xlabel('Time (s)', color='#5E7187')
    ax.set_ylabel('Battery %', color='#5E7187')
    ax.set_title('Battery State of Charge', color='#CBD8E8', fontsize=14, fontfamily='monospace')
    ax.legend(facecolor='#0d1117', edgecolor='#5E7187', labelcolor='#CBD8E8', fontsize=8)
    ax.tick_params(colors='#5E7187')
    ax.grid(True, alpha=0.15, color='#5E7187')
    ax.set_ylim(0, 105)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, facecolor='#080B11', bbox_inches='tight')
    plt.close()


def plot_coverage_over_time(coverage_history, disrupt_time=None, save_path=None):
    """Plot coverage % over simulation time."""
    fig, ax = plt.subplots(1, 1, figsize=(8, 5), facecolor='#080B11')
    ax.set_facecolor('#080B11')

    ax.plot(coverage_history, color='#00E5C8', lw=2)
    ax.fill_between(range(len(coverage_history)), coverage_history,
                    alpha=0.15, color='#00E5C8')

    if disrupt_time:
        ax.axvline(disrupt_time, color='#FF5470', ls='--', lw=1.5, label='Unit Disrupted')
        ax.legend(facecolor='#0d1117', edgecolor='#5E7187', labelcolor='#CBD8E8')

    ax.set_xlabel('Time (s)', color='#5E7187')
    ax.set_ylabel('Coverage %', color='#5E7187')
    ax.set_title('Fleet Coverage Over Time', color='#CBD8E8', fontsize=14, fontfamily='monospace')
    ax.tick_params(colors='#5E7187')
    ax.grid(True, alpha=0.15, color='#5E7187')
    ax.set_ylim(0, 1.0)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, facecolor='#080B11', bbox_inches='tight')
    plt.close()
def generate_animation(frames_data, buildings, save_path='results/animations/coverage_evolution.gif'):
    """Generate animated GIF of coverage evolution."""
    import matplotlib.animation as animation
    
    fig, ax = plt.subplots(1, 1, figsize=(10, 6), facecolor='#080B11')
    ax.set_facecolor('#080B11')
    
    # Buildings
    for (bx, by, bw, bh) in buildings:
        rect = patches.Rectangle((bx, by), bw, bh,
                                  facecolor='#1a1f2e', edgecolor='#5E7187', lw=1)
        ax.add_patch(rect)
    
    im = ax.imshow(frames_data[0], origin='lower', cmap=CMAP_COVERAGE,
                   vmin=0, vmax=1, aspect='auto',
                   extent=[0, CAMPUS_W, 0, CAMPUS_H])
    
    title = ax.set_title('', color='#CBD8E8', fontsize=14, fontfamily='monospace')
    ax.set_xlabel('X (m)', color='#5E7187')
    ax.set_ylabel('Y (m)', color='#5E7187')
    ax.tick_params(colors='#5E7187')
    
    def update(frame_idx):
        im.set_data(frames_data[frame_idx])
        t = frame_idx * 10  # assuming we save every 10 steps
        title.set_text(f'Coverage Evolution — t={t}s')
        return [im, title]
    
    anim = animation.FuncAnimation(fig, update, frames=len(frames_data),
                                    interval=100, blit=True)
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    anim.save(save_path, writer='pillow', fps=10, dpi=100,
              savefig_kwargs={'facecolor': '#080B11'})
    plt.close()
    print(f"[VIZ] Animation saved: {save_path}")
    