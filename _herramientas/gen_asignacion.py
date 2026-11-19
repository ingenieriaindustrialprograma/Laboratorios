"""Genera Analisis/asignacion: asignacion de laboratorio a cada asignatura + componente evaluativo.

Uso: python -I gen_asignacion.py <micro.json> <carpeta salida>
Para cambiar una asignacion basta editar la tabla ASIG y volver a ejecutar.
"""
import sys, os, re, json, collections, unicodedata

JSON_PATH, OUT = sys.argv[1], sys.argv[2]
recs = json.load(open(JSON_PATH, encoding="utf-8"))
os.makedirs(OUT, exist_ok=True)

LAB = {"FIN": "Laboratorio Financiero", "GEIO": "Laboratorio GEIO", "LOG": "Laboratorio de Logística",
       "MF": "Laboratorio de Manufactura Flexible", "CON": "Consultorio Empresarial"}
LABFILE = {"FIN": "02_laboratorio_financiero.md", "GEIO": "03_laboratorio_geio.md", "LOG": "04_laboratorio_logistica.md",
           "MF": "05_laboratorio_manufactura_flexible.md", "CON": "06_consultorio_empresarial.md"}
LABRULES = {
    "FIN": "Abierto a cualquier programa; sin requisitos de ingreso declarados; actividades certificables ante la Vicerrectoría de Innovación, Investigación y Extensión; la plataforma Bolsa Millonaria (concurso bvc–trii) se inscribe por semestre.",
    "GEIO": "Las lúdicas se solicitan por correo o WhatsApp institucional; sin requisitos de ingreso declarados; el informe no publica inventario ni capacidad.",
    "LOG": "Inducción al inicio de cada práctica y capacitación específica previa para gafas de realidad virtual; subgrupos de máximo 16 estudiantes; se espera ofimática básica; no instalar software; normas de seguridad del informe.",
    "MF": "El informe **no incluye normas de seguridad ni requisitos**: antes de asignar prácticas con robots, CNC o PLC deben definirse normas, inducción y acompañamiento.",
    "CON": "Asesoría directa desde **5.º semestre**; compromiso de confidencialidad; supervisión docente permanente; actas de inicio, seguimiento y cierre; no ofrecer servicios a título personal ni recibir pagos. Para semestres < 5 se propone **modalidad formativa** (talleres y observación, sin asesoría autónoma).",
}

