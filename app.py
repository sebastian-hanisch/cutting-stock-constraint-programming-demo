"""
Constraint Programming am Cutting-Stock-Problem – interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Fünftes Stück der Cutting-Stock-Linie: ein unabhängiger Zweig direkt von
cutting-stock-branch-bound-demo (kein Teil der Konvergenz-Kette aus
Symmetrie-Schnitt und LP-Schranke) - erweitert um eine ECHTE Nebenbedingung
(Materialsorten-Kompatibilität) statt der künstlichen Zufalls-Paare aus
constraint-programming-demo (erste Linie).

Lauffähig mit: streamlit run app.py
"""

import time

import streamlit as st

import cspg_constants as C
from cspg_bruteforce import solve_bruteforce
from cspg_evaluation import propagation_comparison, stats_up_to_step
from cspg_ortools_reference import solve_with_ortools
from cspg_presets import (
    apply_preset,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sync_query_params,
)
from cspg_scenario import expand_pieces, generate_instance
from cspg_solver import solve
from cspg_visualization import build_comparison_chart, build_tree_figure

st.set_page_config(page_title="Constraint Programming am Cutting-Stock-Problem – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _compute_solve(n_types, roll_width, max_demand, n_grades, seed):
    instance = generate_instance(n_types, roll_width, max_demand, n_grades, seed)
    result = solve(instance, use_propagation=True)
    true_optimum = solve_bruteforce(instance)
    return instance, result, true_optimum


@st.cache_data(show_spinner=False)
def _compute_comparison(n_types, roll_width, max_demand, n_grades, seed):
    instance = generate_instance(n_types, roll_width, max_demand, n_grades, seed)
    cmp = propagation_comparison(instance)
    ortools_result = solve_with_ortools(instance)
    cmp["ortools_best_value"] = ortools_result["best_value"]
    cmp["ortools_wall_time"] = ortools_result["wall_time"]
    cmp["ortools_proven_optimal"] = ortools_result["proven_optimal"]
    return cmp


st.title("📋📦 Constraint Programming am Cutting-Stock-Problem")
st.markdown(
    """
Fünftes Stück der Cutting-Stock-Linie - ein unabhängiger Zweig direkt von
[cutting-stock-branch-bound-demo](https://github.com/sebastian-hanisch/cutting-stock-branch-bound-demo)
(kein Teil der Konvergenz-Kette aus
[cutting-stock-cutting-planes-demo](https://github.com/sebastian-hanisch/cutting-stock-cutting-planes-demo)
und
[cutting-stock-branch-cut-demo](https://github.com/sebastian-hanisch/cutting-stock-branch-cut-demo)).
Anders als
[constraint-programming-demo](https://github.com/sebastian-hanisch/constraint-programming-demo)
aus der ersten Linie (künstliche Zufalls-Paare) bekommt jeder Auftragstyp hier
eine **Materialsorte** - nur BENACHBARTE Sorten dürfen dieselbe Rolle teilen,
eine reale, in der Papier-/Textil-/Kunststoffindustrie geläufige
Qualitätskontroll-Regel.
"""
)
st.caption(
    "Anders als die Fall-Demos im Portfolio, die an einem Anwendungsfall mehrere Verfahren "
    "vergleichen, zeigt diese Demo - wie jedes Stück dieser Linie - ein Verfahren an einem "
    "wachsenden Beispiel."
)

with st.expander("So funktioniert die Propagation", expanded=True):
    st.markdown(
        r"""
Jeder Auftragstyp hat eine Materialsorte $1, \dots, G$. Zwei Sorten dürfen nur
dieselbe Rolle teilen, wenn sie benachbart sind ($|g_1 - g_2| \leq 1$). Da der
Kompatibilitätsgraph über die Sorten ein **Pfadgraph** ist, kann eine Rolle
nachweislich nie mehr als ZWEI verschiedene (dann zwangsläufig benachbarte)
Sorten gleichzeitig enthalten.

Beim Erzeugen der Kindoptionen prüft die Suche für jedes bereits offene Bin
Kapazität UND Materialkompatibilität. Kapazitätspassende, aber
materialinkompatible Bins werden gar nicht erst als Option erzeugt - im Baum
unten petrol markiert, wo das tatsächlich passiert ist. Zum Vergleich löst
diese Demo dieselbe Instanz zusätzlich mit dem echten
**Google-OR-Tools-CP-SAT-Solver** - dem Industriestandard, hier nur an
Ergebnis und Zeit gezeigt.
        """
    )

st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
PRESET_HELP = {
    "Winzige Instanz (Baum komplett sichtbar)": "3 Auftragstypen - der komplette Suchbaum passt aufs Bild, mit sichtbaren Ausschlüssen.",
    "Materialsorten zahlen sich aus": "Ein deutlicher, aber ehrlich moderater Effekt - wie schon bei constraint-programming-demo in der ersten Linie.",
    "Größere Instanz": "Mehr Auftragstypen und Materialsorten - die Propagation vermeidet tausende verschwendete Knoten.",
}
preset_cols = st.columns(len(C.PRESETS))
for i, name in enumerate(C.PRESETS.keys()):
    with preset_cols[i]:
        st.button(name, width="stretch", on_click=apply_preset, args=(name,), help=PRESET_HELP[name])

st.caption(
    "🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, "
    "um ein Szenario zu teilen."
)

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    st.header("⚙️ Einstellungen")
    n_types = st.slider("Anzahl Auftragstypen", *bounds("n_types_slider"), key="n_types_slider")
    roll_width = st.slider("Rollenbreite", *bounds("roll_width_slider"), key="roll_width_slider")
    max_demand = st.slider(
        "Maximaler Bedarf je Auftragstyp", *bounds("max_demand_slider"), key="max_demand_slider",
        help="Höherer Bedarf bedeutet mehr Stücke - mehr Gelegenheit für Ausschlüsse.",
    )
    n_grades = st.slider(
        "Anzahl Materialsorten", *bounds("n_grades_slider"), key="n_grades_slider",
        help="Mehr Sorten bedeuten mehr potenzielle Inkompatibilitäten zwischen offenen Bins.",
    )
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1)

    st.button(
        "🎲 Neue Instanz generieren",
        width="stretch",
        on_click=randomize_seed,
        help="Würfelt neue Auftragsbreiten, -mengen und -sorten.",
    )

