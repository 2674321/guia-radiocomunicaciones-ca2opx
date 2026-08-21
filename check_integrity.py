#!/usr/bin/env python3
"""
Control de integridad: compara la fuente (FUENTE_RADIOCOMUNICACIONES.md)
contra el documento generado (manual_radiocomunicaciones.html).

Verifica:
 1. Todas las Claves 10 presentes          7. Códigos Q intactos
 2. Sin claves 10 duplicadas               8. Fuentes separadas y declaradas
 3. Ninguna clave eliminada                9. Alfabeto con 26 letras correctas
 4. Recursos/despacho intactos            10. Sin caracteres corruptos
 5. CDCIA se mantiene como CDCIA          11. Tildes/ñ correctas
 6. Códigos R intactos                    12/13. Estructura de tablas (thead, filas indivisibles)
"""

import re
import sys
import sys as _sys
import unicodedata

MD = (
    _sys.argv[_sys.argv.index("--md") + 1]
    if "--md" in _sys.argv
    else "FUENTE_RADIOCOMUNICACIONES.md"
)
HTML = (
    _sys.argv[_sys.argv.index("--html") + 1]
    if "--html" in _sys.argv
    else "manual_radiocomunicaciones.html"
)

# Correcciones puramente tipográficas permitidas (no cambian significado operativo)
TYPO_FIXES = [
    ("no importado el piso", "no importando el piso"),
    ("4 pisos o más no importando", "4 pisos o más, no importando"),
]


def norm(s: str) -> str:
    s = s.replace("&amp;", "&").replace("&middot;", "·")
    for a, b in TYPO_FIXES:
        s = s.replace(a, b)
    s = unicodedata.normalize("NFC", s)
    return re.sub(r"\s+", " ", s).strip()


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


md = read(MD)
html = read(HTML)

failures = []


def check(name, ok, detail=""):
    status = "OK  " if ok else "FALLO"
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(name)


def md_rows():
    """Extrae todas las filas |a|b|...| de las tablas markdown del documento."""
    rows = []
    for line in md.splitlines():
        line = line.strip()
        if line.startswith("|") and line.endswith("|") and "---" not in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            rows.append(cells)
    return rows


# ---------- Extracción desde Markdown ----------
# Los patrones de código son disjuntos entre secciones, por lo que la
# clasificación no requiere rastrear el encabezado de cada bloque.
md_claves, md_r, md_q, md_alfabeto, md_gen = {}, {}, {}, {}, {}
for cells in md_rows():
    if len(cells) >= 3 and re.match(r"^(10-|0-11)", cells[0]):
        md_claves[norm(cells[0])] = (norm(cells[1]), norm(cells[2]))
    elif len(cells) == 2 and re.match(r"^10-\d+$", cells[0]):
        md_gen[norm(cells[0])] = norm(cells[1])
    elif len(cells) == 2 and re.match(r"^R-\d+(-\d+)?$", cells[0]):
        md_r[norm(cells[0])] = norm(cells[1])
    elif len(cells) == 3 and re.match(r"^Q[A-Z]{2}$", cells[0]):
        md_q[cells[0]] = (norm(cells[1]), norm(cells[2]))
    elif len(cells) == 2 and re.match(r"^[A-Z]$", cells[0]) and cells[1].isupper():
        md_alfabeto[cells[0]] = norm(cells[1])

# ---------- Extracción desde HTML ----------
html_claves = {}
dups = []
for m in re.finditer(
    r'<tr><td class="clave">(.*?)</td><td>(.*?)</td><td class="rec">(.*?)</td></tr>',
    html,
    re.DOTALL,
):
    k, d, r = (norm(re.sub(r"<[^>]+>", "", x)) for x in m.groups())
    if k in html_claves or k in dups:
        dups.append(k)
    html_claves[k] = (d, r)

html_gen, dups_gen = {}, []
for m in re.finditer(
    r'<tr><td class="code">(10-\d+)</td><td>(.*?)</td></tr>', html, re.DOTALL
):
    k = norm(re.sub(r"<[^>]+>", "", m.group(1)))
    v = norm(re.sub(r"<[^>]+>", "", m.group(2)))
    if k in html_gen or k in dups_gen:
        dups_gen.append(k)
    html_gen[k] = v

html_r = {}
for m in re.finditer(
    r'<tr><td class="code">(R-[\d-]+)</td><td>(.*?)</td></tr>', html, re.DOTALL
):
    html_r[m.group(1)] = norm(re.sub(r"<[^>]+>", "", m.group(2)))

html_q = {}
for m in re.finditer(
    r'<tr><td class="code">(Q[A-Z]{2})</td><td class="preg">(.*?)</td><td>(.*?)</td></tr>',
    html,
    re.DOTALL,
):
    html_q[m.group(1)] = (norm(m.group(2)), norm(m.group(3)))

html_alfabeto = dict(
    re.findall(
        r'<tr><td class="letra">([A-Z])</td><td class="palabra">([A-Z-]+)</td></tr>',
        html,
    )
)

# ---------- Verificaciones ----------
print("=" * 64)
print("CONTROL DE INTEGRIDAD — GUÍA DE RADIOCOMUNICACIONES")
print("=" * 64)

# 1-3. Claves 10 completas, sin duplicados, sin eliminadas
missing = sorted(set(md_claves) - set(html_claves))
extra = sorted(set(html_claves) - set(md_claves))
check(
    "1/3. Claves 10: todas presentes, ninguna eliminada/inventada",
    not missing and not extra and len(md_claves) == len(html_claves),
    f"fuente={len(md_claves)}, doc={len(html_claves)}"
    + (f"; faltan={missing}" if missing else "")
    + (f"; sobran={extra}" if extra else ""),
)