# (codigo, palabra en nombre, principal, complementarios, ajuste, modalidad, por_que, practica, producto, peso, convierte, antes)
ASIG = [
 ("II123", "", "GEIO", ["MF", "CON"], "Medio", "", "Primer contacto con la profesión: las lúdicas de GEIO muestran fábricas, almacenes y cadenas de suministro (las «áreas de la empresa» del curso) y el microcurrículo ya recurre a «la lúdica que ofrecen los laboratorios de FACIEM».", "Circuito de inmersión: una lúdica GEIO (producción en serie o Beer Game) y una visita guiada al Lab. de Manufactura Flexible para prototipar el producto innovador (CAD e impresión 3D).", "Informe breve de la lúdica y prototipo del producto innovador presentado.", 15, "Desarrollo del prototipo del producto innovador.", ["GEIO"]),
 ("II3B3", "", "CON", ["GEIO"], "Medio", "Formativa", "El entregable «propuesta de creación de empresa» coincide con los talleres de modelo de negocio (Canvas) y formalización del Consultorio. Se imparte antes del 5.º semestre: participa en modalidad de taller, no de asesoría.", "Dos talleres del Consultorio (Canvas y formalización) aplicados al plan de empresa del grupo, con retroalimentación de los asesores.", "Canvas y propuesta de creación de empresa validados.", 15, "Propuesta de creación de empresa.", []),
 ("II321", "", "CON", ["GEIO"], "Medio", "Formativa", "Trabaja clima y cultura organizacional, grupos, liderazgo y bienestar; el Consultorio ofrece ciclos sobre inteligencia emocional y salud mental organizacional y declara la cultura organizacional como área de conocimiento.", "Participación en un ciclo de capacitación del Consultorio y aplicación del instrumento de clima a un caso/organización asignada, con acompañamiento docente.", "Informe de medición de clima y reflexión sobre la lúdica de grupo.", 15, "Medición de clima o cultura organizacional.", []),
 ("II4B3", "", "CON", ["GEIO"], "Alto", "Formativa", "Diseño de cargos, selección, evaluación de desempeño y tendencias de gestión humana: el Consultorio atiende talento humano en Mipymes. Por estar en 4.º semestre opera en modalidad formativa.", "Propuesta de gestión humana (cargos, selección, evaluación) para una Mipyme del Consultorio, en modalidad observación-diagnóstico.", "Propuesta moderna de gestión humana entregada y socializada.", 20, "Propuesta moderna de gestión humana para una empresa.", []),
 ("II6C3", "", "CON", ["FIN"], "Alto", "", "El entregable es una estructura salarial para una empresa; el Consultorio opera con organizaciones reales y el estudiante ya cursa 6.º semestre. FIN aporta el presupuesto y costos salariales.", "Diseñar la estructura salarial (escalas, curva, incentivos, costo) de una organización atendida, con actas de inicio y cierre.", "Estructura salarial y acta de cierre.", 25, "Diseño de nueva estructura de salarios para una empresa.", []),
 ("II7A3", "", "CON", [], "Alto", "", "Ya trabaja sobre empresa real (servucción, marketing mix) y el Consultorio reporta Conexión Empresarial con esta asignatura.", "Formalizar Conexión Empresarial: proyecto de marketing mix y servucción en una empresa acompañada, con actas.", "Informe y sustentación ante la empresa.", 25, "Trabajo especializado de servucción en empresa real y marketing mix (4P).", []),
 ("II8D3", "Mercados II", "CON", [], "Alto", "", "Investigación de mercados y medición de demanda aplicada a organizaciones reales; Conexión Empresarial ya incluye esta asignatura.", "Investigación de mercados para una organización del Consultorio: diseño de encuesta, medición de demanda y devolución de hallazgos.", "Informe de investigación y presentación de resultados a la empresa.", 25, "Investigación de mercados.", []),
 ("II243", "", "FIN", ["CON"], "Medio", "", "Estados financieros, impuestos y nómina; el laboratorio ofrece prácticas con datos reales y guías de análisis financiero, y el microcurrículo ya pide contabilizar una empresa real.", "Práctica de lectura de estados financieros reales (sector bancario/empresas inscritas en bvc) con las guías del laboratorio.", "Taller de lectura de estados y contabilización de transacciones de una empresa real.", 15, "Trabajo de aplicación de los conceptos en una empresa real.", []),
 ("II3C3", "", "FIN", [], "Medio", "", "Mercados, consumo, equilibrio y agregados macro: las pantallas e-bvc y Bolsa Millonaria permiten observar la formación de precios y la reacción a indicadores macroeconómicos.", "Seguimiento del mercado con e-bvc/Bolsa Millonaria durante el semestre y análisis de un agregado macroeconómico.", "Bitácora de seguimiento y ensayo de análisis de mercado.", 15, "(sección 8 vacía)", []),
 ("II4A3", "", "FIN", ["GEIO", "CON"], "Alto", "", "Ya declara Laboratorio Financiero («lúdica mesa de dinero») y GEIO; el costeo por órdenes, procesos y ABC se practica con casos reales.", "Formalizar: mesa de dinero + costeo por órdenes/ABC con lúdica GEIO; costos de una empresa acompañada por el Consultorio.", "Proyecto de aula con costeo completo y sustentación.", 20, "Laboratorio Financiero, proyecto de aula, Laboratorio GEIO.", ["FIN", "GEIO"]),
 ("II6A3", "", "FIN", ["CON"], "Alto", "", "El laboratorio lo lista (guía de análisis financiero, prácticas con datos reales) y es su objetivo central; Conexión Empresarial incluye «Planeación Financiera».", "Diagnóstico financiero con indicadores, usando guías del laboratorio y datos de una empresa, con devolución a una empresa del Consultorio.", "Diagnóstico financiero final y exposición.", 25, "Aplicar todo lo visto a estados financieros de una empresa real.", []),
 ("II8C3", "", "FIN", [], "Alto", "", "Valor del dinero en el tiempo y evaluación de alternativas; el laboratorio lista la asignatura y el mercado de capitales aporta tasas y datos para decisiones de inversión.", "Evaluación de alternativas de inversión con datos de mercado (tasas, renta fija) provistos por el laboratorio.", "Caso de decisión de inversión sustentado.", 20, "(sección 8 vacía)", []),
 ("II923", "Formulación", "CON", ["FIN"], "Alto", "", "Formular y evaluar proyectos de inversión; el Consultorio propone vincular formulación de proyectos y atiende modelos de negocio. FIN apoya la evaluación financiera.", "Formular el proyecto de un emprendimiento del Consultorio (mercado, técnico, financiero).", "Proyecto formulado y evaluado.", 25, "(sección 8 vacía)", []),
 ("II152", "", "FIN", ["LOG"], "Medio", "", "Excel, macros y bases de datos aplicadas: el laboratorio lista la asignatura (prácticas con datos reales) y su equipo incluye a la coordinadora del curso.", "Taller de Excel/Access con series de mercado e indicadores bancarios reales; ejercicio de base de datos con inventario del Lab. de Logística.", "Libro de Excel con macros y base de datos funcional.", 15, "(sección 8 vacía)", []),
 ("II212", "", "FIN", ["LOG"], "Alto", "", "R, tidyverse, limpieza y exploración de datos: encaja con las guías de descarga de indicadores y estados financieros del sector bancario y la búsqueda con IA; el laboratorio la lista.", "Pipeline en R: descarga, limpieza y análisis de indicadores del sector bancario.", "Script reproducible y reporte de análisis.", 20, "(sección 8 vacía)", []),
 ("II4D3", "", "FIN", ["GEIO"], "Medio", "", "Descriptiva, probabilidad y distribuciones: el laboratorio declara «toma de decisiones estadísticas con datos financieros» y GEIO aporta lúdicas de variabilidad (ya usadas en el curso).", "Análisis descriptivo y de probabilidad de retornos de acciones + lúdica GEIO de variabilidad.", "Informe de aplicación a un problema de Ingeniería Industrial.", 15, "Aplicación de estimación y pruebas de hipótesis a un problema de II.", []),
 ("II5A3", "", "GEIO", ["FIN"], "Medio", "", "Inferencia (intervalos, pruebas de hipótesis): las lúdicas de GEIO generan datos (producción en serie, colas) que se pueden contrastar; FIN aporta datos reales.", "Experimento con lúdica: muestrear, estimar y probar hipótesis (paramétricas y no paramétricas) y contrastar con datos de mercado.", "Informe estadístico del experimento.", 15, "(sección 8 vacía)", []),
 ("II6A2", "", "FIN", ["LOG"], "Medio", "", "Muestreo y regresión: series financieras y de indicadores (con el grupo DEA) y análisis de datos logísticos.", "Modelo de regresión múltiple sobre series de mercado y plan de muestreo de inventario.", "Modelo validado e informe.", 15, "(sección 8 vacía)", []),
 ("II713", "", "GEIO", ["LOG"], "Alto", "", "Cadenas de Markov y teoría de colas: GEIO trabaja modelos de colas y simulación; el autoservicio de Logística da colas reales.", "Lúdica de colas y Markov + medición de colas reales en el área de autoservicio del Lab. de Logística.", "Modelo de colas validado con datos propios.", 20, "(sección 8 vacía)", []),
 ("II7D3", "", "GEIO", ["FIN"], "Alto", "", "Ya usa una lúdica GEIO para introducir programación lineal; GEIO tiene solvers y metodologías de modelado.", "Formalizar: lúdica de modelado + proyecto de modelo de PL resuelto con solver.", "Modelo matemático construido y socializado.", 20, "(sección 8 vacía; lúdica GEIO declarada en el contenido)", ["GEIO"]),
 ("II8B3", "", "GEIO", ["LOG", "FIN"], "Alto", "", "Programación entera, heurísticas, redes y TSP: GEIO integra heurísticas y solvers (Gurobi/CPLEX/PuLP); Logística aporta casos de rutas y ubicación.", "Reto de optimización: diseñar una heurística y compararla con la solución exacta sobre un caso logístico.", "Informe comparativo heurística vs. exacto.", 20, "(sección 8 vacía)", []),
 ("II863", "", "GEIO", ["MF", "LOG"], "Alto", "", "Simulación de eventos discretos (ProModel/FlexSim) con 13 prácticas de laboratorio; GEIO integra lúdicas y simulación, MF usa FlexSim y LOG simula procesos logísticos.", "Formalizar las 13 prácticas como componente de laboratorio y validar un modelo contra una lúdica o una celda real.", "Modelo de simulación del caso real y validación.", 25, "Prácticas 1–13 de «Laboratorios de Simulación Discreta» y caso real (ya en el contenido; sección 8 vacía).", []),
 ("II8A3", "", "MF", ["GEIO"], "Alto", "", "Programación, secuenciación y balanceo de líneas de ensamble: el Lab. de Manufactura Flexible lo lista con esos temas y el microcurrículo ya declara MF y GEIO.", "Balanceo de línea y scheduling en la celda de ensamble + simulación en FlexSim; lúdica GEIO de programación.", "Informe de balanceo/programación con simulación.", 25, "Prácticas en el Laboratorio GEIO y en el de Manufactura Flexible.", ["GEIO", "MF"]),
 ("II742", "", "MF", ["LOG", "GEIO"], "Alto", "", "Estudio de tiempos y movimientos, ergonomía y diseño de puestos: MF lo lista (realidad virtual para puestos de trabajo) y el microcurrículo ya usa «tecnologías de realidad virtual (laboratorio)» y Ergonautas.", "Diseño y evaluación de un puesto en VR (REBA/RULA) y estudio de tiempos en la celda de ensamble; réplica del estudio en picking (LOG).", "Informe de observación y rediseño del puesto.", 25, "Diseño de puesto de trabajo y prácticas de laboratorio (movimientos, ensamble).", ["GEIO"]),
 ("II883", "", "LOG", ["MF", "GEIO"], "Medio", "", "Riesgos, diagnóstico de condiciones y desastres: el Lab. de Logística propone entrenamiento en seguridad de almacenes con realidad virtual; MF aporta VR y ergonomía de estaciones.", "Identificación de peligros en un almacén virtual (con capacitación previa) y diagnóstico de condiciones de trabajo de un puesto.", "Matriz de peligros y plan de control.", 20, "Prácticas en el laboratorio GEIO.", ["GEIO"]),
 ("II9B2", "", "MF", ["LOG", "CON"], "Alto", "", "Distribución de plantas, flujo de materiales y celdas: MF permite recorrer alternativas de layout en VR; LOG aporta la distribución de almacenes; el proyecto final es sobre empresa real.", "Layout evaluado en VR (SolidWorks → Unreal) y distribución de un almacén en LOG; proyecto final opcionalmente con una empresa del Consultorio.", "Proyecto de diseño de planta con evaluación en VR.", 25, "Proyecto final de diseño de plantas aplicado a una empresa real.", []),
 ("II9C3", "", "LOG", ["GEIO", "MF"], "Medio", "", "Planeación de demanda, MRP y clasificación y modelos de inventario: Logística lo lista (inventarios, trazabilidad, WMS); GEIO aporta lúdicas de planeación y MF la planeación MRP/Kanban.", "Control de inventarios con códigos de barras/RFID (conteo cíclico, ABC) + lúdica GEIO de efecto látigo + MRP/Kanban en la celda.", "Informe de control de inventario y plan de requerimientos.", 20, "Prácticas en el laboratorio GEIO.", ["GEIO"]),
 ("II0D3", "", "MF", ["GEIO"], "Alto", "", "Su contenido es manufactura flexible: FMS, tecnología de grupos, celdas y ensamble flexible, que es exactamente la celda del Lab. de Manufactura Flexible.", "Diseño y simulación de una celda/FMS, programación de un robot en RobotStudio y lúdica GEIO de celdas y TOC.", "Diseño de celda flexible simulado y validado.", 25, "Prácticas en el laboratorio GEIO.", ["GEIO"]),
 ("II0F3", "", "MF", ["LOG", "GEIO"], "Medio", "", "Control estadístico y mejoramiento: la visión artificial Cognex permite inspección automatizada; Logística aporta trazabilidad de lotes; GEIO lúdicas de calidad.", "Inspección automatizada con visión artificial + gráficos de control; trazabilidad de un lote en LOG.", "Informe de capacidad de proceso y trazabilidad.", 20, "Informes de lecturas especializadas y análisis de casos.", []),
 ("IIE07", "", "MF", [], "Alto", "", "Automatización y robótica: ABB IRB 120, Mitsubishi RV-2AJ, PLC Siemens y Fischertechnik; ya declara el laboratorio.", "Formalizar el proyecto y las prácticas con robots, PLC y Fischertechnik (celda robótica).", "Proyecto de celda automatizada funcionando.", 30, "Proyecto y prácticas con robots industriales y Fischertechnik.", ["MF"]),
 ("IIP02", "", "GEIO", ["CON", "MF"], "Medio", "", "El portafolio de GEIO incluye capacitación en Six Sigma y lúdicas de variabilidad; el proyecto DMAIC puede aplicarse a una organización del Consultorio.", "Proyecto DMAIC sobre un caso de lúdica (medición de variabilidad) y, si es posible, sobre una organización acompañada.", "Proyecto DMAIC documentado.", 25, "Proyecto de aplicación de DMAIC a un caso propuesto.", []),
 ("IIP03", "", "GEIO", ["MF"], "Alto", "", "Lean con lúdicas (Kanban, flujo, 5S): ya declara «lúdicas y prácticas en el Laboratorio GEIO»; MF permite balanceo y Kanban en celda.", "Lúdicas Lean + balanceo y Kanban en la celda de ensamble.", "Informe de mejora Lean con indicadores.", 25, "Desarrollo de lúdicas y prácticas en el Laboratorio GEIO.", ["GEIO"]),
 ("IIA03", "", "CON", ["LOG"], "Medio", "", "Estrategias de entrada a mercados externos y propuesta de mercadeo internacional para una empresa: es trabajo con organizaciones reales; Logística aporta Incoterms, fletes y cubicaje.", "Propuesta de mercadeo internacional para una Mipyme del Consultorio + cálculo de fletes/cubicaje en LOG.", "Propuesta de mercadeo internacional sustentada.", 25, "Propuesta de mercadeo internacional para la empresa.", []),
 ("IIO08", "", "GEIO", ["CON"], "Medio", "", "Sistemas complejos, arquetipos sistémicos y resiliencia: GEIO trabaja dinámicas de sistemas; ya declara «taller con grupo GEIO» y visita técnica.", "Taller GEIO de sistemas complejos y visita técnica/diagnóstico socio-ambiental de una Mipyme con el Consultorio.", "Estudio de caso final con informe de visita.", 20, "Taller con grupo GEIO, estudio de caso y visita técnica.", ["GEIO"]),
 ("II8D3", "Gestión", "CON", [], "Alto", "", "Planeación estratégica, direccionamiento, diseño organizacional y desarrollo organizacional: son servicios centrales del Consultorio.", "Propuesta de estructura administrativa y direccionamiento estratégico de una organización del Consultorio.", "Propuesta de estructura y plan estratégico.", 25, "Propuesta de estructura administrativa de la empresa.", []),
 ("II923", "Optimiz", "FIN", ["GEIO"], "Alto", "", "Optimización de portafolios y mercados financieros: ya cita fuentes del laboratorio (Refinitiv, PRECIA, bvc); GEIO aporta solvers.", "Optimización de portafolio con fuentes del laboratorio, validación en Bolsa Millonaria y solvers GEIO.", "Caso de optimización con datos reales.", 25, "Caso real o académico con bases de datos y fuentes del Laboratorio Financiero.", ["FIN"]),
 ("IIP01", "Log", "LOG", ["GEIO"], "Alto", "", "Cadena de suministro, almacenamiento, transporte: es el núcleo del Lab. de Logística y ya declara LOG y GEIO.", "Formalizar prácticas de inventarios, picking, RFID/WMS, lúdica de cadena (Beer Game) y proyecto final.", "Proyecto final logístico con prácticas documentadas.", 30, "Laboratorio GEIO, Laboratorio de Logística y proyecto final.", ["GEIO", "LOG"]),
 ("IIP01", "Product", "MF", ["GEIO"], "Alto", "", "Diseño de producto y prototipado: SolidWorks, impresión 3D y CNC del Lab. de Manufactura Flexible; GEIO aporta Design Thinking.", "Prototipo físico: modelado en SolidWorks e impresión 3D/CNC; sesión de Design Thinking.", "Prototipo y dossier de diseño.", 30, "Elaboración de prototipos de producto con diversos materiales.", []),
 ("UV093", "", "LOG", ["MF", "FIN"], "Medio", "", "Tecnologías emergentes 4.0 e innovación: Logística propone la asignatura de gestión tecnológica para RFID, NFC y VR/AR; MF aporta Industria 4.0 y FIN la búsqueda con IA en bases especializadas (vigilancia tecnológica).", "Vigilancia tecnológica de una tecnología 4.0 con demostración en LOG y búsqueda en bases especializadas.", "Informe de vigilancia tecnológica y demostración.", 20, "Uso de herramientas digitales y plataformas tecnológicas.", []),
]


