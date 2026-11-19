# Hallazgos de calidad de datos (detección automática)

Observaciones sobre consistencia, completitud y forma de los microcurrículos. Son hallazgos para depurar, no juicios sobre el contenido académico.

## 1. Códigos de asignatura repetidos

- **II8D3** está en 2 microcurrículos: Mercados II (Obligatoria, carpeta Área Administrativa); Gestión Administrativa y Desarrollo Organizacional (Electiva, carpeta Electivas de formación profesional)
- **II923** está en 2 microcurrículos: Formulación y Evaluación de Proyectos (Obligatoria, carpeta Área Financiera); Optimización Financiera (Electiva, carpeta Electivas de formación profesional)
- **IIP01** está en 2 microcurrículos: Logística (Electiva, carpeta Electivas de formación profesional); Product Design (Electiva, carpeta Electivas de formación profesional)

## 2. Nombres de archivo: desajustes y marcas de borrador

- Archivo `IIOD3 Producción III.md` vs. código del encabezado `II0D3`
- Archivo `IIOF3 Control Total de la Calidad.md` vs. código del encabezado `II0F3`
- Marca de borrador/versión en el nombre: `II7A3 Mercados I Observaciones.md`
- Marca de borrador/versión en el nombre: `II8D3 Mercados II Observaciones.md`
- Marca de borrador/versión en el nombre: `II713 Procesos Estocásticos (1).md`
- Marca de borrador/versión en el nombre: `II863 Simulación (1).md`
- Marca de borrador/versión en el nombre: `II8B3 Investigación de Operaciones II (1).md`
- Marca de borrador/versión en el nombre: `II8D3 Gestión Administrativa y Desarrollo Organizacional (1) (2).md`
- Marca de borrador/versión en el nombre: `II923 Optimización Financiera_Propuesta (1).md`

## 3. Área del encabezado vs. carpeta

- II123 Introducción a la Ingeniería Industrial: carpeta «Área Administrativa» · encabezado «Administración»
- II321 Sicología Organizacional: carpeta «Área Administrativa» · encabezado «Administración»
- II3B3 Administración: carpeta «Área Administrativa» · encabezado «Administración»
- II4B3 Administración de Personal: carpeta «Área Administrativa» · encabezado «Administración»
- II6C3 Administración de salarios: carpeta «Área Administrativa» · encabezado «Administración»
- II7A3 Mercados I: carpeta «Área Administrativa» · encabezado «Administración»
- II8D3 Mercados II: carpeta «Área Administrativa» · encabezado «Administración»
- II8D3 Gestión Administrativa y Desarrollo Organizacional: carpeta «Electivas de formación profesional» · encabezado «Administrativa»
- II923 Optimización Financiera: carpeta «Electivas de formación profesional» · encabezado «Financiera»
- IIA03 Comercio Internacional: carpeta «Electivas de formación profesional» · encabezado «Administrativa»
- IIE07 Automatización y Robótica Industrial: carpeta «Electivas de formación profesional» · encabezado «Producción»
- IIO08 Ecosistemas y Organización: carpeta «Electivas de formación profesional» · encabezado «Administrativa»
- IIP01 Logística: carpeta «Electivas de formación profesional» · encabezado «Producción»
- IIP01 Product Design: carpeta «Electivas de formación profesional» · encabezado «Producción»
- IIP02 Six Sigma: carpeta «Electivas de formación profesional» · encabezado «Producción»
- IIP03 Lean Manufacturing: carpeta «Electivas de formación profesional» · encabezado «Producción»
- UV093 Gestión Tecnológica: carpeta «Electivas de formación profesional» · encabezado «Administrativa»

## 4. Dígito del código vs. semestre declarado

El primer dígito del código (p. ej. II**6**A3) sugiere el semestre en una malla de 10 semestres (0 = 10.º); se compara con el semestre que declara el microcurrículo, que llega hasta el 12.º y por tanto no es válido para un programa de 10.

