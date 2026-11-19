"""Genera los Markdown de microcurriculos (fichas por area + tablas transversales).

Uso: python -I gen_micro.py <micro.json> <carpeta Laboratorio> <carpeta salida>
"""
import sys, os, re, json, collections, unicodedata

JSON_PATH, LAB_ROOT, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
MICRO_DIR = "Microcurriculos actualizados"
recs = json.load(open(JSON_PATH, encoding="utf-8"))
os.makedirs(OUT, exist_ok=True)

ORD = [("primer", 1), ("segundo", 2), ("tercer", 3), ("cuarto", 4), ("quinto", 5), ("sexto", 6),
       ("septimo", 7), ("octavo", 8), ("noveno", 9), ("decimo", 10), ("once", 11), ("undecimo", 11),
       ("doceavo", 12), ("doce", 12), ("duodecimo", 12)]


def norm(s):
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def sem_ord(text):
    t = norm(text)
    best = None
    for w_, n in ORD:
        m = re.search(r"\b" + w_, t)
        if m and (best is None or m.start() < best[0]):
            best = (m.start(), n)
    return best[1] if best else None


def esc(s):
    return (s or "").replace("|", "\\|").replace("\n", " ").strip()


def code_of(r):
    return r["header"].get("Código de asignatura", "").strip()


def name_of(r):
    return r["header"].get("Nombre completo de la asignatura", r["titulo_md"]).strip()


def num(s):
    m = re.search(r"(\d+)", s or "")
    return int(m.group(1)) if m else None


def totals(r):
    had = sum(c["had"] or 0 for c in r["contenido"])
    hti = sum(c["hti"] or 0 for c in r["contenido"])
    return had, hti


def eval_sum(r):
    return sum((e["porcentaje"] or 0) for e in r["evaluacion"])


def src_path(r):
    return f"{MICRO_DIR}\\{r['area_carpeta']}\\{r['archivo']}"


EMAIL = r"\s*[–-]?\s*\[?[\w.\-]+@[\w.\-]+\]?(\(mailto:[^)]*\))?"

for r in recs:
    r["codigo"] = code_of(r)
    r["nombre"] = name_of(r)
    r["sem_txt"] = r["header"].get("Semestre y año en que se imparte", "")
    r["sem_n"] = sem_ord(r["sem_txt"])
    r["creditos"] = num(r["header"].get("Número de créditos", ""))
    r["ects"] = num(r["header"].get("Número de créditos Europeos ECTS", ""))
    r["had"], r["hti"] = totals(r)
    r["area_hdr"] = r["header"].get("Área académica o categoría", "")
    r["coord"] = r["header"].get("Coordinador o contacto de la asignatura", "")
    r["direc"] = r["header"].get("Director o contacto del programa", "")
    r["upd"] = r["header"].get("Semestre y año de actualización", "")


def mdlink(s):
    return re.sub(r"\[([^\]]*)\]\(mailto:([^)]*)\)", r"\1 <\2>", s or "")


def w(path, lines):
    p = os.path.join(OUT, path)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines).rstrip() + "\n")
    return len(lines)


