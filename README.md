# Constraint Programming am Cutting-Stock-Problem – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-cutting-stock-constraint-programming-demo.streamlit.app/)**

Fünftes Stück der Cutting-Stock-Linie - ein unabhängiger Zweig direkt von
[cutting-stock-branch-bound-demo](https://github.com/sebastian-hanisch/cutting-stock-branch-bound-demo)
(kein Teil der Konvergenz-Kette aus
[cutting-stock-cutting-planes-demo](https://github.com/sebastian-hanisch/cutting-stock-cutting-planes-demo)
und
[cutting-stock-branch-cut-demo](https://github.com/sebastian-hanisch/cutting-stock-branch-cut-demo)).
Anders als
[constraint-programming-demo](https://github.com/sebastian-hanisch/constraint-programming-demo)
aus der ersten Linie (künstliche Zufalls-Paare) bekommt jeder Auftragstyp hier
eine **Materialsorte** - nur benachbarte Sorten dürfen dieselbe Rolle teilen,
eine reale, in der Papier-/Textil-/Kunststoffindustrie geläufige
Qualitätskontroll-Regel.

## Die Kompatibilitätsregel

Materialsorten $1, \dots, G$, zwei Sorten kompatibel genau dann, wenn
$|g_1 - g_2| \leq 1$. Der Kompatibilitätsgraph über die Sorten ist ein
**Pfadgraph** - Cliquen darin haben höchstens Größe 2, eine Rolle kann also
nachweislich nie mehr als zwei verschiedene (dann zwangsläufig benachbarte)
Sorten gleichzeitig enthalten. Anders als bei `constraint-programming-demo`
(zufällige, künstlich angehängte Paare) ergibt sich die Regel hier aus
realer Branchenpraxis UND hat eine ausnutzbare Struktur.

## Propagation statt totem Status

Beim Erzeugen der Kindoptionen werden kapazitätspassende, aber
materialinkompatible Bins gar nicht erst als Option erzeugt - die Anzahl wird
pro Knoten als `grade_excluded` gezählt (eine echte, beobachtbare Kennzahl,
keine Geister-Kennzahl - Lektion aus den drei vorherigen "unreachable
status"-Funden dieser Serie).

**Ein interessanter Gegenfall zu dieser Serie**: `cutting-stock-branch-bound-
demo` begründet, warum reine Kapazitätsprüfung nie einen
`prune_infeasible`-Status braucht. Mit dieser neuen Materialsorten-Regel ist
`prune_infeasible` tatsächlich ECHT erreichbar: die Baseline dieser Demo
(`use_propagation=False`) erzeugt kapazitätspassende, aber materialinkompatible
Bins trotzdem als Kindknoten und markiert sie sofort als `prune_infeasible`
(ein verschwendeter Knoten), statt sie wie mit Propagation gar nicht erst zu
erzeugen - ein Regressionstest verankert genau das (Status muss in der
Baseline auftreten, im propagierten Baum nie).

## Ehrlich moderater Effekt

Per Prototyp vor der Umsetzung verifiziert: die Propagation wirkt, aber mit
moderatem statt dramatischem Effekt (Reduktionsfaktoren bis ~3,8× in breiten
Sweeps - kein manipuliertes "Baseline scheitert"-Beispiel gefunden, obwohl
gezielt danach gesucht wurde). Konsistent mit `constraint-programming-demo`s
eigenem Fund in der ersten Linie (~1,7× allein durch Kapazitätspropagation).
Auf einer größeren Instanz spart die Propagation dennoch 11.152 unnötig
besuchte Knoten (16.072 → 4.920) bei exakt gleichem bewiesenem Optimum.

## Verifikation

- **Bruteforce-Cross-Check** mit UND ohne Propagation.
- **OR-Tools-CP-SAT-Cross-Check** auf allen drei Presets - erstes
  OR-Tools-Vorkommen in dieser Linie.
- **`grade_excluded`-Wirksamkeits-Test**: Summe > 0 auf einer bekannten
  Instanz.
- **`prune_infeasible`-Erreichbarkeitstest**: Status muss in der Baseline
  auftreten, darf im propagierten Baum nie auftreten.
- **Sicherheitsgrenzen-Test** wie in jedem vorherigen Stück.

## Dateistruktur

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-Hauptablauf: Presets, Einstellungen, Suchbaum-Animation, Vergleich inkl. OR-Tools, Formulierungs-Expander |
| `cspg_constants.py` | Defaults, Regler-Grenzen, Sicherheitsgrenzen, `PRESETS` |
| `cspg_presets.py` | `SettingSpec`/`SETTING_SPECS`, Permalink-Logik, Presets, Zufalls-Seed-Button |
| `cspg_scenario.py` | Zufällige Cutting-Stock-Instanzen mit Materialsorten |
| `cspg_compatibility.py` | Materialsorten-Kompatibilitätsregel (Pfadgraph-Argument) |
| `cspg_bounds.py` | `weak_bound` |
| `cspg_solver.py` | n-äre Tiefensuche mit und ohne Materialsorten-Propagation |
| `cspg_bruteforce.py` | Unabhängige Referenzlösung (vollständige Enumeration) |
| `cspg_ortools_reference.py` | Echter Google-OR-Tools-CP-SAT-Solver |
| `cspg_evaluation.py` | Kennzahlen, Baseline/Propagation-Vergleich |
| `cspg_visualization.py` | Suchbaum- und Vergleichsdiagramm (Plotly) |
| `tests/` | Bruteforce- und OR-Tools-Cross-Check, Ausschluss-Wirksamkeit, Erreichbarkeitstest, Sicherheitsgrenzen |

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

---

Teil des [Operations-Research-Demo-Portfolios](https://sebastianhanisch.net/demos.html) von
[Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning.
Interesse an einer maßgeschneiderten Lösung? [Kontakt aufnehmen](https://sebastianhanisch.net/kontakt.html).