# ---------------------------------------------------------------- utilidades
def norm(s):
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def esc(s):
    return (s or "").replace("|", "\\|").replace("\n", " ").strip()


ORD = [("primer", 1), ("segundo", 2), ("tercer", 3), ("cuarto", 4), ("quinto", 5), ("sexto", 6), ("septimo", 7),
       ("octavo", 8), ("noveno", 9), ("decimo", 10), ("once", 11), ("undecimo", 11), ("doceavo", 12), ("doce", 12)]


def sem_ord(t):
    t = norm(t)
    best = None
    for w, n in ORD:
        m = re.search(r"\b" + w, t)
        if m and (best is None or m.start() < best[0]):
            best = (m.start(), n)
    return best[1] if best else None


def num(s):
    m = re.search(r"(\d+)", s or "")
    return int(m.group(1)) if m else None


def semm(r):
    """Semestre en la malla de 10 semestres: primer digito del codigo (0 = 10). Electivas: None (se ofrecen del 7.o al 10.o)."""
    if r["tipo"] == "Electiva":
        return None
    m = re.match(r"II(\d)", r["codigo"])
    return (10 if m.group(1) == "0" else int(m.group(1))) if m else None


for r in recs:
    h = r["header"]
    r["codigo"] = h.get("Código de asignatura", "").strip()
    r["nombre"] = h.get("Nombre completo de la asignatura", r["titulo_md"]).strip()
    r["sem_txt"] = h.get("Semestre y año en que se imparte", "")
    r["sem_n"] = sem_ord(r["sem_txt"])
    r["had"] = sum(c["had"] or 0 for c in r["contenido"])
    r["hti"] = sum(c["hti"] or 0 for c in r["contenido"])
    r["eval_sum"] = sum((e["porcentaje"] or 0) for e in r["evaluacion"])