def ficha(r, n):
    L = []
    L.append(f"## {n}. {r['codigo']} · {r['nombre']}")
    L.append(f"> Fuente: `{src_path(r)}`")
    L.append("")
    L.append("| Dato | Valor |")
    L.append("|---|---|")
    L.append(f"| Código (encabezado) | {esc(r['codigo'])} |")
    L.append(f"| Tipo | {esc(r['tipo'])} |")
    L.append(f"| Área (encabezado) | {esc(r['area_hdr'])} |")
    L.append(f"| Se imparte en | {esc(r['sem_txt'])} |")
    L.append(f"| Actualización | {esc(r['upd'])} |")
    L.append(f"| Créditos / ECTS | {r['creditos']} / {r['ects']} |")
    had, hti = r["had"], r["hti"]
    L.append(f"| Horas según contenido | HAD {had} · HTI {hti} · total {had + hti} |")
    L.append(f"| Coordinador | {esc(mdlink(r['coord']))} |")
    L.append(f"| RAP del programa | {', '.join('RAP' + c for c in r['rap_codigos']) or '— (no identificado)'} |")
    L.append(f"| Formación integral | {esc('; '.join(r['formacion_integral_comp'])) or '— (no declarada)'} |")
    req = " ".join(r["requisitos"]).strip() or "— (no declarado)"
    L.append(f"| Requisito declarado | {esc(req)} |")
    if r["competencia_previa"]:
        L.append(f"| Competencia previa | {esc(r['competencia_previa'])} |")
    L.append("")
    L.append(f"**Descripción.** {r['breve_descripcion'] or '—'}")
    L.append("")
    L.append(f"**Objetivo de la asignatura.** {r['objetivo_asignatura'] or r['objetivos_raw'] or '—'}")
    L.append("")
    ra = r["resultados_asignatura"]
    L.append(f"**Resultados de aprendizaje de la asignatura ({len(ra)}).**")
    L.append("")
    for i, x in enumerate(ra, 1):
        L.append(f"{i}. {x}")
    if not ra:
        L.append("_No se pudieron identificar resultados de aprendizaje de la asignatura._")
    L.append("")
    L.append(f"**Contenido ({len(r['contenido'])} unidades).**")
    L.append("")
    L.append("| # | Unidad | Temas | HAD | HTI |")
    L.append("|--:|---|---|--:|--:|")
    for i, c in enumerate(r["contenido"], 1):
        t, d = c["titulo"], c["detalle"]
        if not t and d.startswith("Resultados de aprendizaje del programa, objetivos"):
            t, d = "Presentación del curso (sesión introductoria)", "Resultados de aprendizaje y objetivos, programa, cronograma y evaluación"
        if not t:
            t = "—"
        L.append(f"| {i} | {esc(t)} | {esc(d)} | {c['had'] if c['had'] is not None else '—'} | {c['hti'] if c['hti'] is not None else '—'} |")
    L.append(f"| | **Total** | | **{had}** | **{hti}** |")
    L.append("")
    for lab, items in r["didactica"].items():
        L.append(f"**Didáctica – {lab or 'general'}:** " + " ".join(items))
        L.append("")
    L.append("**Trabajos en laboratorio y proyectos:** " + (" ".join(r["lab_proyectos"]) or "—"))
    L.append("")
    for lab, items in r["metodos_aprendizaje_bloques"].items():
        L.append(f"**{lab or 'Métodos de aprendizaje'}:** " + "; ".join(items))
        L.append("")
    L.append("**Evaluación.**")
    L.append("")
    L.append("| Actividades | % |")
    L.append("|---|--:|")
    for e in r["evaluacion"]:
        L.append(f"| {esc('; '.join(e['actividades']))} | {e['porcentaje'] if e['porcentaje'] is not None else esc(e['porcentaje_raw'])} |")
    es = eval_sum(r)
    L.append(f"| **Suma de porcentajes** | **{es}%** |")
    if es != 100:
        L.append("")
        L.append(f"> ⚠ Los porcentajes del microcurrículo suman {es}% (no 100%).")
    L.append("")
    nb = sum(len(v) for v in r["recursos"].values())
    L.append(f"**Bibliografía y recursos:** {nb} referencias/recursos (detalle en `10_bibliografia_consolidada.md`).")
    L.append("")
    L.append("---")
    L.append("")
    return L


def area_header(rs):
    L = []
    progs = collections.OrderedDict()
    for r in rs:
        progs.setdefault(r["objetivo_programa"] or "—", []).append(r["codigo"])
    raps = collections.OrderedDict()
    for r in rs:
        raps.setdefault(r["rap_programa_raw"] or "—", []).append(r["codigo"])
    L.append("**Objetivo(s) del programa asociados al bloque** (texto tal como aparece en los microcurrículos):")
    L.append("")
    for t, cs_ in progs.items():
        L.append(f"- {t}  \n  _Asignaturas:_ {', '.join(cs_)}")
    L.append("")
    L.append("**Resultado(s) de aprendizaje del programa (RAP) referenciados:**")
    L.append("")
    for t, cs_ in raps.items():
        L.append(f"- {t}  \n  _Asignaturas:_ {', '.join(cs_)}")
    L.append("")
    return L


def area_file(fname, title, area, rs):
    L = [f"# {title}", ""]
    L.append(f"_Generado a partir de los microcurrículos en `{MICRO_DIR}\\{area}` · {len(rs)} asignatura(s) en este archivo._")
    L.append("")
    L.append("## Resumen del bloque")
    L.append("")
    L.append("| # | Código | Asignatura | Tipo | Se imparte en | Créd/ECTS | HAD | HTI | RAP |")
    L.append("|--:|---|---|---|---|---|--:|--:|---|")
    for i, r in enumerate(rs, 1):
        L.append(f"| {i} | {r['codigo']} | {esc(r['nombre'])} | {r['tipo']} | {esc(r['sem_txt'])} | {r['creditos']}/{r['ects']} | {r['had']} | {r['hti']} | {', '.join('RAP' + c for c in r['rap_codigos']) or '—'} |")
    L.append("")
    L.extend(area_header(rs))
    L.append("---")
    L.append("")
    for i, r in enumerate(rs, 1):
        L.extend(ficha(r, i))
    return w(fname, L)


def by_area(a):
    rs = [r for r in recs if r["area_carpeta"] == a]
    rs.sort(key=lambda r: (r["sem_n"] if r["sem_n"] else 99, r["codigo"]))
    return rs


