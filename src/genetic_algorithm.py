"""
Genetic Algorithm engine: Prof Zohdi-style GA for fleet route optimization.
"""

import numpy as np
from .config import *
from .fitness import evaluate_fitness, decode_routes


class GA:
    """GA optimizer for fleet patrol routing."""

    def __init__(self, nodes, n_units, seed=SEED):
        self.nodes = nodes
        self.n_nodes = len(nodes)
        self.n_units = n_units
        self.rng = np.random.default_rng(seed)
        self.population = []
        self.fitness_history = []
        self.best_fitness = np.inf
        self.best_chromosome = None
        self._init_population()

    def _init_population(self):
        """Random initialization."""
        self.population = []
        for _ in range(POP_SIZE):
            perm = self.rng.permutation(self.n_nodes)
            breaks = sorted(self.rng.choice(
                range(1, self.n_nodes), size=self.n_units - 1, replace=False
            ))
            self.population.append((perm, breaks))

    def _evaluate_all(self):
        """Evaluate fitness for entire population."""
        costs = []
        for chrom in self.population:
            c = evaluate_fitness(chrom, self.nodes, self.n_units)
            costs.append(c)
        return np.array(costs)

    def _tournament_select(self, costs):
        """Tournament selection."""
        indices = self.rng.choice(POP_SIZE, size=TOURNAMENT_K, replace=False)
        best_idx = indices[np.argmin(costs[indices])]
        return self.population[best_idx]

    def _ordered_crossover(self, p1_perm, p2_perm):
        """OX crossover on permutation."""
        size = len(p1_perm)
        a, b = sorted(self.rng.choice(size, 2, replace=False))
        child = np.full(size, -1, dtype=int)
        child[a:b] = p1_perm[a:b]
        fill_vals = [v for v in p2_perm if v not in child[a:b]]
        idx = 0
        for i in range(size):
            if child[i] == -1:
                child[i] = fill_vals[idx]
                idx += 1
        return child

    def _mutate_perm(self, perm):
        """Swap mutation on permutation."""
        if self.rng.random() < P_MUTATION:
            i, j = self.rng.choice(len(perm), 2, replace=False)
            perm[i], perm[j] = perm[j], perm[i]
        return perm

    def _mutate_breaks(self, breaks):
        """Mutate break points."""
        if self.rng.random() < P_BREAK_MUTATE:
            idx = self.rng.integers(len(breaks))
            breaks[idx] = self.rng.integers(1, self.n_nodes)
        return sorted(list(set(breaks)))[:self.n_units - 1]

    def evolve_one_generation(self):
        """Run one generation of GA."""
        costs = self._evaluate_all()

        # Track best
        best_idx = np.argmin(costs)
        if costs[best_idx] < self.best_fitness:
            self.best_fitness = costs[best_idx]
            self.best_chromosome = self.population[best_idx]
        self.fitness_history.append(self.best_fitness)

        # Elitism
        elite_indices = np.argsort(costs)[:N_ELITE]
        new_pop = [self.population[i] for i in elite_indices]

        # Breed
        while len(new_pop) < POP_SIZE:
            p1 = self._tournament_select(costs)
            p2 = self._tournament_select(costs)

            if self.rng.random() < P_CROSSOVER:
                child_perm = self._ordered_crossover(p1[0], p2[0])
            else:
                child_perm = p1[0].copy()

            child_perm = self._mutate_perm(child_perm)

            # Breaks: inherit from p1, mutate
            child_breaks = list(p1[1]).copy()
            # Ensure correct number of breaks
            while len(child_breaks) < self.n_units - 1:
                child_breaks.append(self.rng.integers(1, self.n_nodes))
            child_breaks = self._mutate_breaks(child_breaks)

            new_pop.append((child_perm, child_breaks))

        self.population = new_pop[:POP_SIZE]

    def run(self, n_gen=N_GENERATIONS):
        """Run full GA optimization."""
        for _ in range(n_gen):
            self.evolve_one_generation()
        return self.best_chromosome, self.best_fitness

    def get_best_routes(self):
        """Decode best chromosome into routes."""
        if self.best_chromosome is None:
            return [[] for _ in range(self.n_units)]
        perm, breaks = self.best_chromosome
        return decode_routes(perm, breaks, self.n_units)