def find(code, kw):
    c = [r for r in recs if r["codigo"] == code and norm(kw) in norm(r["nombre"])]
    assert len(c) == 1, (code, kw, [x["nombre"] for x in c])
    return c[0]


items = []
for (code, kw, prim, comps, fit, mod, why, pract, prod, peso, conv, antes) in ASIG:
    r = find(code, kw)
    r["semm"] = semm(r)
    estado ="Nuevo" if not antes else ("Coincide" if prim in antes else "Cambia")
    horas = 2 * round(peso / 100 * r["had"] / 2)
    items.append(dict(r=r, prim=prim, comps=comps, fit=fit, mod=mod, why=why, pract=pract, prod=prod, peso=peso,
                      conv=conv, antes=antes, estado=estado, horas=horas))
assert len(items) == 39 and len({id(i["r"]) for i in items}) == 39, "faltan o sobran asignaturas"
items.sort(key=lambda i: (i["r"]["semm"] or 11, i["r"]["codigo"], i["r"]["nombre"]))


def label(i):
    r = i["r"]
    return f"{r['codigo']} · {r['nombre']}"


def sem(i):
    return f"{i['r']['semm']}.º" if i["r"]["semm"] else "Elec."


def w(name, lines):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines).rstrip() + "\n")
    return len(lines)