A_ADM, A_FIN, A_IO, A_PROD, A_ELEC = [
    "Área Administrativa", "Área Financiera", "Área de Investigación de Operaciones y Estadística",
    "Área de Producción", "Electivas de formación profesional"]
AREAS = [A_ADM, A_FIN, A_IO, A_PROD, A_ELEC]
sizes = {}
sizes["02_area_administrativa.md"] = area_file("02_area_administrativa.md", "Área Administrativa – fichas de asignaturas", A_ADM, by_area(A_ADM))
sizes["03_area_financiera.md"] = area_file("03_area_financiera.md", "Área Financiera – fichas de asignaturas", A_FIN, by_area(A_FIN))
io = by_area(A_IO)
sizes["04_area_io_estadistica_parte1.md"] = area_file("04_area_io_estadistica_parte1.md", "Área de Investigación de Operaciones y Estadística – fichas (parte 1)", A_IO, io[:5])
sizes["05_area_io_estadistica_parte2.md"] = area_file("05_area_io_estadistica_parte2.md", "Área de Investigación de Operaciones y Estadística – fichas (parte 2)", A_IO, io[5:])
sizes["06_area_produccion.md"] = area_file("06_area_produccion.md", "Área de Producción – fichas de asignaturas", A_PROD, by_area(A_PROD))
el = by_area(A_ELEC)
sizes["07_electivas_parte1.md"] = area_file("07_electivas_parte1.md", "Electivas de formación profesional – fichas (parte 1)", A_ELEC, el[:5])
sizes["08_electivas_parte2.md"] = area_file("08_electivas_parte2.md", "Electivas de formación profesional – fichas (parte 2)", A_ELEC, el[5:])


def short_area(a):
    return a.replace("Área de ", "").replace("Área ", "")


def coord_name(r):
    return re.sub(EMAIL, "", r["coord"]).strip(" –-")


# ------------------------------------------------------------ 01 panorama
L = ["# Panorama general de los microcurrículos", ""]
L.append(f"_{len(recs)} microcurrículos analizados · 5 carpetas de área · plantilla institucional de 10 secciones._")
L.append("")
L.append("> **Semestres.** La columna «Se imparte en» reproduce lo que declara cada microcurrículo, que llega hasta el 12.º. **El programa tiene 10 semestres** y las **electivas profesionales** se ofrecen del 7.º al 10.º (dato confirmado por la Dirección). Para obligatorias, el primer dígito del código sugiere el semestre real (0 = 10.º); ver `13_requisitos_y_secuencia.md`.")
L.append("")
L.append("## 1. Distribución por carpeta de área")
L.append("")
L.append("| Carpeta | Asignaturas | Obligatorias | Electivas | HAD | HTI | Créditos |")
L.append("|---|--:|--:|--:|--:|--:|--:|")
for a in AREAS:
    rs = [r for r in recs if r["area_carpeta"] == a]
    L.append(f"| {a} | {len(rs)} | {sum(1 for r in rs if r['tipo']=='Obligatoria')} | {sum(1 for r in rs if r['tipo']=='Electiva')} | {sum(r['had'] for r in rs)} | {sum(r['hti'] for r in rs)} | {sum(r['creditos'] or 0 for r in rs)} |")
L.append(f"| **Total** | **{len(recs)}** | **{sum(1 for r in recs if r['tipo']=='Obligatoria')}** | **{sum(1 for r in recs if r['tipo']=='Electiva')}** | **{sum(r['had'] for r in recs)}** | **{sum(r['hti'] for r in recs)}** | **{sum(r['creditos'] or 0 for r in recs)}** |")
L.append("")
L.append("## 2. Inventario maestro")
L.append("")
L.append("| Carpeta | Código | Asignatura | Tipo | Se imparte en | Créd | ECTS | HAD | HTI | Actualización | Coordinador |")
L.append("|---|---|---|---|---|--:|--:|--:|--:|---|---|")
for a in AREAS:
    for r in by_area(a):
        L.append(f"| {short_area(a)} | {r['codigo']} | {esc(r['nombre'])} | {r['tipo']} | {esc(r['sem_txt'])} | {r['creditos']} | {r['ects']} | {r['had']} | {r['hti']} | {esc(r['upd'])} | {esc(coord_name(r))} |")
L.append("")
L.append("## 3. Responsables del programa y coordinadores")
L.append("")
dirs = collections.Counter(re.sub(EMAIL, "", r["direc"]).strip(" –-") for r in recs)
L.append("**Director del programa (variantes de escritura encontradas):**")
L.append("")
for k, v in dirs.most_common():
    L.append(f"- {k} ({v} microcurrículos)")
L.append("")
cs = collections.OrderedDict()
for r in recs:
    cs.setdefault(coord_name(r), []).append(r["codigo"])
