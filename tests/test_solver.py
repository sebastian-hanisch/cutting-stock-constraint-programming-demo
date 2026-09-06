import pytest

from cspg_bruteforce import solve_bruteforce
from cspg_constants import PRESETS
from cspg_ortools_reference import solve_with_ortools
from cspg_scenario import CuttingStockInstance, expand_pieces, generate_instance
from cspg_solver import solve


def _check_solution_feasible(instance, result):
    pieces = expand_pieces(instance)
    assert sum(instance.roll_width - cap for cap, _ in result.best_bins) == sum(p[0] for p in pieces)
    for cap, _ in result.best_bins:
        assert 0 <= cap <= instance.roll_width


def test_matches_hand_computed_example():
    instance = CuttingStockInstance(
        roll_width=10, item_widths=(6,), item_demands=(3,), item_grades=(1,), n_grades=1,
    )
    result = solve(instance, use_propagation=True)
    assert result.best_value == 3
    assert solve_bruteforce(instance) == 3


@pytest.mark.parametrize("use_propagation", [True, False])
def test_matches_bruteforce_across_random_small_instances(use_propagation):
    for n_grades in range(2, 5):
        for seed in range(10):
            instance = generate_instance(n_types=3, roll_width=100, max_demand=2, n_grades=n_grades, seed=seed)
            result = solve(instance, use_propagation=use_propagation)
            true_min = solve_bruteforce(instance)
            assert result.best_value == true_min, f"n_grades={n_grades} seed={seed} use_propagation={use_propagation}"
            _check_solution_feasible(instance, result)


def test_propagation_never_changes_the_optimum():
    for n_types in range(2, 7):
        for max_demand in range(1, 4):
            for n_grades in range(2, 5):
                for seed in range(6):
                    instance = generate_instance(n_types, 100, max_demand, n_grades, seed)
                    with_prop = solve(instance, use_propagation=True, max_nodes=50_000)
                    without_prop = solve(instance, use_propagation=False, max_nodes=50_000)
                    if with_prop.truncated or without_prop.truncated:
                        continue
                    assert with_prop.best_value == without_prop.best_value, (
                        f"n={n_types} d={max_demand} g={n_grades} seed={seed}"
                    )


def test_grade_excluded_metric_is_nonzero_on_a_real_instance():
    # Keine unbeobachtbare Geister-Kennzahl: auf einer Instanz, bei der die
    # Regel bekanntermaßen greift, muss die Summe der grade_excluded-Werte > 0
    # sein.
    instance = generate_instance(**PRESETS["Materialsorten zahlen sich aus"])
    result = solve(instance, use_propagation=True)
    assert sum(n.grade_excluded for n in result.nodes) > 0


def test_prune_infeasible_is_actually_reachable_in_the_baseline():
    # Gegenprobe zum "unreachable status"-Fehlermuster dieser Serie: hier soll
    # der Status GENAU DANN erreicht werden, wenn Propagation aus ist - anders
    # als bei den drei früheren Funden (branch-cut-demo, constraint-
    # programming-demo, cutting-stock-branch-bound-demo), wo ein geplanter
    # Status nie feuerte.
    instance = generate_instance(**PRESETS["Materialsorten zahlen sich aus"])
    baseline = solve(instance, use_propagation=False)
    wasted = sum(1 for n in baseline.nodes if n.status == "prune_infeasible")
    assert wasted > 0
    # Und im propagierten Baum darf dieser Status NIE auftauchen - die
    # unzulässigen Optionen werden dort gar nicht erst erzeugt.
    propagated = solve(instance, use_propagation=True)
    assert all(n.status != "prune_infeasible" for n in propagated.nodes)


def test_max_nodes_cap_is_honored_and_flagged_as_truncated():
    instance = generate_instance(n_types=7, roll_width=100, max_demand=4, n_grades=4, seed=1)
    result = solve(instance, use_propagation=True, max_nodes=30)
    assert len(result.nodes) <= 30 + 30  # Sicherheitsmarge für den letzten unvollständigen Options-Batch
    assert result.truncated


@pytest.mark.parametrize("name", list(PRESETS.keys()))
def test_presets_solve_correctly_with_propagation(name):
    instance = generate_instance(**PRESETS[name])
    result = solve(instance, use_propagation=True, max_nodes=100_000)
    assert not result.truncated
    true_min = solve_bruteforce(instance)
    assert result.best_value == true_min, name


@pytest.mark.parametrize("name", list(PRESETS.keys()))
def test_presets_match_ortools_cross_check(name):
    instance = generate_instance(**PRESETS[name])
    result = solve(instance, use_propagation=True, max_nodes=100_000)
    ortools_result = solve_with_ortools(instance, time_limit_seconds=10.0)
    assert ortools_result["best_value"] == result.best_value, name
