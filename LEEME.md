# Análisis de microcurrículos y laboratorios — Ingeniería Industrial (UTP · FACIEM)

Resultado de la **primera etapa**: lectura completa, organización y análisis de los 39 microcurrículos y de los 6 documentos de laboratorio. Todo quedó en Markdown segmentado (ningún archivo supera ~530 líneas).

## Dónde empezar

1. `microcurriculos/00_INDICE_Y_SINTESIS.md` — síntesis de todo lo organizado de los microcurrículos.
2. `laboratorios/00_INDICE_Y_SINTESIS.md` — síntesis de los laboratorios.
3. `laboratorios/06_matriz_laboratorio_asignatura.md` — **cruce laboratorio × asignatura**, insumo clave para la siguiente etapa.

## Etapa 2: asignación de laboratorio por asignatura

`asignacion/00_INDICE_Y_METODO.md` — **39 de 39 asignaturas asignadas** a un laboratorio principal (con componente evaluativo y aprobatorio) y laboratorios complementarios. Incluye matriz, una ficha por laboratorio, ruta por semestre, plantilla del componente evaluativo y el impacto en cada tabla de evaluación. Se regenera editando `_herramientas/gen_asignacion.py`.

## Estructura (etapa 1)

```
Analisis/
├─ LEEME.md
├─ microcurriculos/          (15 archivos)
│  ├─ 00_INDICE_Y_SINTESIS.md          ← síntesis analítica
│  ├─ 01_panorama_asignaturas.md       ← inventario maestro
│  ├─ 02 … 08  fichas por área (Administrativa, Financiera, IO y Estadística ×2, Producción, Electivas ×2)
│  └─ 09 … 14  vistas transversales (RAP, bibliografía, pedagogía/TIC/evaluación, labs en microcurrículos, requisitos, hallazgos)
└─ laboratorios/             (9 archivos)
   ├─ 00_INDICE_Y_SINTESIS.md          ← síntesis analítica
   ├─ 01 … 05  una ficha por espacio (Financiero, GEIO, Logística, Manufactura Flexible, Consultorio)
   └─ 06 matriz lab × asignatura · 07 necesidades, brechas y riesgos · 08 competencias y aporte
```

## Cifras clave

- **39** microcurrículos (29 obligatorios, 10 electivos) · **114** créditos · **5** carpetas de área.
- **5** espacios de laboratorio documentados en **6** archivos (Manufactura Flexible viene en dos versiones del mismo texto).
- **12 de 39** microcurrículos nombran un laboratorio; **11 de 39** tienen vacía la sección de laboratorio.

## Lo más importante que apareció

1. Los laboratorios proponen usos en muchas asignaturas, pero **solo 1 de cada 6–10 está confirmada en el microcurrículo**.
2. **Sismo del 10-ago-2026:** Financiero y Consultorio perdieron su espacio; **Logística (5-111) y Manufactura Flexible (5-109) no informan su estado**.
3. **Logística:** cómputo y software obsoletos (4 estudiantes simultáneos), compra PARCE 2026 de **COP 42,1 M** sin entregar.
4. **Manufactura Flexible:** informe sin normas de seguridad, inventario ni necesidades.
5. En los microcurrículos: **códigos duplicados** (II8D3, II923, IIP01), **10 asignaturas que declaran 11.º o 12.º semestre** en un programa de **10 semestres** (las electivas profesionales van del 7.º al 10.º) y **6 evaluaciones que no suman 100 %**. *(Nota: la «secuencia contradictoria en Producción» que se reportó antes era un efecto de esa numeración y quedó descartada.)*
6. Asignaturas que los laboratorios citan y **no se entregaron**: Mercado de Capitales, Planeación Financiera, GB273, GB353, II972.

## Convenciones y límites

- Los **datos** (códigos, horas, créditos, cifras, placas, valores) provienen literalmente de los archivos fuente. Las **inferencias** del análisis están marcadas: «(c)» en la matriz, «deducidas» en competencias, «propuesta» en mapeos a RAP.
- Detecciones automáticas (herramientas por palabras clave, años de bibliografía, referencias repetidas) son **pistas**, no auditorías.
- Los archivos fuente originales **no se modificaron**.
