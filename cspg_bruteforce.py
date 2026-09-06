"""Erschöpfende Referenzlösung für Bin Packing mit Materialsorten-Kompatibilität
- unabhängig von der Branch-&-Bound-Suche, nur für kleine Instanzen praktikabel.
Wie csbb_bruteforce.py, zusätzlich mit grade_compatible-Prüfung vor jeder
Zuweisung."""

from cspg_compatibility import add_grade, grade_compatible
from cspg_scenario import expand_pieces


def solve_bruteforce(instance):
    pieces = expand_pieces(instance)
    n = len(pieces)
    best = {"count": n}  # triviale obere Schranke: ein Bin pro Stück

    def assign(idx, bins):
        if len(bins) >= best["count"]:
            return
        if idx == n:
            best["count"] = min(best["count"], len(bins))
            return
        width, grade = pieces[idx]
        for i, (cap, grades_present) in enumerate(bins):
            if cap >= width and grade_compatible(grades_present, grade):
                old = bins[i]
                bins[i] = (cap - width, add_grade(grades_present, grade))
                assign(idx + 1, bins)
                bins[i] = old
        bins.append((instance.roll_width - width, (grade,)))
        assign(idx + 1, bins)
        bins.pop()

    assign(0, [])
    return best["count"]