sync_query_params(n_types, roll_width, max_demand, n_grades, seed)

scenario_key = (int(n_types), int(roll_width), int(max_demand), int(n_grades), int(seed))

with st.spinner("Durchsuche den Baum..."):
    instance, result, true_optimum = _compute_solve(*scenario_key)

pieces = expand_pieces(instance)
st.caption(
    f"🔗 {instance.n_types} Auftragstypen, Breiten {instance.item_widths} mit Bedarf "
    f"{instance.item_demands} und Materialsorten {instance.item_grades} ({instance.n_grades} Sorten) "
    f"→ {len(pieces)} Einzelstücke, Rollenbreite {instance.roll_width}."
)

st.markdown("## 🎯 Der Suchbaum mit Propagation")

if "cspg_step" not in st.session_state or st.session_state.get("cspg_step_owner") != scenario_key:
    st.session_state["cspg_step"] = len(result.nodes) - 1
    st.session_state["cspg_step_owner"] = scenario_key

max_step = len(result.nodes) - 1
step_col, play_col = st.columns([5, 1])
with step_col:
    if max_step == 0:
        step = 0
        st.caption("Nur der Wurzelknoten - kein Regler nötig.")
    else:
        step = st.slider(
            "Schritt (Knoten)", 0, max_step, key="cspg_step",
            help="Ein Schritt = ein besuchter Suchbaum-Knoten, in Besuchsreihenfolge.",
        )