def labs_txt(lst):
    return ", ".join(LAB[x].replace("Laboratorio ", "Lab. ").replace("Laboratorio de ", "Lab. ") for x in lst) or "—"


def short(x):
    return {"FIN": "FIN", "GEIO": "GEIO", "LOG": "LOG", "MF": "MF", "CON": "CON"}[x]


sizes = {}
cnt_prim = collections.Counter(i["prim"] for i in items)
cnt_comp = collections.Counter(c for i in items for c in i["comps"])
cnt_est = collections.Counter(i["estado"] for i in items)
cnt_fit = collections.Counter(i["fit"] for i in items)

# ---------------------------------------------------------------- 01 matriz
L = ["# Matriz de asignación: asignatura → laboratorio", ""]
L.append("**Principal** = laboratorio al que se vincula el componente evaluativo y aprobatorio. **Complementarios** = laboratorios que aportan sesiones puntuales sin peso adicional. **Ajuste** = pertinencia entre los resultados de aprendizaje y contenidos de la asignatura y el propósito y recursos del laboratorio. **Estado** compara con lo que ya declaraba el microcurrículo (*Coincide* / *Cambia* / *Nuevo*).")
L.append("")
L.append("| Sem. | Código | Asignatura | Antes (declarado) | **Principal** | Complementarios | Ajuste | Estado | Peso | Horas |")
L.append("|--:|---|---|---|---|---|:-:|:-:|--:|--:|")
for i in items:
    mod = " (formativa)" if i["mod"] else ""
    L.append(f"| {sem(i)} | {i['r']['codigo']} | {esc(i['r']['nombre'])} | {labs_txt(i['antes'])} | **{short(i['prim'])}**{mod} | {', '.join(short(c) for c in i['comps']) or '—'} | {i['fit']} | {i['estado']} | {i['peso']}% | {i['horas']} |")
L.append("")
L.append("_FIN Financiero · GEIO · LOG Logística · MF Manufactura Flexible · CON Consultorio Empresarial. «Horas» = sesiones de laboratorio (HAD) propuestas dentro de las horas presenciales existentes._")
L.append("")
L.append("## Por qué cada asignatura quedó donde quedó")
L.append("")
L.append("| Código | Asignatura | Justificación |")
L.append("|---|---|---|")
for i in items:
    L.append(f"| {i['r']['codigo']} | {esc(i['r']['nombre'])} | {esc(i['why'])} |")
sizes["01_matriz_asignacion_39.md"] = w("01_matriz_asignacion_39.md", L)