L.append("**Coordinadores de asignatura (quién coordina qué):**")
L.append("")
L.append("| Coordinador | N.º | Asignaturas |")
L.append("|---|--:|---|")
for k, v in sorted(cs.items(), key=lambda x: -len(x[1])):
    L.append(f"| {esc(k) or '—'} | {len(v)} | {', '.join(v)} |")
L.append("")
L.append("## 4. Carga horaria observada")
L.append("")
std = [r for r in recs if (r["had"], r["hti"]) == (64, 80)]
L.append(f"- Estándar dominante: **HAD 64 + HTI 80 = 144 h** (3 créditos × 48 h). Lo cumplen {len(std)} de {len(recs)} microcurrículos.")
L.append("- Se desvían del estándar:")
for r in recs:
    if (r["had"], r["hti"]) != (64, 80):
        L.append(f"  - {r['codigo']} {r['nombre']}: HAD {r['had']} · HTI {r['hti']} (total {r['had'] + r['hti']}) — {r['creditos']} créditos / {r['ects']} ECTS")
sizes["01_panorama_asignaturas.md"] = w("01_panorama_asignaturas.md", L)

# ------------------------------------------------------------ 09 RAP
L = ["# Matriz de resultados de aprendizaje (RAP) y formación integral", ""]
raps = collections.OrderedDict()
for r in recs:
    for c in r["rap_codigos"]:
        raps.setdefault(c, collections.OrderedDict()).setdefault(r["rap_programa_raw"], []).append(r["codigo"])
L.append("## 1. RAP del programa y asignaturas que los declaran")
L.append("")
for c in sorted(raps, key=int):
    allc = [x for v in raps[c].values() for x in v]
    L.append(f"### RAP{c} — {len(allc)} asignaturas")
    L.append("")
    for txt, cl in raps[c].items():
        L.append(f"- _Redacción:_ {txt}")
        L.append(f"  - Asignaturas: {', '.join(cl)}")
    L.append("")
sin = [r for r in recs if not r["rap_codigos"]]
if sin:
    L.append("**Sin RAP identificado:** " + ", ".join(r["codigo"] for r in sin))
    L.append("")
L.append("## 2. Matriz asignatura × RAP")
L.append("")
allr = sorted(raps, key=int)
L.append("| Código | Asignatura | " + " | ".join("RAP" + c for c in allr) + " |")
L.append("|---|---|" + "|".join(":-:" for _ in allr) + "|")
for a in AREAS:
    for r in by_area(a):
        L.append(f"| {r['codigo']} | {esc(r['nombre'])} | " + " | ".join("●" if c in r["rap_codigos"] else "" for c in allr) + " |")
L.append("")
L.append("## 3. Resultados de aprendizaje de formación integral (competencias institucionales)")
L.append("")
comp = collections.OrderedDict()
for r in recs:
    for c in r["formacion_integral_comp"]:
        comp.setdefault(c, []).append(r["codigo"])
L.append("| Competencia | N.º | Asignaturas |")
L.append("|---|--:|---|")
for k, v in sorted(comp.items(), key=lambda x: -len(x[1])):
    L.append(f"| {esc(k)} | {len(v)} | {', '.join(v)} |")
L.append("")
L.append("## 4. Resultados de aprendizaje de asignatura: cantidad por microcurrículo")
L.append("")
L.append("| Código | Asignatura | N.º resultados |")
L.append("|---|---|--:|")
for r in sorted(recs, key=lambda r: len(r["resultados_asignatura"])):
    L.append(f"| {r['codigo']} | {esc(r['nombre'])} | {len(r['resultados_asignatura'])} |")
sizes["09_matriz_RAP_y_formacion_integral.md"] = w("09_matriz_RAP_y_formacion_integral.md", L)

