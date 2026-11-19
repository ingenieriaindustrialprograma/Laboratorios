"""Genera la presentacion HTML interactiva (un solo archivo, sin dependencias).

Uso: python -I gen_presentacion.py <micro.json> <plantilla.html> <salida.html> <carpeta asignacion>
"""
import sys, os, re, json, collections, statistics

JSON_PATH, TEMPLATE, OUT_HTML, ASIG_DIR = sys.argv[1:5]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.argv = ["gen_asignacion.py", JSON_PATH, ASIG_DIR]
import gen_asignacion as G  # noqa: E402  (regenera de forma idempotente los .md de asignacion)

norm = G.norm
AREA_SHORT = {"Área Administrativa": "Administrativa", "Área Financiera": "Financiera",
              "Área de Investigación de Operaciones y Estadística": "IO y Estadística",
              "Área de Producción": "Producción", "Electivas de formación profesional": "Electivas"}
LABIDS = ["FIN", "GEIO", "LOG", "MF", "CON"]


def nm(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", norm(s))).strip()


subjects = []
for idx, i in enumerate(G.items):
    r = i["r"]
    h = r["header"]
    subjects.append(dict(
        id=idx, code=r["codigo"], name=r["nombre"], area=AREA_SHORT[r["area_carpeta"]], areaHdr=r["header"].get("Área académica o categoría", ""),
        type=r["tipo"], sem=r["semm"], semDecl=r["sem_n"], semTxt=r["sem_txt"], cred=G.num(h.get("Número de créditos", "")), ects=G.num(h.get("Número de créditos Europeos ECTS", "")),
        had=r["had"], hti=r["hti"], upd=h.get("Semestre y año de actualización", ""),
        coord=re.sub(r"\s*[–-]?\s*\[?[\w.\-]+@[\w.\-]+\]?(\(mailto:[^)]*\))?", "", h.get("Coordinador o contacto de la asignatura", "")).strip(" –-"),
        rap=["RAP" + c for c in r["rap_codigos"]], comps=r["formacion_integral_comp"], req=" ".join(r["requisitos"]).strip(),
        desc=r["breve_descripcion"], obj=r["objetivo_asignatura"] or r["objetivos_raw"], outcomes=r["resultados_asignatura"],
        units=[dict(t=c["titulo"] or "", d=c["detalle"], had=c["had"], hti=c["hti"]) for c in r["contenido"]],
        eval=[dict(a="; ".join(e["actividades"]), p=e["porcentaje"]) for e in r["evaluacion"]], evalSum=r["eval_sum"],
        lab8=" ".join(r["lab_proyectos"]).strip(), tic=r["metodos_aprendizaje_bloques"].get("Estrategias TIC", []),
        methods=r["metodos_aprendizaje_bloques"].get("", []), bibN=sum(len(v) for v in r["recursos"].values()),
        archivo=r["archivo"], carpeta=AREA_SHORT[r["area_carpeta"]],
        generic=(r["codigo"] == "II123"),
        asg=dict(prim=i["prim"], comps=i["comps"], fit=i["fit"], mod=i["mod"], estado=i["estado"], peso=i["peso"], horas=i["horas"],
                 why=i["why"], pract=i["pract"], prod=i["prod"], conv=i["conv"], antes=i["antes"]),
    ))
byid = {s["id"]: s for s in subjects}
code2id = collections.defaultdict(list)
for s in subjects:
    code2id[s["code"]].append(s["id"])

# ----------------------------- prerrequisitos
alias = {}
for s in subjects:
    alias.setdefault(nm(s["name"]), s["id"])
for a, code in [("informatica ii", "II212"), ("psicologia organizacional", "II321"), ("sistemas de costeo", "II4A3"),
                ("diseno de plantas", "II9B2"), ("diseno de planta", "II9B2"), ("administracion de salarios", "II6C3")]:
    alias[a] = code2id[code][0]
for s in subjects:
    ids, ext, note = [], [], ""
    txt = s["req"]
    for frag in re.split(r"\s*[-–—]\s*", txt):
        f = frag.strip(" .;")
        if not f:
            continue
        n = nm(f)
        if n in alias:
            ids.append(alias[n])
        elif "semestre" in n:
            note = f
        elif n in ("ninguno", "sin requisito"):
            pass
        else:
            ext.append(f)
    s["reqIds"], s["reqExt"], s["reqNote"] = ids, ext, note

# ----------------------------- hallazgos
findings = []
dups = collections.defaultdict(list)
for s in subjects:
    dups[s["code"]].append(s["id"])
findings.append(dict(k="Códigos repetidos", sev="alto", desc="El mismo código identifica asignaturas distintas.", ids=[x for v in dups.values() if len(v) > 1 for x in v]))
findings.append(dict(k="Evaluación que no suma 100 %", sev="alto", desc="La tabla de métodos de evaluación no totaliza 100 %.", ids=[s["id"] for s in subjects if s["evalSum"] != 100]))
seq, same = [], []
for s in subjects:
    for j in s["reqIds"]:
        a, b = s["sem"], byid[j]["sem"]
        if a and b:
            if b > a:
                seq.append((s["id"], j))
            elif b == a:
                same.append((s["id"], j))
findings.append(dict(k="Secuencia contradictoria", sev="alto", desc="El requisito está en un semestre posterior al de la asignatura que lo exige (malla de 10 semestres, según el primer dígito del código).", ids=sorted({x for p in seq for x in p}), pairs=seq))
findings.append(dict(k="Sección de laboratorio vacía", sev="medio", desc="La sección 8 (trabajos en laboratorio y proyectos) no tiene contenido.", ids=[s["id"] for s in subjects if not s["lab8"] or s["lab8"] in ("—", "-")]))
findings.append(dict(k="Horas distintas del estándar", sev="medio", desc="El contenido no suma 64 HAD + 80 HTI (3 créditos × 48 h).", ids=[s["id"] for s in subjects if (s["had"], s["hti"]) != (64, 80)]))
findings.append(dict(k="Unidades sin horas", sev="medio", desc="Hay unidades de contenido sin HAD/HTI.", ids=[s["id"] for s in subjects if any(u["had"] is None for u in s["units"])]))
findings.append(dict(k="Sin estrategias TIC", sev="bajo", desc="No declara estrategias TIC.", ids=[s["id"] for s in subjects if not s["tic"]]))
findings.append(dict(k="Sin coordinador", sev="medio", desc="El encabezado no nombra al coordinador.", ids=[s["id"] for s in subjects if not s["coord"]]))
findings.append(dict(k="Semestre declarado fuera de la malla de 10", sev="alto", desc="El microcurrículo declara 11.º o 12.º semestre; el programa tiene 10 semestres.", ids=[s["id"] for s in subjects if (s["semDecl"] or 0) > 10]))
findings.append(dict(k="Archivo con marca de borrador", sev="bajo", desc="El nombre del archivo incluye «(1)», «Observaciones» o «Propuesta».", ids=[s["id"] for s in subjects if re.search(r"\(\d\)|Observaciones|Propuesta", s["archivo"])]))
findings.append(dict(k="Requisito en el mismo semestre", sev="medio", desc="La asignatura y su requisito caen en el mismo semestre de la malla de 10.", ids=sorted({x for p in same for x in p}), pairs=same))
findings.append(dict(k="Sin formación integral o con 1 resultado", sev="bajo", desc="Campos incompletos en resultados de aprendizaje.", ids=[s["id"] for s in subjects if not s["comps"] or len(s["outcomes"]) <= 1]))

# ----------------------------- bibliografia y herramientas
YEAR = re.compile(r"\b(19[5-9]\d|20[0-2]\d)\b")
years = []
by_area_years = collections.defaultdict(list)
for i in G.items:
    r = i["r"]
    for lab, its in r["recursos"].items():
        for it in its:
            m = YEAR.search(it)
            if m:
                y = int(m.group(1))
                years.append(y)
                by_area_years[AREA_SHORT[r["area_carpeta"]]].append(y)
bib = dict(years=sorted(years), median=statistics.median(years), byArea={k: dict(n=len(v), med=statistics.median(v)) for k, v in by_area_years.items()},
           total=sum(s["bibN"] for s in subjects))
TOOLS = [("Excel", r"\bexcel\b"), ("R / RStudio", r"\brstudio\b|\blenguaje r\b|\bsoftware r\b|\br y rstudio"), ("SPSS", r"\bspss\b"), ("MATLAB", r"\bmatlab\b"), ("Minitab", r"\bminitab\b"),
         ("Python", r"\bpython\b"), ("ProModel / FlexSim", r"promodel|flexsim"), ("AMPL / Solver / LINGO", r"\bampl\b|\bsolver\b|\blingo\b"), ("Lekin", r"\blekin\b"),
         ("Realidad virtual", r"realidad virtual"), ("RFID / código de barras", r"\brfid\b|c[oó]digo de barras"), ("Lean / Kanban", r"\blean\b|\bkanban\b"),
         ("Classroom / Meet / Zoom", r"classroom|google meet|\bzoom\b"), ("Jamboard / Padlet", r"jamboard|padlet"), ("Bases de datos de la Universidad", r"bases de datos")]
tools = []
for name, pat in TOOLS:
    hit = []
    for i in G.items:
        r = i["r"]
        parts = [r["breve_descripcion"], " ".join(c["raw"] for c in r["contenido"]), " ".join(r["lab_proyectos"])]
        for d in (r["recursos"], r["didactica"], r["metodos_aprendizaje_bloques"]):
            for v in d.values():
                parts.append(" ".join(v))
        if re.search(pat, norm(" ".join(parts))):
            hit.append(i["r"]["codigo"] + ("|" + i["r"]["nombre"] if len(code2id[i["r"]["codigo"]]) > 1 else ""))
    ids = [s["id"] for s in subjects if s["code"] + ("|" + s["name"] if len(code2id[s["code"]]) > 1 else "") in hit]
    tools.append(dict(name=name, ids=ids))

# ----------------------------- laboratorios
def ids_of(pairs):
    return [G.find(c, k)["codigo"] and next(s["id"] for s in subjects if s["code"] == c and norm(k) in norm(s["name"])) for c, k in pairs]


CLAIMS = {
    "FIN": ([("II6A3", ""), ("II8C3", ""), ("II4A3", ""), ("II152", ""), ("II212", ""), ("II4D3", ""), ("II7D3", ""), ("II8B3", "")], ["Mercado de Capitales"]),
    "GEIO": ([], []),
    "LOG": ([("II742", ""), ("II8A3", ""), ("II9C3", ""), ("II0D3", ""), ("II883", ""), ("II863", ""), ("II9B2", ""), ("II0F3", ""), ("IIP01", "Log"), ("IIA03", "")],
            ["GB273 Gerencia de Operaciones", "GB353 Gestión Tecnológica e Innovación (¿UV093?)", "II972 Seminario de Investigación"]),
    "MF": ([("II742", ""), ("II8A3", ""), ("II9C3", ""), ("II0D3", ""), ("II9B2", ""), ("II0F3", "")], ["Semillero de Investigación"]),
    "CON": ([("II7A3", ""), ("II8D3", "Mercados II")], ["Planeación Financiera"]),
}
COB_ITEMS = ["Responsable y contacto", "Ubicación y estado actual", "Inventario con cantidades y estado", "Capacidad simultánea", "Requisitos / competencias previas",
             "Normas de seguridad o conducta", "Procedimiento de acceso", "Necesidades y limitaciones", "Cifras de uso", "Asignaturas relacionadas (lista)"]
COB = {"FIN": [0, 2, 1, 0, 0, 0, 1, 1, 2, 2], "GEIO": [2, 0, 0, 0, 0, 0, 1, 0, 0, 0], "LOG": [0, 0, 2, 2, 2, 2, 2, 2, 1, 2],
       "MF": [2, 0, 0, 0, 0, 0, 0, 0, 0, 2], "CON": [2, 2, 2, 1, 2, 2, 2, 2, 2, 2]}
LABS = {
    "FIN": dict(name="Laboratorio Financiero", color="#009E73", fuente="Copia de Laboratorio_Financiero_FACIEM.pdf (3 pp.)", fecha="sin fecha",
                nat="Formación complementaria en finanzas, abierta a todos los programas; docencia, investigación y extensión con el Semillero de II.",
                loc="Edificio 15C, oficina 307", estado="Sin espacio propio: asignado a personal administrativo tras el sismo de agosto de 2026.", contacto="Equipo: A. M. Santa Alvarado, J. S. Arias Hernández, M. E. Bernal Loaiza, L. M. Marín Romero",
                recursos=["Alianza con bvc (2015) y Nuam Exchange: conferencias, cursos certificados", "Pantallas e-bvc con el mercado en tiempo real", "Bolsa Millonaria (bvc y trii): dinero ficticio, mesa de dinero, lúdicas", "Bases de datos con IA y guías para descargar indicadores y estados financieros bancarios", "6 computadores de escritorio, 3 portátiles, 2 pantallas de mercado"],
                actividades=["Docencia: Ruta de aprendizaje modular (2026-1: 3 módulos, 11 sesiones, 22 h)", "Investigación: Semillero y grupo DEA (educación financiera, mercado eléctrico)", "Extensión: finanzas personales, lúdicas de mercado de capitales, colegios", "Eventos: Semana FACIEM, Expo U, PDI FEST"],
                impacto=[("275", "participantes en la Ruta 2026-1"), ("1.289", "personas en extensión 2025 (20 actividades)"), ("5.º", "nacional en Bolsa Millonaria 2025 (97 participantes)"), ("Premio ACOFI 2025", "5.º Congreso Latinoamericano EIEI")],
                competencias=["Cultura financiera y lectura del mercado de valores (deducida)", "Análisis de datos financieros y modelación cuantitativa (deducida)", "Uso de IA en investigación y habilidades en entornos digitales (módulos 2026-1)"],
                requisitos="Ninguno declarado: abierto a cualquier programa.", necesidades=["Recuperar un espacio propio"]),
    "GEIO": dict(name="Laboratorio GEIO", color="#E69F00", fuente="Informe_Laboratorio_GEIO_UTP (1).docx", fecha="sin fecha",
                 nat="Grupo en la Enseñanza de la Investigación de Operaciones: aprendizaje activo con lúdicas, gamificación y simulación; semillero y transferencia.",
                 loc="No indicada", estado="No informa.", contacto="geio@utp.edu.co · WhatsApp +57 318 806 9722 · @geio_utp",
                 recursos=["Kits de lúdicas: producción en serie, Kanban, Beer Game, ensamblaje por celdas, colas", "Software declarado: Arena, Simio, FlexSim, Gurobi, CPLEX, Python/PuLP (por verificar)", "Metodologías: gamificación, ABP, Design Thinking, aprender haciendo", "Aulas taller y mesas modulares configurables"],
                 actividades=["Diseño y ejecución de lúdicas pedagógicas", "Semillero: optimización, simulación, heurísticas, analítica prescriptiva", "Portafolio de capacitaciones (Lean, Six Sigma, operaciones) para empresas", "Red Iddeal y visitas guiadas de colegios y gremios"],
                 impacto=[("10", "microcurrículos ya citan al GEIO"), ("Sin cifras", "el informe no reporta participantes ni sesiones")],
                 competencias=["Liderazgo bajo presión y negociación", "Comunicación efectiva", "Toma de decisiones basada en datos", "Pensamiento crítico y resolución colaborativa"],
                 requisitos="Ninguno declarado.", necesidades=["No declara necesidades"]),
    "LOG": dict(name="Laboratorio de Logística", color="#0072B2", fuente="reporte laboratorio de logística.pdf (6 pp.)", fecha="2026",
                nat="Experimentación con identificación y captura de datos, realidad virtual y aumentada para almacenamiento, inventarios, transporte y distribución.",
                loc="Sala 5-111", estado="El informe no menciona el estado de la sala tras el sismo.", contacto="No indicado",
                recursos=["17 grupos de equipos con placa: RFID (RF Code M250, ThingMagic), lectores de barras, Zebra ZT410, Oculus", "7 computadores (2010–2015) sin compatibilidad con Windows 11", "Software obsoleto o demo; solo Zebra Designer Pro (2024) en condiciones", "Dron DJI Phantom 3 (no vuela, para baja), góndola inteligente (rehacer)"],
                actividades=["Prácticas de inventarios, trazabilidad, picking, autoservicio, bases de datos", "Talleres para II, Administración, Esp. en Logística Empresarial, Tecnología en Gestión Logística", "Apoyo logístico a eventos y visitas institucionales", "Semillero y línea de logística del GEIO"],
                impacto=[("4", "estudiantes simultáneos en el mejor caso (16 en demostración)"), (">2.000", "estudiantes potenciales"), ("COP 42,1 M", "compra PARCE 2026 aprobada, sin entregar")],
                competencias=["Identificación y captura automática de datos (barras, RFID, NFC)", "Diseño y control de procesos de almacén", "Indicadores y análisis de datos logísticos", "Tecnologías inmersivas (VR/AR)"],
                requisitos="Ofimática básica; inducción en cada práctica y capacitación previa para gafas VR; subgrupos de máx. 16.", necesidades=["Reposición de cómputo y software (prioridad 1)", "Entrega de la compra PARCE 2026", "Licencias de WMS y simulación logística", "Dar de baja el dron; rehacer la góndola"]),
    "MF": dict(name="Laboratorio de Manufactura Flexible", color="#D55E00", fuente="Informe Laboratorio de Manufactura Flexible.pdf (8 pp.) + copia sin encabezado", fecha="10 de octubre de 2026",
               nat="Manufactura, ensamble y gestión de operaciones con equipos industriales, automatización, fabricación digital, simulación y realidad virtual (Industria 4.0).",
               loc="Bloque 5 – 109", estado="El informe no menciona el estado del bloque tras el sismo.", contacto="Director: John Andrés Muñoz Guevara · johandmunoz@utp.edu.co",
               recursos=["Robots ABB IRB 120 y Mitsubishi RV-2AJ", "Centro de mecanizado CNC e impresoras 3D", "Fischertechnik, visión artificial Cognex, PLC Siemens", "Gafas Meta Quest 2 y celda de manufactura y ensamble flexible", "Software: RobotStudio, SolidWorks, Unreal Engine, FlexSim"],
               actividades=["Diseño y análisis de puestos con VR, balanceo de líneas, scheduling", "Programación de robots, CNC, fabricación aditiva, PLC y visión artificial", "Modelos 3D de estaciones y plantas; integración CAD–entornos 3D", "Investigación aplicada en scheduling, optimización, simulación y robótica"],
               impacto=[("8", "equipos principales"), ("4", "plataformas de software"), ("Sin cifras", "no reporta uso ni estudiantes atendidos")],
               competencias=["Competencias tecnológicas: robótica, CNC, PLC, visión, VR", "Análisis, diseño y mejora de sistemas productivos", "Competencias para Industria 4.0"],
               requisitos="No declarados. La sección «Normas de seguridad» está vacía.", necesidades=["No declara necesidades", "Definir normas de seguridad (robots, CNC, PLC, VR)"]),
    "CON": dict(name="Consultorio Empresarial", color="#CC79A7", fuente="Informe Consultorio Empresarial - Dirección Ingeniería Industrial.pdf (10 pp.)", fecha="octubre de 2026",
                nat="No es un laboratorio de equipos: su laboratorio son emprendimientos y organizaciones reales; asesoría gratuita con estudiantes supervisados por docentes.",
                loc="Edificio 5-110", estado="Inhabilitado por el terremoto del 10 de agosto.", contacto="consultorioempresarial@utp.edu.co",
                recursos=["Mapa de procesos, formatos (actas, confidencialidad), guías del asesor y del docente", "Curso Fundamentos de Asesoría Empresarial (método del caso)", "Sitio web y boletín", "4 profesores transitorios, 3 catedráticos, 6 voluntarios, 1 monitora"],
                actividades=["Talleres de Canvas, formalización y gestión financiera inicial", "Asesorías y planeación estratégica para Mipymes", "Conexión Empresarial: proyectos finales de asignaturas con empresas reales", "Capacitación abierta y boletín"],
                impacto=[("10 → 7", "empresarios vinculados → certificados (2025)"), ("68", "participantes promedio por capacitación 2026-I"), ("5", "empresas en Conexión Empresarial"), ("25", "estudiantes en el curso 2026-II")],
                competencias=["Diagnóstico organizacional", "Escucha y comunicación con el cliente", "Pensamiento sistémico", "Gestión de procesos de asesoría", "Trabajo en equipo interdisciplinario", "Ética profesional y responsabilidad social"],
                requisitos="5.º semestre o superior, confidencialidad firmada, supervisión docente y actas de inicio, seguimiento y cierre.", necesidades=["Horas docentes y financiación tras el proyecto 28846", "Espacio físico para reuniones", "Insumos, transporte, televisor y mobiliario"]),
}
for lid, L in LABS.items():
    L["id"] = lid
    L["cob"] = COB[lid]
    pairs, ext = CLAIMS[lid]
    L["claims"] = ids_of(pairs)
    L["claimsExt"] = ext
parce = [("Gafas de realidad mixta Samsung Galaxy XR", "Capacitación inmersiva en picking y RA en almacén", 11495400),
         ("DevKit Basic de control gestual Kinemic", "Interacción por gestos con sistemas de almacén", 4165000),
         ("Quiosco de autoservicio Zebra KC50", "Autoservicio, caja y visualización", 11084850),
         ("Terminal móvil Zebra TC27", "Captura 1D/2D en recepción, inventario y despacho", 5105100),
         ("Lector RFID Zebra RFD40", "Lectura masiva de etiquetas RFID", 10282552)]
assert sum(p[2] for p in parce) == 42132902
risks = [("Sismo del 10-ago-2026", "Consultorio (5-110) inhabilitado; Financiero sin espacio; Logística (5-111) y Manufactura Flexible (5-109) no informan su estado.", "alto"),
         ("Obsolescencia tecnológica", "Logística: 7 PC y software de 2010–2015; solo 4 estudiantes simultáneos.", "alto"),
         ("Compra detenida", "PARCE 2026 aprobado el 16-mar-2026 (Acta 09) y sin entrega en octubre.", "medio"),
         ("Dependencia de voluntarios", "Consultorio extracurricular; fin del proyecto 28846 el 3-feb-2026.", "medio"),
         ("Baja integración curricular", "Solo 12 de 39 microcurrículos nombran un laboratorio; 11 tienen vacía la sección 8.", "alto"),
         ("Seguridad sin normas", "Manufactura Flexible maneja robots, CNC y PLC y su informe no trae normas de seguridad.", "alto")]

# ----------------------------- indicadores globales
now_declared = [s["id"] for s in subjects if s["asg"]["antes"] and not s["generic"]]
meta = dict(n=len(subjects), cred=sum(s["cred"] or 0 for s in subjects), had=sum(s["had"] for s in subjects), hti=sum(s["hti"] for s in subjects),
            nowDeclared=len(now_declared), generic=[s["id"] for s in subjects if s["generic"]],
            horasLab=sum(s["asg"]["horas"] for s in subjects))
DATA = dict(meta=meta, subjects=subjects, labs=LABS, labIds=LABIDS, findings=findings, bib=bib, tools=tools, cobItems=COB_ITEMS, parce=parce, risks=risks)

blob = json.dumps(DATA, ensure_ascii=False).replace("</", "<\\/")
tpl = open(TEMPLATE, encoding="utf-8").read()
assert "/*__DATA__*/" in tpl
html = tpl.replace("/*__DATA__*/", blob)
os.makedirs(os.path.dirname(OUT_HTML), exist_ok=True)
open(OUT_HTML, "w", encoding="utf-8", newline="\n").write(html)
print("OK", OUT_HTML, round(len(html) / 1024), "KB", "| hallazgos:", {f["k"]: len(f["ids"]) for f in findings})
print("seq:", [(byid[a]["code"], byid[b]["code"]) for a, b in seq], "mismo:", [(byid[a]["code"], byid[b]["code"]) for a, b in same])