# ---------------------------------------------------------------- 02..06 por laboratorio
for lab in LAB:
    mine = [i for i in items if i["prim"] == lab]
    comp = [i for i in items if lab in i["comps"]]
    L = [f"# {LAB[lab]} — asignaturas vinculadas", ""]
    L.append(f"**{len(mine)} asignaturas como laboratorio principal** (con componente evaluativo y aprobatorio) y **{len(comp)} como complementario** (sesiones puntuales, sin peso adicional).")
    L.append("")
    L.append(f"**Condiciones de uso que el laboratorio declara en su informe:** {LABRULES[lab]}")
    L.append("")
    L.append("| Sem. | Asignatura | Ajuste | Estado | Peso | Horas |")
    L.append("|--:|---|:-:|:-:|--:|--:|")
    for i in mine:
        L.append(f"| {sem(i)} | {esc(label(i))} | {i['fit']} | {i['estado']} | {i['peso']}% | {i['horas']} |")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## A. Asignaturas con componente evaluativo en este laboratorio")
    L.append("")
    for i in mine:
        r = i["r"]
        L.append(f"### {label(i)} ({sem(i)} semestre)")
        L.append("")
        L.append(f"- **Ajuste:** {i['fit']} · **Estado:** {i['estado']}" + (f" (antes: {labs_txt(i['antes'])})" if i["antes"] else " (sin antecedente en el microcurrículo)") + (f" · **Modalidad:** {i['mod']}, sin asesoría directa (< 5.º semestre)" if i["mod"] else ""))
        L.append(f"- **Por qué aquí:** {i['why']}")
        L.append(f"- **Práctica propuesta:** {i['pract']}")
        L.append(f"- **Evidencia evaluable:** {i['prod']}")
        L.append(f"- **Peso y horas:** {i['peso']}% de la nota final · {i['horas']} h de las {r['had']} HAD del curso")
        L.append(f"- **Convierte (no suma carga):** {i['conv']}")
        L.append(f"- **Complementarios:** {labs_txt(i['comps'])}")
        L.append(f"- **Resultado de aprendizaje del programa:** {', '.join('RAP' + c for c in r['rap_codigos']) or '—'} · **Formación integral:** {', '.join(r['formacion_integral_comp']) or '—'}")
        L.append("")
    L.append("## B. Asignaturas que usan este laboratorio como complemento")
    L.append("")
    if comp:
        L.append("| Sem. | Asignatura | Laboratorio principal | Aporte puntual de este laboratorio |")
        L.append("|--:|---|---|---|")
        for i in comp:
            L.append(f"| {sem(i)} | {esc(label(i))} | {short(i['prim'])} | Ver práctica propuesta en la ficha de la asignatura (`01_matriz_asignacion_39.md`) |")
    else:
        L.append("Ninguna.")
    sizes[LABFILE[lab]] = w(LABFILE[lab], L)

# ---------------------------------------------------------------- 07 ruta por semestre
L = ["# Ruta del estudiante por semestre", ""]
L.append("Qué laboratorio toca al estudiante en cada semestre de la **malla de 10 semestres** (principal en **negrita**; entre paréntesis, complementarios).")
L.append("")
L.append("> El semestre se toma del **primer dígito del código** del curso (0 = 10.º), porque los microcurrículos declaran semestres hasta el 12.º que no existen en un programa de 10. Es un dato **inferido**. Las **electivas profesionales** se ofrecen del 7.º al 10.º y se agrupan aparte.")
L.append("")
L.append("| Semestre | Asignatura → laboratorio |")
L.append("|--:|---|")
by = collections.defaultdict(list)
for i in items:
    by[i["r"]["semm"]].append(i)
for s in sorted(by, key=lambda x: (x is None, x)):
    cells = "<br>".join(f"{esc(i['r']['codigo'] + ' ' + i['r']['nombre'])} → **{short(i['prim'])}**" + (f" ({', '.join(short(c) for c in i['comps'])})" if i["comps"] else "") for i in by[s])
    L.append(f"| {s if s else 'Electivas (7.º–10.º)'} | {cells} |")
L.append("")
L.append("## Carga por laboratorio y semestre (n.º de asignaturas principales)")
L.append("")
sems = sorted(by, key=lambda x: (x is None, x))
L.append("| Lab. | " + " | ".join(str(s) if s else "Elec." for s in sems) + " | Total |")
L.append("|---|" + "|".join("--:" for _ in sems) + "|--:|")
for lab in LAB:
    row = [sum(1 for i in by[s] if i["prim"] == lab) for s in sems]
    L.append(f"| {short(lab)} | " + " | ".join(str(x) if x else "" for x in row) + f" | {sum(row)} |")
L.append("")
L.append("> Es un insumo para la etapa de asignación de espacios y horarios: muestra en qué semestres se concentra la demanda de cada laboratorio. **No** se evaluó capacidad física ni número de estudiantes.")
sizes["07_ruta_por_semestre.md"] = w("07_ruta_por_semestre.md", L)

# ---------------------------------------------------------------- 09 impacto en evaluacion
L = ["# Impacto en la evaluación de cada microcurrículo", ""]
L.append("Regla: el componente de laboratorio **no se suma**; se toma de la evaluación de proceso ya existente (talleres, informes, proyecto) para no aumentar la carga.")
L.append("")
L.append("| Código | Asignatura | Evaluación actual (filas) | Suma actual | Componente lab | Resto | Acción |")
L.append("|---|---|---|--:|--:|--:|---|")
for i in items:
    r = i["r"]
    ps = " + ".join(str(e["porcentaje"]) for e in r["evaluacion"])
    if r["eval_sum"] == 100:
        acc = f"Reasignar {i['peso']} pts desde la evaluación de proceso"
    else:
        acc = f"⚠ Normalizar primero: suma {r['eval_sum']}%; luego asignar {i['peso']}% al componente"
    L.append(f"| {r['codigo']} | {esc(r['nombre'])} | {ps} | {r['eval_sum']}% | {i['peso']}% | {100 - i['peso']}% | {acc} |")