# ------------------------------------------------------------ herramientas / TIC / evaluacion
TOOLS = [
    ("Excel", r"\bexcel\b"), ("Solver", r"\bsolver\b"), ("Python", r"\bpython\b"), ("R / RStudio", r"\brstudio\b|\blenguaje r\b|\bsoftware r\b"),
    ("SPSS", r"\bspss\b"), ("Minitab", r"\bminitab\b"), ("Statgraphics", r"\bstatgraphics\b"), ("Arena", r"\barena\b"),
    ("Simio", r"\bsimio\b"), ("FlexSim", r"\bflexsim\b"), ("ProModel", r"\bpromodel\b"), ("LINGO", r"\blingo\b"), ("GAMS", r"\bgams\b"),
    ("WinQSB / QM / TORA", r"\bwinqsb\b|\btora\b|\bqm for windows\b"), ("MATLAB", r"\bmatlab\b"), ("SAP / ERP", r"\bsap\b|\berp\b"),
    ("MS Project", r"\bms project\b|\bmicrosoft project\b"), ("SolidWorks / CAD", r"\bsolidworks\b|\bautocad\b|\bcad\b"),
    ("Power BI / Tableau", r"\bpower ?bi\b|\btableau\b"), ("SQL / Access", r"\bsql\b|\baccess\b"),
    ("Ergonautas", r"\bergonautas\b"), ("Logyca (cursos virtuales)", r"\blogyca\b"), ("Quick Pallet Maker / Sice-tac", r"quick pallet|sice-?tac"),
    ("Realidad virtual / aumentada", r"realidad virtual|realidad aumentada"), ("RFID / código de barras", r"\brfid\b|c[oó]digo de barras"),
    ("WMS / TMS", r"\bwms\b|\btms\b"), ("Lean / Kanban", r"\blean\b|\bkanban\b"), ("Six Sigma / DMAIC", r"six sigma|\bdmaic\b"),
    ("Jamboard / Padlet / Kahoot", r"jamboard|padlet|kahoot|mentimeter"), ("Google Drive / Classroom / Meet", r"google drive|classroom|google meet"),
    ("Moodle / Teams / Zoom", r"moodle|\bteams\b|\bzoom\b"), ("Bases de datos suscritas por la Universidad", r"bases de datos"),
    ("Simulación (genérico)", r"simulaci[oó]n"), ("Software (genérico)", r"software"),
]
LABS = [
    ("GEIO", r"\bgeio\b"), ("Laboratorio de logística", r"laboratorio de log"), ("Laboratorio de manufactura flexible", r"manufactura flexible"),
    ("Laboratorio financiero / Bolsa", r"laboratorio financiero|bolsa|bvc"), ("Consultorio empresarial", r"consultorio"),
    ("Laboratorio (genérico)", r"laboratorio"), ("Lúdicas", r"l[uú]dica"), ("Visita técnica / empresa", r"visita"),
    ("Proyecto final / trabajo final", r"proyecto final|trabajo final|trabajo de grupo|proyecto de"),
    ("Caso real / empresa real", r"empresa real|casos? real|empresas reales|caso de empresa"),
]


def full_text(r):
    parts = [r["breve_descripcion"], r["objetivo_asignatura"], " ".join(r["resultados_asignatura"]),
             " ".join(c["raw"] for c in r["contenido"]), " ".join(r["lab_proyectos"])]
    for d in (r["recursos"], r["didactica"], r["metodos_aprendizaje_bloques"]):
        for v in d.values():
            parts.append(" ".join(v))
    return norm(" ".join(parts))


FT = {r["archivo"]: full_text(r) for r in recs}

L = ["# Pedagogía, TIC, herramientas y evaluación", ""]
L.append("## 1. Herramientas y tecnologías mencionadas en los microcurrículos")
L.append("")
L.append("Detección automática por palabras clave sobre todo el texto de cada microcurrículo. Es una pista, no una auditoría: conviene confirmar en la ficha.")
L.append("")
L.append("| Herramienta / tema | N.º | Asignaturas |")
L.append("|---|--:|---|")
for name, pat in TOOLS:
    hit = [r["codigo"] for r in recs if re.search(pat, FT[r["archivo"]])]
    if hit:
        L.append(f"| {name} | {len(hit)} | {', '.join(hit)} |")
L.append("")
L.append("## 2. Estrategias TIC declaradas por asignatura (sección 9)")
L.append("")
for a in AREAS:
    L.append(f"### {a}")
    L.append("")
    for r in by_area(a):
        tic = r["metodos_aprendizaje_bloques"].get("Estrategias TIC", [])
        L.append(f"- **{r['codigo']} {r['nombre']}:** " + ("; ".join(tic) if tic else "— (sin estrategias TIC declaradas)"))
    L.append("")
L.append("## 3. Métodos de aprendizaje declarados (sección 9)")
L.append("")
for a in AREAS:
    L.append(f"### {a}")
    L.append("")
    for r in by_area(a):
        ma = r["metodos_aprendizaje_bloques"].get("", [])
        L.append(f"- **{r['codigo']} {r['nombre']}:** " + ("; ".join(ma) if ma else "—"))
    L.append("")
L.append("## 4. Evaluación: estructura y consistencia")
L.append("")
L.append("| Código | Asignatura | Filas | Porcentajes declarados | Suma | ¿100%? |")
L.append("|---|---|--:|---|--:|:-:|")
for a in AREAS:
    for r in by_area(a):
        ps = [e["porcentaje"] for e in r["evaluacion"]]
        s = eval_sum(r)
        L.append(f"| {r['codigo']} | {esc(r['nombre'])} | {len(ps)} | {' + '.join(str(p) for p in ps)} | {s} | {'sí' if s == 100 else 'NO'} |")
