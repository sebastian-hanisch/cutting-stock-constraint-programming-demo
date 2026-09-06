"""Tiefensuche für Bin Packing wie in cutting-stock-branch-bound-demo, erweitert
um eine ECHTE Nebenbedingung (Materialsorten-Kompatibilität, siehe
cspg_compatibility.py) statt der künstlichen Zufalls-Paare aus
constraint-programming-demo (erste Linie). Unabhängiger Zweig direkt von der
Wurzel - kein Teil der Konvergenz-Kette (Symmetrie-Schnitt/LP-Schranke).

`use_propagation=True` (Normalfall, Hauptbaum dieser Demo): materialinkompatible
Bins werden beim Erzeugen der Kindoptionen gar nicht erst als Option generiert -
die Anzahl so ausgeschlossener Bins wird pro Knoten als `grade_excluded`
gezählt (eine echte, beobachtbare Kennzahl statt eines toten Status - Lektion
aus den drei vorherigen "unreachable status"-Funden dieser Serie).

`use_propagation=False` (Baseline für den Vergleich): kapazitätspassende, aber
materialinkompatible Bins werden TROTZDEM als Kindoption erzeugt und sofort als
`prune_infeasible` markiert (ein verschwendeter Knoten). Wichtig: anders als
`cutting-stock-branch-bound-demo`s Docstring-Behauptung ("Bin Packing braucht
strukturell nie prune_infeasible") gilt das nur für reine Kapazitätsprüfung -
mit der NEUEN Materialsorten-Regel ist `prune_infeasible` hier ein ECHTER,
tatsächlich erreichbarer Status im Baseline-Pfad, kein Rückfall in den
"unreachable status"-Fehler."""

from dataclasses import dataclass

from cspg_bounds import weak_bound
from cspg_compatibility import add_grade, grade_compatible
from cspg_constants import MAX_NODES_EXPLORED
from cspg_scenario import expand_pieces


@dataclass(frozen=True)
class Node:
    id: int
    parent_id: int
    depth: int  # Anzahl bislang platzierter Stücke
    piece_width: int  # das gerade platzierte Stück, None für die Wurzel
    piece_grade: object  # Materialsorte des gerade platzierten Stücks, None für die Wurzel
    target: object  # ("existing", bin_index) oder ("new", bin_index), None für die Wurzel
    bins_open: int  # Anzahl offener Bins NACH dieser Entscheidung
    bound: object  # Schranke an diesem Knoten, None an Blättern
    status: str  # root | branch | prune_bound | prune_infeasible | leaf_new_best | leaf_not_best
    grade_excluded: int  # wie viele kapazitätspassende Bins hier per Materialsorte ausgeschlossen wurden


@dataclass(frozen=True)
class SolveResult:
    best_value: int
    best_bins: tuple  # (Restkapazität, vorhandene Sorten) je Bin der besten Lösung
    nodes: tuple
    incumbent_history: tuple
    truncated: bool
    pieces: tuple


def solve(instance, use_propagation=True, max_nodes=MAX_NODES_EXPLORED):
    pieces = expand_pieces(instance)
    n = len(pieces)
    nodes = []
    incumbent_history = []
    best = {"count": None, "bins": None}
    truncated = {"flag": False}
    next_id = [0]

    def new_node(parent_id, depth, piece_width, piece_grade, target, bins_open, bound, status, grade_excluded=0):
        node = Node(next_id[0], parent_id, depth, piece_width, piece_grade, target, bins_open, bound, status, grade_excluded)
        next_id[0] += 1
        nodes.append(node)
        return node

    root_bound = weak_bound(instance, pieces, 0, [])
    root = new_node(None, 0, None, None, None, 0, root_bound, "root")

    def branch_options(bins, width, grade):
        """Liste von (target, new_bins_or_None, infeasible: bool). new_bins is
        None nur, wenn infeasible=True (use_propagation=False-Pfad: ein
        kapazitätspassendes, aber materialinkompatibles Bin wird trotzdem als
        Option erzeugt, aber ohne gültigen Folgezustand)."""
        options = []
        grade_excluded = 0
        for i, (cap, grades_present) in enumerate(bins):
            if cap < width:
                continue
            compatible = grade_compatible(grades_present, grade)
            if compatible:
                new_bins = list(bins)
                new_bins[i] = (cap - width, add_grade(grades_present, grade))
                options.append((("existing", i), new_bins, False))
            elif use_propagation:
                grade_excluded += 1
            else:
                options.append((("existing", i), None, True))
        options.append((("new", len(bins)), list(bins) + [(instance.roll_width - width, (grade,))], False))
        return options, grade_excluded

    def explore(node, depth, bins):
        width, grade = pieces[depth]
        options, grade_excluded_here = branch_options(bins, width, grade)

        for idx, (target, new_bins, infeasible) in enumerate(options):
            if truncated["flag"] or len(nodes) >= max_nodes:
                truncated["flag"] = True
                return

            excluded_here = grade_excluded_here if idx == 0 else 0
            new_depth = depth + 1

            if infeasible:
                new_node(node.id, new_depth, width, grade, target, len(bins), None, "prune_infeasible")
                continue

            bins_open = len(new_bins)

            if new_depth == n:
                is_new_best = best["count"] is None or bins_open < best["count"]
                status = "leaf_new_best" if is_new_best else "leaf_not_best"
                child = new_node(node.id, new_depth, width, grade, target, bins_open, None, status, excluded_here)
                if is_new_best:
                    best["count"] = bins_open
                    best["bins"] = tuple(new_bins)
                    incumbent_history.append((child.id, bins_open))
                continue

            bound = weak_bound(instance, pieces, new_depth, new_bins)
            if best["count"] is not None and bound >= best["count"]:
                new_node(node.id, new_depth, width, grade, target, bins_open, bound, "prune_bound", excluded_here)
                continue

            child = new_node(node.id, new_depth, width, grade, target, bins_open, bound, "branch", excluded_here)
            explore(child, new_depth, new_bins)

    explore(root, 0, [])

    return SolveResult(
        best_value=best["count"],
        best_bins=best["bins"],
        nodes=tuple(nodes),
        incumbent_history=tuple(incumbent_history),
        truncated=truncated["flag"],
        pieces=pieces,
    )