bad = [i for i in items if i["r"]["eval_sum"] != 100]
L.append("")
L.append(f"**{len(bad)} microcurrículos requieren normalizar su tabla de evaluación antes de insertar el componente:** " + ", ".join(f"{i['r']['codigo']} ({i['r']['eval_sum']}%)" for i in bad) + ".")
sizes["09_impacto_en_evaluacion.md"] = w("09_impacto_en_evaluacion.md", L)

# ---------------------------------------------------------------- 08 plantilla
T = """# Componente de laboratorio: definición, regla aprobatoria, rúbrica y textos modelo

## 1. Definición
El **componente de laboratorio** es el conjunto de sesiones prácticas y el entregable evaluado que cada asignatura realiza en su laboratorio principal. Se incorpora al microcurrículo en las secciones **8** (trabajos en laboratorio y proyectos), **9** (métodos de aprendizaje) y **10** (métodos de evaluación) y tiene **peso propio** en la nota final.

## 2. Principios
1. **No suma carga: convierte.** El componente reemplaza trabajos, talleres o proyectos que el microcurrículo ya exige (columna «Convierte» de cada ficha).
2. **Un laboratorio principal por asignatura**, con peso y condición aprobatoria. Los complementarios son sesiones puntuales sin peso adicional.
3. **Horas dentro de la HAD existente.** Se propone entre 6 y 20 horas de las horas presenciales, en sesiones de 4 horas; la preparación se cuenta en HTI.
4. **Peso entre 15 % y 30 %:** 15 % si el ajuste es indirecto o la modalidad es formativa; 20 % por defecto; 25–30 % cuando el entregable del laboratorio sustituye el proyecto final de la asignatura.

## 3. Regla aprobatoria (para decisión)
| Opción | Regla | Efecto |
|---|---|---|
| **A (recomendada)** | Para aprobar la asignatura se debe **aprobar el componente de laboratorio** (nota mínima = la aprobatoria institucional) además de la nota final | Garantiza que el laboratorio sea requisito real; exige definir recuperación del componente |
| B | El componente solo pondera en la nota final | Más simple; la asistencia y la práctica no quedan garantizadas |

> Verificar la opción elegida contra el reglamento estudiantil y la instancia curricular competente antes de modificar los microcurrículos.

## 4. Rúbrica estándar (se adapta por laboratorio)
| Criterio | Peso | Qué se observa |
|---|--:|---|
| Preparación, inducción y normas | 15 % | Asistencia a la inducción, cumplimiento de normas de seguridad o confidencialidad, preparación previa |
| Ejecución y registro de la práctica | 30 % | Correcta ejecución, bitácora, datos obtenidos |
| Análisis y resultados | 35 % | Interpretación, uso de modelos/herramientas del curso, conclusiones sustentadas |
| Informe, sustentación y trabajo en equipo | 20 % | Calidad del informe, exposición, trabajo colaborativo |

Niveles: insuficiente · aceptable · bueno · sobresaliente. La competencia institucional de la asignatura (liderazgo, trabajo en equipo, pensamiento crítico, comunicación, sostenibilidad, aprender a aprender) se evalúa dentro de «informe, sustentación y trabajo en equipo».

## 5. Textos modelo para el microcurrículo
**Sección 8 — Trabajos en laboratorio y proyectos**
> Componente de laboratorio en [laboratorio principal]: [N] sesiones de 4 horas ([H] HAD). Práctica: [descripción]. Evidencia evaluable: [producto]. Laboratorios complementarios: [lista, si aplica]. Este componente es de carácter aprobatorio.

**Sección 9 — Métodos de aprendizaje**
> Práctica de laboratorio ejecutada por los estudiantes en [laboratorio principal], con inducción previa y acompañamiento del docente/coordinador del laboratorio.

**Sección 10 — Métodos de evaluación (fila nueva)**
> Evaluación de proceso y resultado: componente de laboratorio ([producto]) según rúbrica institucional. **[X] %.** Aprobatorio. *([competencia institucional])*

## 6. Lista de verificación al actualizar cada microcurrículo
- [ ] Sección 8 describe el laboratorio principal y el producto.
- [ ] Sección 9 incluye la práctica ejecutada por el estudiante.
- [ ] Sección 10: fila del componente con su porcentaje y la nota de carácter aprobatorio.
- [ ] La tabla de evaluación suma 100 % (ver `09_impacto_en_evaluacion.md`).
- [ ] Las horas de laboratorio quedan dentro de la HAD del contenido.
- [ ] Se citan las condiciones del laboratorio (inducción, seguridad, confidencialidad, semestre mínimo).
- [ ] Se conserva evidencia para acreditación: listas de asistencia, rúbricas y productos.

## 7. Condiciones por laboratorio
""" + "\n".join(f"- **{LAB[k]}:** {v}" for k, v in LABRULES.items()) + "\n"
sizes["08_componente_evaluativo_plantilla.md"] = w("08_componente_evaluativo_plantilla.md", T.split("\n"))