L.append("")
bad = [r for r in recs if eval_sum(r) != 100]
L.append(f"**{len(bad)} de {len(recs)}** microcurrículos no suman 100% en la tabla de evaluación: " + ", ".join(f"{r['codigo']} ({eval_sum(r)}%)" for r in bad) + ".")
sizes["11_pedagogia_tic_y_evaluacion.md"] = w("11_pedagogia_tic_y_evaluacion.md", L)

# ------------------------------------------------------------ 12 labs/proyectos
L = ["# Laboratorios, proyectos y trabajo práctico en los microcurrículos", ""]
L.append("Fuente: sección 8 (*Trabajos en Laboratorio y Proyectos*) de cada microcurrículo, más menciones detectadas a espacios de laboratorio en el resto del texto.")
L.append("")
L.append("## 1. Qué declara cada asignatura (sección 8, texto original)")
L.append("")
for a in AREAS:
    L.append(f"### {a}")
    L.append("")
    for r in by_area(a):
        L.append(f"- **{r['codigo']} {r['nombre']}:** " + (" ".join(r["lab_proyectos"]) or "—"))
    L.append("")
L.append("## 2. Menciones a laboratorios y espacios prácticos detectadas en todo el texto")
L.append("")
L.append("| Espacio / actividad | N.º | Asignaturas |")
L.append("|---|--:|---|")
for name, pat in LABS:
    hit = [r["codigo"] for r in recs if re.search(pat, FT[r["archivo"]])]
    if hit:
        L.append(f"| {name} | {len(hit)} | {', '.join(hit)} |")
L.append("")
L.append("## 3. Asignaturas cuya sección 8 no menciona laboratorio, taller, proyecto, caso, visita, informe ni práctica")
L.append("")
nolab = [r for r in recs if not re.search(r"laborat|proyecto|caso|visita|taller|simula|informe|trabajo|practica", norm(" ".join(r["lab_proyectos"])))]
for r in nolab:
    L.append(f"- {r['codigo']} {r['nombre']}: «{' '.join(r['lab_proyectos'])}»")
if not nolab:
    L.append("- Ninguna (todas declaran algún trabajo práctico, taller, proyecto o caso).")
sizes["12_laboratorios_y_proyectos_en_microcurriculos.md"] = w("12_laboratorios_y_proyectos_en_microcurriculos.md", L)

# ------------------------------------------------------------ 13 requisitos
L = ["# Requisitos, prerrequisitos y secuencia", ""]
L.append("| Carpeta | Código | Asignatura | Se imparte en | Requisito declarado | Competencia previa |")
L.append("|---|---|---|---|---|---|")
for a in AREAS:
    for r in by_area(a):
        L.append(f"| {short_area(a)} | {r['codigo']} | {esc(r['nombre'])} | {esc(r['sem_txt'])} | {esc(' '.join(r['requisitos'])) or '—'} | {esc(r['competencia_previa']) or '—'} |")
L.append("")
L.append("## Secuencia por semestre declarado (hasta el 12.º; no válido para una malla de 10)")
L.append("")
by_sem = collections.defaultdict(list)
for r in recs:
    by_sem[r["sem_n"]].append(r)
for k in sorted(by_sem, key=lambda x: (x is None, x)):
    L.append(f"- **{'Semestre ' + str(k) if k else 'Sin semestre reconocido'}:** " + "; ".join(f"{r['codigo']} {r['nombre']}" for r in by_sem[k]))
L.append("")
L.append("## Secuencia en la malla de 10 semestres (inferida del primer dígito del código; 0 = 10.º)")
L.append("")
L.append("Las **electivas profesionales** se ofrecen del 7.º al 10.º y no tienen dígito de semestre en el código.")
L.append("")


def semm_(r):
    if r["tipo"] == "Electiva":
        return None
    mm = re.match(r"^II(\d)", r["codigo"])
    return (10 if mm.group(1) == "0" else int(mm.group(1))) if mm else None


by_m = collections.defaultdict(list)
for r in recs:
    by_m[semm_(r)].append(r)
for k in sorted(by_m, key=lambda x: (x is None, x)):
    L.append(f"- **{('Semestre ' + str(k)) if k else 'Electivas (7.º–10.º)'}:** " + "; ".join(f"{r['codigo']} {r['nombre']}" for r in by_m[k]))
L.append("")
L.append("**Verificación de requisitos con esta malla:** salvo tres casos, cada requisito cae en un semestre anterior: Contabilidad de Empresas (2.º) exige Economía (3.º); Sicología Organizacional (3.º) exige Administración (3.º) y Simulación (8.º) exige Investigación de Operaciones II (8.º), en el mismo semestre. La contradicción que aparecía en Producción con los semestres declarados desaparece.")
sizes["13_requisitos_y_secuencia.md"] = w("13_requisitos_y_secuencia.md", L)

