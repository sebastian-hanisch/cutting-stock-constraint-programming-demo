"""Schranke für die Bin-Packing-Suche, identisch zu csbb_bounds.weak_bound aus
cutting-stock-branch-bound-demo. Die Materialsorten-Regel dieses Stücks wirkt
über Propagation (siehe cspg_solver.py), nicht über eine geänderte Schranke."""


def weak_bound(instance, pieces, depth, bins):
    remaining_width = sum(p[0] for p in pieces[depth:])
    remaining_capacity = sum(cap for cap, _ in bins)
    if remaining_width <= remaining_capacity:
        return len(bins)
    extra = -(-(remaining_width - remaining_capacity) // instance.roll_width)
    return len(bins) + extra