| Código | Asignatura | Dígito | Semestre declarado | ¿Coincide? |
|---|---|--:|---|:-:|
| II123 | Introducción a la Ingeniería Industrial | 1 | Primer semestre – Primer año | sí |
| II321 | Sicología Organizacional | 3 | Tercer semestre – Segundo año | sí |
| II3B3 | Administración | 3 | Segundo semestre – Primer año | NO |
| II4B3 | Administración de Personal | 4 | Cuarto semestre – Segundo año | sí |
| II6C3 | Administración de salarios | 6 | Sexto semestre – Tercer año | sí |
| II7A3 | Mercados I | 7 | Octavo semestre – Cuarto año | NO |
| II8D3 | Mercados II | 8 | Noveno semestre – Quinto año | NO |
| II243 | Contabilidad de Empresas | 2 | Sexto semestre – Tercer año | NO |
| II3C3 | Economía | 3 | Quinto semestre – Tecer año | NO |
| II4A3 | Sistema de Costeo | 4 | Séptimo semestre – Cuarto año | NO |
| II6A3 | Análisis Financiero | 6 | Octavo semestre – Cuarto año | NO |
| II8C3 | Ingeniería Económica | 8 | Noveno semestre – Quinto año | NO |
| II923 | Formulación y Evaluación de Proyectos | 9 | Onceavo semestre – Sexto año | NO |
| II152 | Informática I | 1 | Segundo semestre – Primer año | NO |
| II212 | Informática T2 | 2 | Tercer semestre – Segundo año | NO |
| II4D3 | Estadística I | 4 | Cuarto semestre – Segundo año | sí |
| II5A3 | Estadística II | 5 | Quinto semestre – tercer año | sí |
| II6A2 | Estadística III | 6 | Sexto semestre – Tercer año | sí |
| II713 | Procesos Estocásticos | 7 | Decimo semestre – Quinto año | NO |
| II7D3 | Investigación de Operaciones I | 7 | Octavo semestre – Cuarto año | NO |
| II863 | Simulación | 8 | Onceavo semestre – Sexto año | NO |
| II8B3 | Investigación de Operaciones II | 8 | Noveno semestre – Quinto año | NO |
| II742 | Ingeniería de Métodos | 7 | Noveno semestre – Quinto año | NO |
| II883 | Salud Ocupacional | 8 | Decimo semestre- Quinto año | NO |
| II8A3 | Producción I | 8 | Octavo semestre - Cuarto año | sí |
| II9B2 | Diseño de Plantas | 9 | Onceavo semestre - Sexto año | NO |
| II9C3 | Producción II | 9 | Noveno semestre - Quinto año | sí |
| II0D3 | Producción III | 0 | Doceavo semestre - Sexto año | NO |
| II0F3 | Control Total de la Calidad | 0 | Doceavo semestre - Sexto año | NO |
| II8D3 | Gestión Administrativa y Desarrollo Organizacional | 8 | Doceavo semestre – Sexto año | NO |
| II923 | Optimización Financiera | 9 | Doceavo semestre – Sexto año | NO |
| IIA03 | Comercio Internacional | — | Decimo semestre – quinto año | — |
| IIE07 | Automatización y Robótica Industrial | — | Octavo semestre - Cuarto año | — |
| IIO08 | Ecosistemas y Organización | — | Decimo semestre II- 8º semestre AE | — |
| IIP01 | Logística | — | Doceavo semestre – Sexto año | — |
| IIP01 | Product Design | — | Doceavo semestre – Sexto año | — |
| IIP02 | Six Sigma | — | Octavo semestre - Cuarto año | — |
| IIP03 | Lean Manufacturing | — | Octavo semestre - Cuarto año | — |
| UV093 | Gestión Tecnológica | — | Doceavo semestre – Sexto año | — |

## 5. Estructura de la plantilla

- Encabezado «### 3. Resultados de Aprendizaje» repetido dentro de Contenido (artefacto de plantilla): 33 microcurrículos.
- Abreviatura «(HT: n)» en lugar de «(HTI: n)»: II742.
- Sin encabezado «### 4. Contenido» (texto corrupto): II742.

