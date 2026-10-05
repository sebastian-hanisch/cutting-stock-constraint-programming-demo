"""Unabhängiges Orakel: Mengenüberdeckungs-DP über alle Teilmengen. Eine Teilmenge ist als Rolle zulässig,
wenn ihre Breitensumme <= W UND JEDES Paar ihrer Sorten |g1 - g2| <= 1 erfüllt (direkt aus der Regel,
ohne `grade_compatible`/`add_grade` und ohne den Pfadgraph-Zustand aus dem Solver). Dazu zwei Kennzahl-
Invarianten: Baseline-Knoten = propagierte Knoten + verschwendete Knoten, und die per Propagation
ausgeschlossenen Bins entsprechen genau den verschwendeten Baseline-Knoten."""

import random

from cspg_evaluation import compute_stats
from cspg_scenario import CuttingStockInstance, expand_pieces
from cspg_solver import solve


def _min_rolls(pieces, width):
    n = len(pieces)
    if n == 0:
        return 0
    feasible = [False] * (1 << n)
    for mask in range(1, 1 << n):
        idx = [i for i in range(n) if mask >> i & 1]
        if sum(pieces[i][0] for i in idx) <= width and all(
            abs(pieces[i][1] - pieces[j][1]) <= 1 for i in idx for j in idx
        ):
            feasible[mask] = True
    best = [99] * (1 << n)
    best[0] = 0
    for mask in range(1, 1 << n):
        low = mask & -mask
        rest = mask ^ low
        sub = rest
        while True:
            cand = sub | low
            if feasible[cand] and best[mask ^ cand] + 1 < best[mask]:
                best[mask] = best[mask ^ cand] + 1
            if sub == 0:
                break
            sub = (sub - 1) & rest
    return best[-1]


def _random_instance(rng):
    width = rng.choice([10, 20, 37, 50, 100])
    n_types = rng.randint(1, 4)
    widths = tuple(rng.randint(max(1, round(0.1 * width)), max(2, round(0.7 * width))) for _ in range(n_types))
    demands = tuple(rng.randint(1, 3) for _ in range(n_types))
    n_grades = rng.randint(1, 4)
    grades = tuple(rng.randint(1, n_grades) for _ in range(n_types))
    return CuttingStockInstance(width, widths, demands, grades, n_grades)


def test_both_modes_match_subset_dp_and_counters_are_consistent():
    rng = random.Random(17)
    checked = excluded_seen = 0
    while checked < 60:
        inst = _random_instance(rng)
        pieces = expand_pieces(inst)
        if len(pieces) > 9:
            continue
        checked += 1
        optimum = _min_rolls(pieces, inst.roll_width)
        propagated, baseline = solve(inst, use_propagation=True), solve(inst, use_propagation=False)
        assert propagated.best_value == baseline.best_value == optimum, inst
        sp, sb = compute_stats(propagated), compute_stats(baseline)
        assert sp["pruned_infeasible"] == 0
        assert len(baseline.nodes) == len(propagated.nodes) + sb["pruned_infeasible"], inst
        assert sp["grade_excluded_total"] == sb["pruned_infeasible"], inst
        for cap, grades in propagated.best_bins:
            assert len(grades) <= 2 and (len(grades) < 2 or abs(grades[0] - grades[1]) <= 1)
        excluded_seen += sp["grade_excluded_total"] > 0
    assert excluded_seen > 0


def test_hand_example():
    # W=10: (6,g1)+(4,g1) teilen sich eine Rolle, (4,g3) ist mit g1 unverträglich -> 2 Rollen
    inst = CuttingStockInstance(10, (6, 4, 4), (1, 1, 1), (1, 3, 1), 3)
    assert _min_rolls(expand_pieces(inst), 10) == 2
    assert solve(inst).best_value == 2