check(
    "2. Sin claves 10 duplicadas",
    not dups,
    f"duplicadas={sorted(set(dups))}" if dups else "",
)

# 4. Descripciones y recursos intactos
diffs = [k for k in md_claves if k in html_claves and md_claves[k] != html_claves[k]]
check(
    "4. Descripciones y recursos despachados intactos",
    not diffs,
    "; ".join(f"{k}: {md_claves[k]} != {html_claves[k]}" for k in diffs[:5]),
)

# 5. CDCIA y frases propias de la edición Claves 10 de Coquimbo
if md_claves:
    cdc_md, cdc_html = md.count("CDCIA"), html.count("CDCIA")
    check(
        "5. 'CDCIA' se mantiene como CDCIA",
        cdc_md == cdc_html and cdc_html > 0,
        f"fuente={cdc_md}, doc={cdc_html}",
    )
    check(
        "5b. 'COMANDANCIA' preservado (clave 0-11)",
        md.count("LO QUE DISPONGA COMANDANCIA")
        == html.count("LO QUE DISPONGA COMANDANCIA"),
    )
    check(
        "5c. 'SEGÚN REQUERIMIENTO DEL CB SOLICITANTE' preservado",
        md.count("SEGÚN REQUERIMIENTO DEL CB SOLICITANTE")
        == html.count("SEGÚN REQUERIMIENTO DEL CB SOLICITANTE"),
    )

# 6. Códigos R
r_missing = sorted(set(md_r) - set(html_r))
r_diff = [k for k in md_r if k in html_r and md_r[k] != html_r[k]]
check(
    "6. Códigos R completos y con significado intacto",
    not r_missing and not r_diff and len(md_r) == len(html_r),
    f"fuente={len(md_r)}, doc={len(html_r)}"
    + (f"; faltan={r_missing}" if r_missing else "")
    + (f"; difieren={r_diff[:5]}" if r_diff else ""),
)

# 7. Códigos Q
q_missing = sorted(set(md_q) - set(html_q))
q_diff = [k for k in md_q if k in html_q and md_q[k] != html_q[k]]
check(
    "7. Códigos Q completos y con significado intacto",
    not q_missing and not q_diff and len(md_q) == len(html_q),
    f"fuente={len(md_q)}, doc={len(html_q)}"
    + (f"; faltan={q_missing}" if q_missing else "")
    + (f"; difieren={q_diff[:5]}" if q_diff else ""),
)

# 8. Fuentes separadas y declaradas
fuentes = [
    ("Código Q", "Fuente: Unión Internacional de Telecomunicaciones (UIT)"),
    ("Claves R", "Fuente: Corporación Nacional Forestal (CONAF)"),
    ("Claves 10", "Fuente: Cuerpo de Bomberos de Coquimbo"),
    (
        "Alfabeto Fonético",
        "Fuente: OACI/ICAO — Alfabeto de Deletreo Radiotelefónico Internacional",
    ),
]
ok8 = all(
    f"<strong>{t}</strong>" in html and f"<em>{f}</em>" in html for t, f in fuentes
)
check("8. Las cuatro fuentes declaradas por separado", ok8)

# 9. Alfabeto: 26 letras correctas
esperado = {
    "A": "ALFA",
    "B": "BRAVO",
    "C": "CHARLIE",
    "D": "DELTA",
    "E": "ECHO",
    "F": "FOXTROT",
    "G": "GOLF",
    "H": "HOTEL",
    "I": "INDIA",
    "J": "JULIETT",
    "K": "KILO",
    "L": "LIMA",
    "M": "MIKE",
    "N": "NOVEMBER",
    "O": "OSCAR",
    "P": "PAPA",
    "Q": "QUEBEC",
    "R": "ROMEO",
    "S": "SIERRA",
    "T": "TANGO",
    "U": "UNIFORM",
    "V": "VICTOR",
    "W": "WHISKY",
    "X": "X-RAY",
    "Y": "YANKEE",
    "Z": "ZULU",
}
check(
    "9. Alfabeto fonético: 26 letras con nomenclatura OACI",
    html_alfabeto == esperado,
    f"doc={len(html_alfabeto)} letras",
)

# 10. Caracteres corruptos
corruptos = [
    p for p in ("�", "Ã©", "Ã­", "Ã³", "Ãº", "Ã±", "â€", "\ufffd") if p in html
]
check("10. Sin caracteres corruptos / mojibake", not corruptos, str(corruptos))

# 11. Tildes y eñes
if md_claves:
    muestras = [
        "MECÁNICA",
        "Atención",
        "Emanaciones",
        "cardiorrespiratorio",
        "CÓNYUGE",
        "SÍRVASE",
    ]
elif md_gen:
    muestras = ["Comprobación", "teléfono", "Persecución", "Suspensión", "Localización"]
else:
    muestras = []
faltan = [m for m in muestras if m not in html]
check(
    "11. Tildes y caracteres españoles correctos",
    not faltan,
    f"faltan={faltan}" if faltan else "",
)

# 12/13. Estructura de tablas: thead en todas; filas indivisibles; cabecera repetible
n_tablas = html.count('<table class="data')
n_thead = html.count("<thead>")
check(
    "12/13. Todas las tablas usan <thead> (se repite al saltar de página)",
    n_tablas == n_thead,
    f"tablas={n_tablas}, thead={n_thead}",
)
check(
    "12b. Filas protegidas contra corte entre páginas (break-inside: avoid)",
    "table.data tr { break-inside: avoid" in html.replace("\n", " ").replace("  ", " ")
    or "break-inside: avoid" in html,
)

# Resumen
print("=" * 64)
if failures:
    print(f"RESULTADO: {len(failures)} verificación(es) FALLARON:")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
print("RESULTADO: TODAS las verificaciones pasaron.")
