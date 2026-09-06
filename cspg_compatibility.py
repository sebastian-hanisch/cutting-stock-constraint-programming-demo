"""Materialsorten-Kompatibilität: zwei Sorten dürfen nur auf derselben Rolle
landen, wenn sie BENACHBART sind (|g1 - g2| <= 1) - eine reale, in der
Papier-/Textil-/Kunststoffindustrie geläufige Qualitätskontroll-Regel (sehr
unterschiedliche Sorten dürfen nicht vermischt werden, ähnliche/benachbarte
Sorten sind unkritisch). Anders als die künstlichen Zufalls-Paare aus
constraint-programming-demo (erste Linie) hat diese Regel eine Struktur: der
Kompatibilitätsgraph über die Sorten ist ein PFADGRAPH (1-2-3-...-G), und jede
Clique in einem Pfadgraphen hat höchstens Größe 2. Ein Bin kann deshalb
nachweislich NIE mehr als zwei verschiedene (dann zwangsläufig benachbarte)
Sorten gleichzeitig enthalten - der Zustand eines Bins lässt sich deshalb
vollständig durch ein sortiertes Tupel von 0, 1 oder 2 Sorten darstellen,
statt eine allgemeine Menge verwalten zu müssen."""


def grade_compatible(grades_present, g_new):
    """grades_present: sortiertes Tupel von 0, 1 oder 2 bereits im Bin
    vorhandenen Sorten. True, wenn eine weitere Rolle der Sorte g_new
    hinzugefügt werden darf, ohne die Pfadgraph-Clique-Eigenschaft zu
    verletzen."""
    if not grades_present:
        return True
    if len(grades_present) == 1:
        return abs(grades_present[0] - g_new) <= 1
    return g_new in grades_present


def add_grade(grades_present, g_new):
    if g_new in grades_present:
        return grades_present
    return tuple(sorted(grades_present + (g_new,)))
