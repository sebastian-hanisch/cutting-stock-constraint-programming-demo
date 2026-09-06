"""Defaults, slider bounds und Presets für die Cutting-Stock-Constraint-
Programming-Demo."""

DEFAULT_N_TYPES = 4
DEFAULT_MAX_DEMAND = 2
DEFAULT_ROLL_WIDTH = 100
DEFAULT_N_GRADES = 3
DEFAULT_SEED = 7

N_TYPES_MIN, N_TYPES_MAX = 2, 7
MAX_DEMAND_MIN, MAX_DEMAND_MAX = 1, 4
ROLL_WIDTH_MIN, ROLL_WIDTH_MAX = 50, 200
N_GRADES_MIN, N_GRADES_MAX = 2, 4

# Auftragsbreiten werden als Anteil der Rollenbreite gezogen - hält die Instanzen
# unabhängig von der absoluten Rollenbreite vergleichbar (wie in jedem
# vorherigen Stück dieser Linie).
WIDTH_FRACTION_RANGE = (0.15, 0.6)

# Per Prototyp kalibriert.
MAX_NODES_EXPLORED = 100_000
MAX_NODES_RENDERED = 800
ORTOOLS_TIME_LIMIT_SECONDS = 5.0

PRESETS = {
    "Winzige Instanz (Baum komplett sichtbar)": {
        "n_types": 3, "roll_width": 100, "max_demand": 2, "n_grades": 3, "seed": 1,
    },
    "Materialsorten zahlen sich aus": {
        "n_types": 7, "roll_width": 100, "max_demand": 4, "n_grades": 3, "seed": 13,
    },
    "Größere Instanz": {
        "n_types": 7, "roll_width": 100, "max_demand": 4, "n_grades": 4, "seed": 1,
    },
}