# ------------------------------------------------------------ 10 bibliografia
YEAR = re.compile(r"\b(19[5-9]\d|20[0-2]\d)\b")
entries = []
for r in recs:
    for lab, items in r["recursos"].items():
        for it in items:
            m = YEAR.search(it)
            entries.append({"cod": r["codigo"], "nom": r["nombre"], "area": r["area_carpeta"], "lab": lab, "txt": it, "year": int(m.group(1)) if m else None})
L = ["# Bibliografía y recursos consolidados", ""]
L.append(f"_{len(entries)} entradas (bibliografía, recursos audiovisuales, web) extraídas de la sección 6 de los 39 microcurrículos._")
L.append("")
yrs = [e["year"] for e in entries if e["year"]]
L.append("## 1. Indicadores de vigencia (año de publicación detectado)")
L.append("")
L.append(f"- Entradas con año detectable: {len(yrs)} de {len(entries)}")
if yrs:
    L.append(f"- Año más antiguo: {min(yrs)} · más reciente: {max(yrs)} · mediana: {sorted(yrs)[len(yrs)//2]}")
    for lo, hi, lab in [(1950, 1999, "anteriores a 2000"), (2000, 2009, "2000–2009"), (2010, 2014, "2010–2014"), (2015, 2019, "2015–2019"), (2020, 2029, "2020 o posterior")]:
        L.append(f"- {lab}: {sum(1 for y in yrs if lo <= y <= hi)}")
L.append("")
L.append("### Vigencia por carpeta de área")
L.append("")
L.append("| Carpeta | Entradas | Con año | Mediana | ≤1999 | ≥2015 |")
L.append("|---|--:|--:|--:|--:|--:|")
for a in AREAS:
    es_ = [e for e in entries if e["area"] == a]
    ys = sorted(e["year"] for e in es_ if e["year"])
    L.append(f"| {a} | {len(es_)} | {len(ys)} | {ys[len(ys)//2] if ys else '—'} | {sum(1 for y in ys if y <= 1999)} | {sum(1 for y in ys if y >= 2015)} |")
L.append("")
keyd = collections.defaultdict(list)
for e in entries:
    k = re.sub(r"[^a-z0-9]", "", norm(e["txt"]))[:36]
    if len(k) > 20:
        keyd[k].append(e)
dups = {k: v for k, v in keyd.items() if len({x["cod"] for x in v}) > 1}
L.append("## 2. Referencias compartidas entre asignaturas (coincidencia aproximada)")
L.append("")
if dups:
    for k, v in dups.items():
        L.append(f"- {v[0]['txt'][:160]}  \n  _Usada en:_ {', '.join(sorted({x['cod'] for x in v}))}")
else:
    L.append("- No se detectaron referencias idénticas compartidas entre asignaturas.")
L.append("")
L.append("## 3. Referencias anteriores a 2000 (revisar vigencia)")
L.append("")
old = [e for e in entries if e["year"] and e["year"] < 2000]
for e in sorted(old, key=lambda e: e["year"]):
    L.append(f"- ({e['year']}) {e['cod']} {e['nom']}: {e['txt'][:170]}")
if not old:
    L.append("- Ninguna.")
L.append("")
L.append("## 4. Listado completo por asignatura")
L.append("")
for a in AREAS:
    L.append(f"### {a}")
    L.append("")
    for r in by_area(a):
        L.append(f"**{r['codigo']} {r['nombre']}**")
        L.append("")
        any_ = False
        for lab, items in r["recursos"].items():
            for it in items:
                L.append(f"- {('[' + lab + '] ') if lab else ''}{it}")
                any_ = True
        if not any_:
            L.append("- — (sin recursos declarados)")
        L.append("")
sizes["10_bibliografia_consolidada.md"] = w("10_bibliografia_consolidada.md", L)

# ------------------------------------------------------------ 14 hallazgos
L = ["# Hallazgos de calidad de datos (detección automática)", ""]
L.append("Observaciones sobre consistencia, completitud y forma de los microcurrículos. Son hallazgos para depurar, no juicios sobre el contenido académico.")
L.append("")
cnt = collections.defaultdict(list)
for r in recs:
    cnt[r["codigo"]].append(r)
L.append("## 1. Códigos de asignatura repetidos")
L.append("")
for c, rs in cnt.items():
    if len(rs) > 1:
        L.append(f"- **{c}** está en {len(rs)} microcurrículos: " + "; ".join(f"{r['nombre']} ({r['tipo']}, carpeta {r['area_carpeta']})" for r in rs))
L.append("")
L.append("## 2. Nombres de archivo: desajustes y marcas de borrador")
L.append("")
for r in recs:
    if not r["archivo"].startswith(r["codigo"]):
        L.append(f"- Archivo `{r['archivo']}` vs. código del encabezado `{r['codigo']}`")
