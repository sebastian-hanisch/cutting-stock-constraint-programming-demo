"""Zufällige 1D-Cutting-Stock-Instanzen, EIN Rollentyp - wie in jedem vorherigen
Stück dieser Linie, erweitert um eine echte Nebenbedingung: jeder Auftragstyp
bekommt eine Materialsorte (1..n_grades). Siehe cspg_compatibility.py für die
Kompatibilitätsregel."""

from dataclasses import dataclass

import numpy as np

from cspg_constants import WIDTH_FRACTION_RANGE


@dataclass(frozen=True)
class CuttingStockInstance:
    roll_width: int
    item_widths: tuple  # eine Breite je Auftragstyp
    item_demands: tuple  # Bedarf (Menge) je Auftragstyp, parallel zu item_widths
    item_grades: tuple  # Materialsorte (1..n_grades) je Auftragstyp
    n_grades: int

    @property
    def n_types(self):
        return len(self.item_widths)


def generate_instance(n_types, roll_width, max_demand, n_grades, seed):
    rng = np.random.default_rng(seed)
    lo = max(1, round(WIDTH_FRACTION_RANGE[0] * roll_width))
    hi = max(lo + 1, round(WIDTH_FRACTION_RANGE[1] * roll_width))
    widths = rng.integers(lo, hi + 1, size=n_types)
    demands = rng.integers(1, max_demand + 1, size=n_types)
    grades = rng.integers(1, n_grades + 1, size=n_types)
    return CuttingStockInstance(
        roll_width=int(roll_width),
        item_widths=tuple(int(w) for w in widths),
        item_demands=tuple(int(d) for d in demands),
        item_grades=tuple(int(g) for g in grades),
        n_grades=int(n_grades),
    )


def expand_pieces(instance):
    """Bedarfsmengen zu individuellen (Breite, Materialsorte)-Stück-Objekten
    expandiert, absteigend nach Breite sortiert (First-Fit-Decreasing) - die
    Brücke zu Bin Packing, wie in jedem vorherigen Stück dieser Linie."""
    pieces = []
    for w, q, g in zip(instance.item_widths, instance.item_demands, instance.item_grades):
        pieces.extend([(w, g)] * q)
    pieces.sort(key=lambda p: (-p[0], p[1]))
    return tuple(pieces)