# ---------------------------------------------------------------- 00 indice
L = ["# Asignación de laboratorio por asignatura — método y resultados", ""]
L.append("**Objetivo.** Declarar, para cada una de las **39 asignaturas**, el laboratorio que mejor conviene a su formación según su microcurrículo (contenidos, resultados de aprendizaje, entregables) y el propósito y recursos del laboratorio, de modo que **ninguna asignatura quede sin laboratorio** y el componente práctico sea **evaluativo y aprobatorio**. Es el insumo para la etapa posterior de asignaciones, ubicaciones y espacios.")
L.append("")
L.append("## 1. Método")
L.append("")
L.append("Cada asignatura se evaluó con cuatro criterios:")
L.append("")
L.append("1. **Pertinencia de contenido:** relación entre los resultados de aprendizaje y las unidades del curso con el propósito y los recursos del laboratorio.")
L.append("2. **Evidencia previa:** si el microcurrículo ya nombra al laboratorio o el laboratorio ya lista la asignatura.")
L.append("3. **Entregable convertible:** si el trabajo o proyecto que el microcurrículo ya exige puede realizarse en el laboratorio sin añadir carga.")
L.append("4. **Condiciones de uso del laboratorio:** por ejemplo, el Consultorio solo asesora desde 5.º semestre (antes, modalidad formativa); Manufactura Flexible no tiene normas de seguridad escritas.")
L.append("")
L.append("**Ajuste Alto:** el contenido apunta directamente a los recursos del laboratorio y hay evidencia previa o un entregable convertible. **Ajuste Medio:** el vínculo es indirecto, se apoya en datos o lúdicas del laboratorio o está limitado por una condición de uso.")
L.append("")
L.append("## 2. Resultado en una mirada")
L.append("")
L.append(f"- **39 de 39 asignaturas asignadas** (0 vacías). Ajuste **Alto: {cnt_fit['Alto']}** · **Medio: {cnt_fit['Medio']}**.")
L.append("- **Laboratorio principal:** " + " · ".join(f"{short(k)} {cnt_prim[k]}" for k in LAB) + ".")
L.append("- **Complementario en:** " + " · ".join(f"{short(k)} {cnt_comp[k]}" for k in LAB) + " asignaturas.")
L.append(f"- **Frente a lo declarado hoy en los microcurrículos:** Coincide {cnt_est['Coincide']} · Cambia {cnt_est['Cambia']} · Nuevo {cnt_est['Nuevo']}.")
cam = [i for i in items if i["estado"] == "Cambia"]
L.append("- **Reasignaciones (cambia el laboratorio principal):** " + "; ".join(f"{i['r']['codigo']} {i['r']['nombre']} ({labs_txt(i['antes'])} → {LAB[i['prim']]})" for i in cam) + ".")
L.append(f"- **Peso medio del componente:** {sum(i['peso'] for i in items) / len(items):.0f}% (rango {min(i['peso'] for i in items)}–{max(i['peso'] for i in items)}%) · **horas de laboratorio propuestas:** {sum(i['horas'] for i in items)} h en total.")
L.append(f"- **{len(bad)} microcurrículos** deben normalizar su tabla de evaluación (no suma 100 %) antes de insertar el componente.")
L.append("")
L.append("## 3. Archivos")
L.append("")
L.append("| Archivo | Contenido |")
L.append("|---|---|")
for n, d in [("01_matriz_asignacion_39.md", "Tabla maestra de las 39 asignaturas y justificación de cada asignación"),
             ("02_laboratorio_financiero.md · 03_laboratorio_geio.md · 04_laboratorio_logistica.md · 05_laboratorio_manufactura_flexible.md · 06_consultorio_empresarial.md", "Por laboratorio: asignaturas vinculadas, práctica propuesta, evidencia evaluable, peso, horas y qué trabajo existente se convierte"),
             ("07_ruta_por_semestre.md", "Qué laboratorio toca al estudiante en cada semestre y carga por semestre"),
             ("08_componente_evaluativo_plantilla.md", "Definición, regla aprobatoria (opciones), rúbrica estándar y textos modelo para secciones 8, 9 y 10"),
             ("09_impacto_en_evaluacion.md", "Cómo cambia la evaluación de cada microcurrículo y cuáles hay que normalizar")]:
    L.append(f"| `{n}` | {d} |")
L.append("")
L.append("## 4. Supuestos y límites")
L.append("")
L.append("- Es una **propuesta técnica** basada en los documentos; las asignaciones y prácticas deben validarse con los **docentes coordinadores** de cada asignatura y con los responsables de cada laboratorio.")
L.append("- **No se consideró** ubicación, espacio, horarios ni número de estudiantes por grupo; esa es la etapa siguiente.")
L.append("- **Semestres:** el programa tiene **10 semestres** y las **electivas profesionales** se ofrecen del 7.º al 10.º (dato confirmado por la Dirección). Los microcurrículos declaran semestres hasta el 12.º, así que aquí el semestre de cada obligatoria se infiere del primer dígito de su código (0 = 10.º). Esto no cambia ninguna asignación; solo la ruta por semestre.")
L.append("- Las asignaciones con ajuste **Medio** son las más discutibles y se marcan como tales. Los informes de **GEIO y Manufactura Flexible** no detallan inventario, capacidad ni normas, así que la viabilidad práctica de lo propuesto allí debe confirmarse.")
L.append("- La regla aprobatoria (opción A) y los pesos son **propuestas de política** que requieren aval de la instancia curricular y verificación frente al reglamento estudiantil.")
L.append("- Para cambiar una asignación, edite la tabla `ASIG` de `Analisis/_herramientas/gen_asignacion.py` y vuelva a ejecutarlo: regenera todos los archivos de esta carpeta.")
sizes["00_INDICE_Y_METODO.md"] = w("00_INDICE_Y_METODO.md", L)

# copia de herramientas para poder regenerar
import shutil
tools = os.path.join(os.path.dirname(OUT.rstrip("\\/")), "_herramientas")
os.makedirs(tools, exist_ok=True)
shutil.copy(__file__, os.path.join(tools, "gen_asignacion.py"))
shutil.copy(JSON_PATH, os.path.join(tools, "micro.json"))
for k in sorted(sizes):
    print(k, sizes[k], "lineas")
print("prim", dict(cnt_prim), "comp", dict(cnt_comp), "estado", dict(cnt_est), "ajuste", dict(cnt_fit))
