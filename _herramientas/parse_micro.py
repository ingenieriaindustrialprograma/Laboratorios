"""Parser de microcurriculos (Markdown de plantilla UTP) -> micro.json.

Uso: python -I parse_micro.py <carpeta Microcurriculos actualizados> <salida micro.json> [--stats]
"""
import sys, os, re, json, collections

AREA_ORDER = [
    "Área Administrativa",
    "Área Financiera",
    "Área de Investigación de Operaciones y Estadística",
    "Área de Producción",
    "Electivas de formación profesional",
]


def clean(s):
    s = s.replace(" ", " ")
    s = re.sub(r"<br\s*/?>", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def unbold(s):
    return clean(re.sub(r"\*\*", "", s))


KNOWN_LABELS = re.compile(
    r"^(estrategias\s+tic|actividad\s+(dentro\s+del\s+)?aula(\s+de\s+clase)?|actividad\s+fuera\s+del\s+aula(\s+de\s+clase)?|"
    r"estrategias\s+did[aá]cticas\s+del\s+profesor|bibliogr[aá]ficos?|bibliograf[ií]as?|textos\s+complementarios|"
    r"lecturas\s+obligatorias|recursos\s+adicionales|webgraf[ií]a|software|libros|did[aá]cticos)\s*[.:]?$",
    re.I,
)


def split_labeled(lines):
    """Divide lineas en bloques por lineas que son solo negrita (**Etiqueta**) o etiquetas conocidas sin negrita."""
    out = collections.OrderedDict()
    cur = ""
    out[cur] = []
    for l in lines:
        t = l.strip()
        if not t or t.startswith("#"):
            continue
        t_nb = re.sub(r"^[-*•]\s+", "", t)
        m = re.match(r"^\*\*([^*]+?)\*\*\s*:?\s*$", t_nb)
        if m:
            cur = clean(m.group(1)).rstrip(":")
            out.setdefault(cur, [])
            continue
        # 'Estrategias didacticas del profesor Actividad aula' en una sola linea
        m2 = re.match(r"^estrategias\s+did[aá]cticas\s+del\s+profesor\s+(actividad.*)$", t_nb, re.I)
        if m2:
            cur = clean(m2.group(1)).rstrip(":.")
            out.setdefault(cur, [])
            continue
        if KNOWN_LABELS.match(unbold(t_nb)):
            cur = unbold(t_nb).rstrip(":.")
            out.setdefault(cur, [])
            continue
        out.setdefault(cur, []).append(t)
    return out


def bullets(lines):
    items = []
    for l in lines:
        t = l.strip()
        if not t:
            continue
        if re.match(r"^[-*•]\s+", t):
            items.append(re.sub(r"^[-*•]\s+", "", t))
        elif items:
            items[-1] += " " + t
        else:
            items.append(t)
    return [unbold(i) for i in items]


HOURS = re.compile(r"\(\s*HAD\s*:\s*(\d+)\s*\)\s*[–—-]?\s*\(\s*HT[I]?\s*:\s*(\d+)\s*\)", re.I)


def parse_contenido(lines):
    units = []
    for l in lines:
        t = l.strip()
        if not t:
            continue
        if re.match(r"^[-*•]\s+", t):
            units.append(re.sub(r"^[-*•]\s+", "", t))
        elif units:
            units[-1] += " " + t
        else:
            units.append(t)
    # une titulos en negrita sueltos con la vineta siguiente (p.ej. Ingenieria de Metodos)
    merged = []
    pending = None
    for u in units:
        if pending is not None:
            u = pending + " " + u
            pending = None
        if re.match(r"^\*\*[^*]+\*\*\s*[:.]?\s*$", u) and not HOURS.search(u):
            pending = u
            continue
        merged.append(u)
    if pending:
        merged.append(pending)
    units = merged
    res = []
    for u in units:
        had = hti = None
        m = HOURS.search(u)
        if m:
            had, hti = int(m.group(1)), int(m.group(2))
            u = (u[: m.start()] + u[m.end():]).strip()
        title, rest = "", u
        m2 = re.match(r"^\*\*(.+?)\*\*\s*[:.]?\s*(.*)$", u)
        if m2:
            title = unbold(m2.group(1)).rstrip(":.")
            rest = m2.group(2)
        res.append({"titulo": title, "detalle": unbold(rest).strip(" .;"), "had": had, "hti": hti, "raw": unbold(u)})
    return res


def parse_header(lines):
    d = {}
    for l in lines:
        m = re.match(r"^\|\s*\*\*(.+?)\*\*\s*\|\s*(.*?)\s*\|\s*$", l.strip())
        if m:
            d[unbold(m.group(1))] = m.group(2).strip()
    return d


def parse_eval(lines):
    rows = []
    for l in lines:
        t = l.strip()
        if not t.startswith("|") or re.match(r"^\|\s*:?-{3,}", t) or "Método / Actividad" in t:
            continue
        cells = [c.strip() for c in t.strip("|").split("|")]
        if len(cells) >= 2:
            pct = re.search(r"(\d+)\s*%", cells[-1])
            parts = [clean(x) for x in re.split(r"<br\s*/?>", cells[0])]
            parts = [re.sub(r"^[-•]\s*", "", unbold(p)) for p in parts if p.strip()]
            rows.append({"actividades": parts, "porcentaje": int(pct.group(1)) if pct else None, "porcentaje_raw": cells[-1]})
    return rows


def split_sections(body_lines):
    secs = collections.OrderedDict()
    cur = 0
    secs[0] = {"titulo": "(preambulo)", "lines": []}
    footer = []
    in_footer = False
    for l in body_lines:
        if re.match(r"^###\s+Convenciones", l):
            in_footer = True
            continue
        if in_footer:
            footer.append(l)
            continue
        # encabezado de Contenido mal formado (p.ej. '**En el entorno laboral4. Contenido**')
        mg = re.search(r"^(.*?)4\.\s*Contenido\b", l)
        if mg and cur < 4 and not l.startswith("###"):
            stray = re.sub(r"\*", "", mg.group(1)).strip()
            if stray:
                secs[cur]["lines"].append(stray)
            cur = 4
            secs[cur] = {"titulo": "Contenido", "lines": []}
            continue
        m = re.match(r"^###\s+(\d+)\.\s*(.*)$", l)
        if m:
            n = int(m.group(1))
            if n > cur:
                cur = n
                secs[cur] = {"titulo": clean(m.group(2)), "lines": []}
                continue
            # numeral repetido (p.ej. '### 3.' dentro de Contenido): se descarta el encabezado
            continue
        secs[cur]["lines"].append(l)
    return secs, footer


def parse_file(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    lines = text.splitlines()
    title = ""
    for l in lines:
        if l.startswith("# "):
            title = clean(l[2:])
            break
    idx = next((i for i, l in enumerate(lines) if l.startswith("## Descripci")), len(lines))
    header = parse_header(lines[:idx])
    secs, footer = split_sections(lines[idx + 1:])
    rec = {"archivo": os.path.basename(path), "titulo_md": title, "header": header, "footer": clean(" ".join(footer))}

    # Tipo
    tipo_raw = header.get("Tipo de asignatura", "")
    m = re.search(r"\[\s*[xX]\s*\]\s*(Obligatoria|Electiva)", tipo_raw)
    rec["tipo"] = m.group(1) if m else clean(tipo_raw)
    rec["tipo_raw"] = clean(tipo_raw)

    S = lambda n: secs.get(n, {"lines": [], "titulo": ""})["lines"]
    rec["secciones_presentes"] = sorted(k for k in secs if k)
    rec["breve_descripcion"] = unbold(" ".join(l for l in S(1) if l.strip() and not l.startswith("#")))
    obj = split_labeled(S(2))
    rec["objetivos_raw"] = unbold(" ".join(" ".join(v) for v in obj.values()))
    o_prog = o_asig = ""
    for l in S(2):
        t = l.strip()
        m1 = re.match(r"^\*\*Objetivo\s+Del\s+Programa\*\*\s*:?\s*(.*)$", t, re.I)
        m2 = re.match(r"^\*\*Objetivo\s+(de\s+la\s+)?Asignatura\*\*\s*:?\s*(.*)$", t, re.I)
        if m1:
            o_prog = unbold(m1.group(1))
        elif m2:
            o_asig = unbold(m2.group(2))
    rec["objetivo_programa"] = o_prog
    rec["objetivo_asignatura"] = o_asig

    # Seccion 3
    s3 = S(3)
    idx_prog = idx_asig = idx_int = None
    for i, l in enumerate(s3):
        t = re.sub(r"^[-*•]\s+", "", l.strip())
        if re.match(r"^\**\s*Resultados?\s+de\s+Aprendizaje\s+del\s+Programa", t, re.I):
            idx_prog = i
        elif re.match(r"^\**\s*Resultados?\s+de\s+Aprendizaje\s+de\s+la\s+Asignatura", t, re.I):
            idx_asig = i
        elif re.match(r"^\**\s*Resultados?\s+de\s+aprendizaje\s+de\s+formaci", t, re.I):
            idx_int = i
    s3 = [l for l in s3 if not l.strip().startswith("#")] if False else s3
    rec["s3_marcadores"] = [idx_prog, idx_asig, idx_int]
    ends = sorted(x for x in (idx_prog, idx_asig, idx_int, len(s3)) if x is not None)
    def seg(a):
        if a is None:
            return []
        b = min(x for x in ends if x > a)
        return [x for x in s3[a + 1:b] if not x.strip().startswith("#")]
    prog_lines = [l for l in seg(idx_prog) if l.strip()]
    rec["rap_programa_raw"] = unbold(" ".join(prog_lines))
    rap_codes = re.findall(r"RAP\s*\.?\s*(\d+)", " ".join(prog_lines))
    if not rap_codes:
        for l in s3:
            mm = re.match(r"^[-*\s]*\**\s*RAP\s*(\d+)\b\.?\**\s*(.*)$", l.strip())
            if mm:
                rap_codes.append(mm.group(1))
                prog_lines = prog_lines or [l]
                rec_rap_text = unbold(l)
                prog_lines = [l]
                rec["rap_programa_raw"] = unbold(l)
                rec["rap_lineas"] = [unbold(l)]
                break
    rec["rap_codigos"] = sorted(set(rap_codes), key=int)
    rec["rap_lineas"] = [unbold(l) for l in prog_lines]
    rec["resultados_asignatura"] = bullets(seg(idx_asig))
    integ = [l for l in seg(idx_int) if l.strip()]
    rec["formacion_integral_raw"] = [unbold(l) for l in integ]
    comps = []
    for l in integ:
        t = l.strip()
        m = re.match(r"^[-*]?\s*\*\*(.+?)\*\*\s*$", t)
        if m:
            comps.append(unbold(m.group(1)))
        elif not t.startswith(("-", "*", "#")) and len(t) < 60 and ":" not in t and not t.startswith("En el entorno"):
            comps.append(unbold(t))
    rec["formacion_integral_comp"] = comps

    # Seccion 4 contenido
    rec["contenido"] = parse_contenido(S(4))
    rec["contenido_raw_lines"] = [l for l in S(4) if l.strip()]

    # Seccion 5
    s5 = S(5)
    req_main = []
    comp_prev = ""
    for l in s5:
        t = l.strip()
        if not t:
            continue
        m = re.match(r"^\*\*Competencia[s]?\s+que\s+debe[n]?\s+cumplir:?\*\*\s*(.*)$", t, re.I)
        if m:
            comp_prev = unbold(m.group(1))
            continue
        req_main.append(unbold(t))
    rec["requisitos"] = req_main
    rec["competencia_previa"] = comp_prev
    rec["s5_raw"] = [unbold(l) for l in s5 if l.strip()]

    # Seccion 6
    s6 = split_labeled(S(6))
    rec["recursos"] = {k: bullets(v) for k, v in s6.items() if v}

    # Seccion 7
    s7 = split_labeled(S(7))
    rec["didactica"] = {k: bullets(v) for k, v in s7.items() if v}

    # Seccion 8
    rec["lab_proyectos"] = [unbold(l) for l in S(8) if l.strip() and not l.startswith("#")]

    # Seccion 9
    s9 = split_labeled(S(9))
    rec["metodos_aprendizaje_bloques"] = {k: bullets(v) for k, v in s9.items() if v}

    # Seccion 10
    rec["evaluacion"] = parse_eval(S(10))
    rec["evaluacion_raw"] = [l for l in S(10) if l.strip()]
    return rec


def main():
    root, out = sys.argv[1], sys.argv[2]
    recs = []
    for area in AREA_ORDER:
        d = os.path.join(root, area)
        if not os.path.isdir(d):
            print("FALTA AREA", area)
            continue
        for f in sorted(os.listdir(d)):
            if f.endswith(".md"):
                r = parse_file(os.path.join(d, f))
                r["area_carpeta"] = area
                recs.append(r)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(recs, fh, ensure_ascii=False, indent=1)
    print("OK", len(recs), "registros ->", out)
    if "--stats" in sys.argv:
        for r in recs:
            print("-" * 70)
            print(r["archivo"], "| tipo:", r["tipo"], "| secc:", r["secciones_presentes"], "| s3:", r["s3_marcadores"])
            print("  n_resultados:", len(r["resultados_asignatura"]), "| rap:", r["rap_codigos"], "| integral:", r["formacion_integral_comp"])
            print("  contenido n:", len(r["contenido"]), "| sin horas:", [c["titulo"][:30] for c in r["contenido"] if c["had"] is None])
            print("  recursos labels:", list(r["recursos"].keys()))
            print("  didactica labels:", list(r["didactica"].keys()))
            print("  s9 labels:", list(r["metodos_aprendizaje_bloques"].keys()))
            print("  eval:", [(e["porcentaje"]) for e in r["evaluacion"]], "| comp_prev?", bool(r["competencia_previa"]))
            print("  header keys:", [k for k in r["header"].keys()] if len(r["header"]) != 11 else "11 ok")


if __name__ == "__main__":
    main()