with play_col:
    auto_play = st.button("▶️ Abspielen", width="stretch")

render_note = (
    f" (zeigt die ersten {C.MAX_NODES_RENDERED:,} von {len(result.nodes):,} Knoten)"
    if len(result.nodes) > C.MAX_NODES_RENDERED
    else ""
)
st.caption(f"{len(result.nodes):,} Knoten insgesamt besucht{render_note}.")

tree_slot = st.empty()


def _render(current_step):
    tree_slot.plotly_chart(
        build_tree_figure(result, current_step, C.MAX_NODES_RENDERED),
        width="stretch", key=f"tree_{current_step}",
    )


if auto_play:
    n_frames = min(max_step + 1, 60)
    frame_skip = max(1, (max_step + 1) // n_frames)
    for s in list(range(0, max_step, frame_skip)) + [max_step]:
        _render(s)
        time.sleep(0.08)
    step = max_step
else:
    _render(step)

live = stats_up_to_step(result, step)
lm1, lm2, lm3, lm4 = st.columns(4)
lm1.metric("Besuchte Knoten (bisher)", f"{live['nodes_so_far']:,}")
lm2.metric(
    "Gestutzt (Bound)", f"{live['pruned_bound']:,}",
    help="Äste, die abgebrochen wurden, weil die Schranke keine Verbesserung mehr versprach.",
)
lm3.metric(
    "Per Materialsorte ausgeschlossen", f"{live['grade_excluded_so_far']:,}",
    help="Kapazitätspassende Bins, die die Propagation gar nicht erst als Option erzeugt hat.",
)
lm4.metric(
    "Bester Fund bisher", live["current_best"] if live["current_best"] is not None else "–",
    help="Die wenigsten Rollen einer bislang vollständig gefundenen Lösung.",
)

if result.truncated:
    st.error(
        f"⛔ Abgebrochen bei {C.MAX_NODES_EXPLORED:,} untersuchten Knoten - das gezeigte Ergebnis ist die "
        f"beste bislang gefundene, nicht garantiert optimale Lösung."
    )
else:
    st.caption(
        f"Bewiesenes Optimum: **{result.best_value}** Rollen - stimmt mit der unabhängigen "
        f"Bruteforce-Referenz überein."
        if result.best_value == true_optimum
        else f"⚠️ Optimum {result.best_value} weicht von der Bruteforce-Referenz {true_optimum} ab - bitte melden."
    )

st.markdown("---")

st.subheader("📐 Wie oft verhindert die Materialsorten-Regel einen unnötigen Ast?")
st.markdown(
    """
Live für Ihre aktuelle Instanz: derselbe Suchlauf, einmal als Baseline (die
Regel wird respektiert, aber Verletzungen fallen erst am jeweiligen Kindknoten
auf - ein verschwendeter Knoten), einmal mit Propagation (unzulässige Bins
werden gar nicht erst als Kindoption erzeugt), plus der echte OR-Tools-CP-SAT-
Solver als unabhängiger Beleg.
"""
)

cmp = _compute_comparison(*scenario_key)
st.plotly_chart(build_comparison_chart(cmp), width="stretch", key="comparison_chart")

cc1, cc2, cc3 = st.columns(3)
cc1.metric(
    "Baseline", f"{cmp['baseline_nodes']:,} Knoten" + (" (abgebrochen)" if cmp["baseline_truncated"] else ""),
    help=f"Davon {cmp['baseline_wasted']:,} sofort als unzulässig verworfene, verschwendete Knoten.",
)
cc2.metric(
    "Mit Propagation", f"{cmp['propagation_nodes']:,} Knoten" + (" (abgebrochen)" if cmp["propagation_truncated"] else ""),
    delta=f"{cmp['propagation_nodes'] - cmp['baseline_nodes']:,} ggü. Baseline", delta_color="inverse",
)
cc3.metric(
    "OR-Tools CP-SAT", cmp["ortools_best_value"],
    help=f"Echter industrieller Solver, {cmp['ortools_wall_time']:.4f}s - "
    + ("beweist Optimalität." if cmp["ortools_proven_optimal"] else "Zeitlimit erreicht."),
)

if cmp["baseline_best"] == cmp["propagation_best"] == cmp["ortools_best_value"]:
    factor = cmp["baseline_nodes"] / cmp["propagation_nodes"] if cmp["propagation_nodes"] else float("inf")
    if factor >= 1.3:
        st.success(
            f"✅ Propagation braucht **{factor:.1f}×** weniger Knoten als die Baseline - für dasselbe "
            f"bewiesene Optimum. Alle drei Verfahren (diese Demo, Baseline, OR-Tools) finden denselben "
            f"Wert: **{cmp['propagation_best']}**."
        )
    else:
        st.info(
            "Bei dieser Instanz macht sich die Materialsorten-Regel kaum bemerkbar - probieren Sie das "
            "Preset \"Materialsorten zahlen sich aus\" oder mehr Materialsorten."
        )
else:
    st.warning("⚠️ Die drei Verfahren sind sich uneinig - das sollte nie passieren, bitte melden.")

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Kompatibilitätsregel**: Materialsorten $1, \dots, G$, zwei Sorten $g_1, g_2$
kompatibel genau dann, wenn $|g_1 - g_2| \leq 1$. Der Kompatibilitätsgraph
über die Sorten ist ein **Pfadgraph** $1 - 2 - 3 - \dots - G$. Cliquen in
einem Pfadgraphen haben höchstens Größe 2 - eine Rolle kann deshalb NIE mehr
als zwei verschiedene (dann zwangsläufig benachbarte) Sorten gleichzeitig
enthalten. Der Zustand eines Bins lässt sich deshalb vollständig durch ein
Tupel von 0, 1 oder 2 Sorten darstellen (`cspg_compatibility.py`).

**Anders als `constraint-programming-demo` (erste Linie)**: dort waren die
Kompatibilitätspaare zufällig und künstlich an das Rucksackproblem angehängt.
Hier ergibt sich die Regel aus einer realen Branchenpraxis (Materialsorten-
Trennung) UND hat eine ausnutzbare Struktur (Pfadgraph statt beliebigem
Graphen).

**Ehrlich benannt**: der gemessene Effekt ist moderat (Faktor bis ~3,8× in
breiten Sweeps, nicht die dramatischen Größenordnungen des Symmetrie-Schnitts
oder der LP-Schranke aus den vorherigen Stücken) - konsistent mit
`constraint-programming-demo`s eigenem Fund in der ersten Linie (~1,7× allein
durch Kapazitätspropagation).

**`prune_infeasible` ist hier ECHT erreichbar**: `cutting-stock-branch-bound-
demo` begründet, warum reine Kapazitätsprüfung nie einen
`prune_infeasible`-Status braucht. Mit der neuen Materialsorten-Regel gilt das
nicht mehr - die Baseline dieser Demo (`use_propagation=False`) erzeugt
kapazitätspassende, aber materialinkompatible Bins trotzdem als Kindknoten und
markiert sie sofort als `prune_infeasible` (ein verschwendeter Knoten), statt
sie wie mit Propagation gar nicht erst zu erzeugen.

Implementiert in `cspg_compatibility.py` (die Regel), `cspg_solver.py`
(Verzweigung mit und ohne Propagation), `cspg_bruteforce.py` (unabhängige
Referenzlösung) und `cspg_ortools_reference.py` (echter
Google-OR-Tools-CP-SAT-Solver).
        """
    )

st.markdown("---")

st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning. Interesse an einer maßgeschneiderten Lösung für "
    "Ihr Unternehmen? [Kontakt aufnehmen](https://sebastianhanisch.net/kontakt.html)"
)
