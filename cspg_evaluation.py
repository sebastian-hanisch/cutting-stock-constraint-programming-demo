"""Kennzahlen aus einem Suchlauf, plus der Kern-Vergleich dieses Stücks: derselbe
Suchlauf auf DERSELBEN Instanz, einmal ohne (Baseline mit verschwendeten
prune_infeasible-Knoten), einmal mit aktiver Materialsorten-Propagation."""

from collections import Counter

from cspg_constants import MAX_NODES_EXPLORED
from cspg_solver import solve


def compute_stats(result):
    counts = Counter(node.status for node in result.nodes)
    return {
        "nodes_explored": len(result.nodes),
        "pruned_bound": counts["prune_bound"],
        "pruned_infeasible": counts["prune_infeasible"],
        "leaves_evaluated": counts["leaf_new_best"] + counts["leaf_not_best"],
        "grade_excluded_total": sum(n.grade_excluded for n in result.nodes),
        "best_value": result.best_value,
        "truncated": result.truncated,
    }


def stats_up_to_step(result, step):
    relevant = [node for node in result.nodes if node.id <= step]
    counts = Counter(node.status for node in relevant)
    current_best = None
    for nid, v in result.incumbent_history:
        if nid <= step:
            current_best = v
    return {
        "nodes_so_far": counts.total(),
        "pruned_bound": counts["prune_bound"],
        "grade_excluded_so_far": sum(n.grade_excluded for n in relevant),
        "current_best": current_best,
    }


def propagation_comparison(instance, max_nodes=MAX_NODES_EXPLORED):
    baseline = solve(instance, use_propagation=False, max_nodes=max_nodes)
    propagated = solve(instance, use_propagation=True, max_nodes=max_nodes)
    baseline_counts = Counter(node.status for node in baseline.nodes)
    return {
        "baseline_nodes": len(baseline.nodes),
        "baseline_wasted": baseline_counts["prune_infeasible"],
        "baseline_best": baseline.best_value,
        "baseline_truncated": baseline.truncated,
        "propagation_nodes": len(propagated.nodes),
        "propagation_excluded": sum(n.grade_excluded for n in propagated.nodes),
        "propagation_best": propagated.best_value,
        "propagation_truncated": propagated.truncated,
    }
