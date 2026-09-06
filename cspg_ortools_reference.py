"""Ruft den echten Google-OR-Tools-CP-SAT-Solver auf derselben Instanz auf - das
Muster aus constraint-programming-demo/csp_ortools_reference.py (erste Linie),
hier zum ersten Mal in der Cutting-Stock-Linie. Dient als unabhängiger
Korrektheits-Cross-Check, unabhängig von cspg_solver.py und cspg_bruteforce.py.

Standard-Bin-Packing-CP-SAT-Modell (x[i][k]: Stück i in Bin k, y[k]: Bin k
benutzt, Kapazität je Bin) plus EINE zusätzliche Nebenbedingung pro Paar
inkompatibler Materialsorten: x[i][k] + x[j][k] <= 1 für jedes Bin k. Das
Pfadgraph-Argument aus cspg_compatibility.py (höchstens zwei Sorten pro Bin)
folgt daraus automatisch - keine gesonderte "höchstens zwei Sorten"-Formulierung
nötig."""

from ortools.sat.python import cp_model

from cspg_constants import ORTOOLS_TIME_LIMIT_SECONDS
from cspg_scenario import expand_pieces


def solve_with_ortools(instance, time_limit_seconds=ORTOOLS_TIME_LIMIT_SECONDS):
    pieces = expand_pieces(instance)
    n = len(pieces)
    max_bins = n  # triviale, aber sichere Obergrenze: ein Bin pro Stück

    model = cp_model.CpModel()
    x = [[model.NewBoolVar(f"x{i}_{k}") for k in range(max_bins)] for i in range(n)]
    y = [model.NewBoolVar(f"y{k}") for k in range(max_bins)]

    for i in range(n):
        model.Add(sum(x[i][k] for k in range(max_bins)) == 1)

    for k in range(max_bins):
        model.Add(sum(pieces[i][0] * x[i][k] for i in range(n)) <= instance.roll_width * y[k])

    for i in range(n):
        for j in range(i + 1, n):
            if abs(pieces[i][1] - pieces[j][1]) > 1:
                for k in range(max_bins):
                    model.Add(x[i][k] + x[j][k] <= 1)

    model.Minimize(sum(y))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_seconds
    solver.parameters.num_search_workers = 1  # ein Kern, deterministisch - fairer Vergleich

    status = solver.Solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        best_value = int(round(solver.ObjectiveValue()))
    else:
        best_value = None

    return {
        "status": solver.StatusName(status),
        "proven_optimal": status == cp_model.OPTIMAL,
        "best_value": best_value,
        "wall_time": solver.WallTime(),
    }