for r in recs:
    if re.search(r"\(\d\)|Observaciones|Propuesta", r["archivo"]):
        L.append(f"- Marca de borrador/versión en el nombre: `{r['archivo']}`")
L.append("")
L.append("## 3. Área del encabezado vs. carpeta")
L.append("")
for r in recs:
    carp, ah = norm(r["area_carpeta"]), norm(r["area_hdr"])
    if ah not in carp and not (ah.startswith("investig") and "investig" in carp):
        L.append(f"- {r['codigo']} {r['nombre']}: carpeta «{r['area_carpeta']}» · encabezado «{r['area_hdr']}»")
L.append("")
L.append("## 4. Dígito del código vs. semestre declarado")
L.append("")
L.append("El primer dígito del código (p. ej. II**6**A3) sugiere el semestre en una malla de 10 semestres (0 = 10.º); se compara con el semestre que declara el microcurrículo, que llega hasta el 12.º y por tanto no es válido para un programa de 10.")
L.append("")
L.append("| Código | Asignatura | Dígito | Semestre declarado | ¿Coincide? |")
L.append("|---|---|--:|---|:-:|")
for r in recs:
    m = re.match(r"^II(\d)", r["codigo"])
    dg = int(m.group(1)) if m else None
    ok = "—" if dg is None or r["sem_n"] is None else ("sí" if dg == r["sem_n"] else "NO")
    L.append(f"| {r['codigo']} | {esc(r['nombre'])} | {dg if dg is not None else '—'} | {esc(r['sem_txt'])} | {ok} |")
L.append("")
L.append("## 5. Estructura de la plantilla")
L.append("")
raw_issues = []
for r in recs:
    p = os.path.join(LAB_ROOT, MICRO_DIR, r["area_carpeta"], r["archivo"])
    t = open(p, encoding="utf-8").read()
    raw_issues.append((r, len(re.findall(r"^###\s+3\.\s+Resultados de Aprendizaje", t, re.M)),
                       len(re.findall(r"\(HT\s*:", t)), not re.search(r"^###\s+4\.\s+Contenido", t, re.M)))
L.append(f"- Encabezado «### 3. Resultados de Aprendizaje» repetido dentro de Contenido (artefacto de plantilla): {sum(1 for x in raw_issues if x[1] > 1)} microcurrículos.")
L.append("- Abreviatura «(HT: n)» en lugar de «(HTI: n)»: " + (", ".join(x[0]["codigo"] for x in raw_issues if x[2]) or "ninguno") + ".")
L.append("- Sin encabezado «### 4. Contenido» (texto corrupto): " + (", ".join(x[0]["codigo"] for x in raw_issues if x[3]) or "ninguno") + ".")
L.append("")
L.append("## 6. Contenido sin horas, horas atípicas y evaluación inconsistente")
L.append("")
for r in recs:
    nh = [c for c in r["contenido"] if c["had"] is None]
    if nh:
        L.append(f"- {r['codigo']} {r['nombre']}: {len(nh)} de {len(r['contenido'])} unidades sin horas HAD/HTI.")
for r in recs:
    if (r["had"], r["hti"]) != (64, 80):
        L.append(f"- {r['codigo']} {r['nombre']}: horas atípicas HAD {r['had']} / HTI {r['hti']}.")
for r in recs:
    if eval_sum(r) != 100:
        L.append(f"- {r['codigo']} {r['nombre']}: evaluación suma {eval_sum(r)}%.")
L.append("")
L.append("## 7. Campos faltantes o anómalos")
L.append("")
for r in recs:
    pr = []
    if not r["rap_codigos"]:
        pr.append("sin RAP identificado")
    if not r["formacion_integral_comp"]:
        pr.append("sin competencias de formación integral")
    if len(r["resultados_asignatura"]) <= 1:
        pr.append(f"solo {len(r['resultados_asignatura'])} resultado(s) de aprendizaje de la asignatura")
    if not " ".join(r["requisitos"]).strip():
        pr.append("sin requisito declarado")
    if not r["recursos"]:
        pr.append("sin bibliografía/recursos")
    if "Estrategias TIC" not in r["metodos_aprendizaje_bloques"]:
        pr.append("sin estrategias TIC")
    if pr:
        L.append(f"- {r['codigo']} {r['nombre']}: " + "; ".join(pr))
L.append("")
L.append("## 8. Semestres declarados fuera de la malla de 10 (11.º y 12.º)")
L.append("")
for r in recs:
    if r["sem_n"] is None or r["sem_n"] > 10:
        L.append(f"- {r['codigo']} {r['nombre']}: «{r['sem_txt']}»")
sizes["14_hallazgos_calidad_datos.md"] = w("14_hallazgos_calidad_datos.md", L)

for k in sorted(sizes):
    print(k, sizes[k], "lineas")
