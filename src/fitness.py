"""
Multi-objective fitness function for GA evaluation.
"""

import numpy as np
from .config import *


def route_length(route, nodes):
    """Total loop distance for a cyclic route."""
    if len(route) < 2:
        return 0.0
    dist = 0.0
    for i in range(len(route)):
        j = (i + 1) % len(route)
        dist += np.linalg.norm(nodes[route[i]] - nodes[route[j]])
    return dist


def evaluate_fitness(chromosome, nodes, n_units):
    """
    Evaluate cost Π(Λ) for a chromosome.
    
    chromosome = (permutation, breaks)
    Returns: cost (lower is better)
    """
    perm, breaks = chromosome

    # Decode routes
    routes = decode_routes(perm, breaks, n_units)

    # Compute route lengths
    lengths = np.array([route_length(r, nodes) for r in routes])

    # Cost components
    c_makespan = np.max(lengths) if len(lengths) > 0 else 0
    c_total = np.sum(lengths)
    c_balance = np.std(lengths) if len(lengths) > 1 else 0

    # Energy infeasibility
    c_energy = 0.0
    for l in lengths:
        if l > D_MAX:
            c_energy += (l - D_MAX) ** 2

    # Empty route penalty
    n_empty = sum(1 for r in routes if len(r) == 0)
    c_empty = n_empty

    # Total cost
    cost = (W_MAKESPAN * c_makespan +
            W_TOTAL * c_total +
            W_BALANCE * c_balance +
            W_ENERGY * c_energy +
            W_EMPTY * c_empty)

    return cost


def decode_routes(perm, breaks, n_units):
    """Split permutation into per-unit routes using break indices."""
    routes = []
    sorted_breaks = sorted(breaks)
    indices = [0] + sorted_breaks + [len(perm)]

    for i in range(len(indices) - 1):
        route = list(perm[indices[i]:indices[i + 1]])
        routes.append(route)

    # Pad or trim to n_units
    while len(routes) < n_units:
        routes.append([])
    routes = routes[:n_units]

    return routes