## 6. Contenido sin horas, horas atípicas y evaluación inconsistente

- II4B3 Administración de Personal: 2 de 9 unidades sin horas HAD/HTI.
- II7A3 Mercados I: 3 de 11 unidades sin horas HAD/HTI.
- II8D3 Mercados II: 1 de 8 unidades sin horas HAD/HTI.
- II212 Informática T2: 7 de 14 unidades sin horas HAD/HTI.
- II4D3 Estadística I: 1 de 5 unidades sin horas HAD/HTI.
- II8B3 Investigación de Operaciones II: 1 de 7 unidades sin horas HAD/HTI.
- II9B2 Diseño de Plantas: 5 de 9 unidades sin horas HAD/HTI.
- II0F3 Control Total de la Calidad: 3 de 9 unidades sin horas HAD/HTI.
- II8D3 Gestión Administrativa y Desarrollo Organizacional: 3 de 8 unidades sin horas HAD/HTI.
- IIP01 Product Design: 2 de 8 unidades sin horas HAD/HTI.
- UV093 Gestión Tecnológica: 1 de 6 unidades sin horas HAD/HTI.
- II321 Sicología Organizacional: horas atípicas HAD 48 / HTI 16.
- II4B3 Administración de Personal: horas atípicas HAD 68 / HTI 85.
- II4A3 Sistema de Costeo: horas atípicas HAD 64 / HTI 90.
- II8C3 Ingeniería Económica: horas atípicas HAD 40 / HTI 50.
- II212 Informática T2: horas atípicas HAD 48 / HTI 48.
- II4D3 Estadística I: horas atípicas HAD 60 / HTI 62.
- II5A3 Estadística II: horas atípicas HAD 60 / HTI 64.
- II6A2 Estadística III: horas atípicas HAD 42 / HTI 42.
- II713 Procesos Estocásticos: horas atípicas HAD 64 / HTI 84.
- II7D3 Investigación de Operaciones I: horas atípicas HAD 64 / HTI 85.
- II742 Ingeniería de Métodos: horas atípicas HAD 64 / HTI 77.
- IIE07 Automatización y Robótica Industrial: horas atípicas HAD 64 / HTI 85.
- IIP01 Product Design: horas atípicas HAD 66 / HTI 80.
- UV093 Gestión Tecnológica: horas atípicas HAD 48 / HTI 96.
- II123 Introducción a la Ingeniería Industrial: evaluación suma 180%.
- II321 Sicología Organizacional: evaluación suma 130%.
- II6C3 Administración de salarios: evaluación suma 160%.
- II9B2 Diseño de Plantas: evaluación suma 70%.
- IIA03 Comercio Internacional: evaluación suma 130%.
- IIP01 Product Design: evaluación suma 60%.

## 7. Campos faltantes o anómalos

- II883 Salud Ocupacional: sin estrategias TIC
- II8D3 Gestión Administrativa y Desarrollo Organizacional: sin competencias de formación integral
- II923 Optimización Financiera: solo 1 resultado(s) de aprendizaje de la asignatura
- IIP01 Product Design: sin estrategias TIC

## 8. Semestres declarados fuera de la malla de 10 (11.º y 12.º)

- II923 Formulación y Evaluación de Proyectos: «Onceavo semestre – Sexto año»
- II863 Simulación: «Onceavo semestre – Sexto año»
- II9B2 Diseño de Plantas: «Onceavo semestre - Sexto año»
- II0D3 Producción III: «Doceavo semestre - Sexto año»
- II0F3 Control Total de la Calidad: «Doceavo semestre - Sexto año»
- II8D3 Gestión Administrativa y Desarrollo Organizacional: «Doceavo semestre – Sexto año»
- II923 Optimización Financiera: «Doceavo semestre – Sexto año»
- IIP01 Logística: «Doceavo semestre – Sexto año»
- IIP01 Product Design: «Doceavo semestre – Sexto año»
- UV093 Gestión Tecnológica: «Doceavo semestre – Sexto año»
