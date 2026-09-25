# Sprint 1 — Baseline longitudinal y evolución del estudio CIMPS
## README — Documentación del proceso

**Estudiante:** William Tehuatle Sosa
**Proyecto:** Gestión de la Deuda Técnica — línea de investigación **Ruta B**
(archivos que concentran cambios / hotspots y contexto de commits, issues y pull requests)

---

## 1. Objetivo del sprint y pregunta rectora

Este sprint da continuidad al artículo enviado a CIMPS 2026, que analizó la deuda técnica de código
en ocho proyectos Java de código abierto **en un único momento** (un *snapshot* por proyecto). El
objetivo de esta etapa **no** es entrenar modelos ni demostrar priorización, sino comprobar la
**factibilidad** de un estudio longitudinal:

> **Pregunta rectora:** ¿Podemos reconstruir de manera trazable la evolución de los proyectos usados
> en CIMPS, seguir los archivos a través del tiempo e identificar eventos posteriores que permitan
> preparar un nuevo estudio experimental **sin utilizar información del futuro**?

El sprint se considera exitoso cuando hay evidencia para responder tres preguntas: (1) ¿podemos
seguir archivos de forma confiable a través del tiempo?, (2) ¿podemos obtener información histórica
sin usar datos futuros?, y (3) ¿los repositorios ofrecen trazabilidad suficiente para diseñar el
siguiente experimento?

---

## 2. Información del entorno (reproducibilidad)

| Elemento | Valor |
|---|---|
| Sistema operativo | Windows 10 (build 26200) — terminal Git Bash / MINGW64 |
| Versión de Git | git 2.52.0.windows.1 |
| Versión de Java | OpenJDK 17.0.17 (Temurin-17.0.17+10) |
| Versión de Python | 3.8.10 (no utilizado; los scripts se ejecutaron en Bash) |
| Versión de RefactoringMiner | Pendiente — se instala en D4 |
| Repositorios analizados | Los 8 del corpus CIMPS (ver §4) |
| Proyecto piloto | `apache/commons-lang`, rama `master` |
| Commit de referencia CIMPS (commons-lang) | `rel/commons-lang-3.20.0` → `598dfc163b8b` (2025-11-12) |
| decision_time (D3) | 2025-11-12 (fecha del snapshot CIMPS) |
| Fechas de ejecución | 2026-09-15 a 2026-09-21 |

**Nota sobre el commit de referencia:** el inventario y las prácticas se realizaron sobre el
repositorio en su rama `master` (historia completa). El commit exacto que analizó CIMPS
(`598dfc163b8b`) se usa como `decision_time` en D3: todas las métricas emplean exclusivamente
información anterior a esa fecha.

---

## 3. Estado de los entregables

| Entregable | Descripción | Estado |
|---|---|---|
| D1 | Revisión de literatura (CIMPS, Carvalho 2026, Tsoukalas 2024) | **En curso** — CIMPS y Carvalho revisados; falta Tsoukalas y la matriz formal |
| D2 | Inventario de observabilidad de los 8 proyectos | **Completo** — 8/8 inspeccionados con evidencia (`D2_CIMPS8_OBSERVABILIDAD.csv`) |
| D3 | Identidad de artefactos + dataset de evolución | **Completo** — 10 archivos con identidad, 30 con métricas, verificación de 3 casos, análisis documentado |
| D4 | RefactoringMiner + control de fuga temporal | **Pendiente** |
| D5 | Plan de evolución CIMPS → estudio longitudinal | **Pendiente** |

---

## 4. D2 — Inventario de observabilidad de los 8 proyectos

### 4.1 Qué es y para qué

D2 no analiza la deuda técnica: **inventaría qué tan observable es cada repositorio** para un estudio
longitudinal. Para cada proyecto se inspeccionó el repositorio real (rama, historial, tags,
estructura Java, issues, pull requests, tracker externo) y se registró la evidencia mínima.

### 4.2 Comandos utilizados (ejecutados en cada repositorio)

```bash
git branch -a                                   # rama principal y ramas existentes
git rev-list --all --count                      # total de commits
git log --reverse --format=%cd --date=short | head -1   # fecha del primer commit
git log -1 --format=%cd --date=short            # fecha del último commit
git tag | wc -l                                 # número de releases/tags
ls src/main/java  ||  find . -type d -path "*/src/main/java"   # estructura Java
git log --oneline -10                           # inspección de mensajes de commit
git log --oneline --all | grep -iE "<PREFIJO>-[0-9]+"   # detección de JIRA (p.ej. LANG-, MATH-)
```

Los datos de issues y pull requests se verificaron directamente en la interfaz de GitHub
(pestañas *Issues* y *Pull requests*, contadores Open/Closed).

### 4.3 Resultado — Inventario de los 8 proyectos

| Proyecto | Rama | Commits | Primer commit | Último commit | Tags | Estructura Java | Tracker | PRs (open/closed) |
|---|---|---|---|---|---|---|---|---|
| checkstyle | master | 19,589 | 2001-06-22 | 2026-09-14 | 223 | mono-módulo `src/main/java` | GitHub Issues | 82 / 14,900 |
| commons-collections | master | 5,690 | 2001-04-14 | 2026-09-07 | 59 | mono-módulo `src/main/java` | JIRA (COLLECTIONS) | 32 / 703 |
| commons-lang | master | 10,278 | 2002-07-19 | 2026-09-13 | 113 | mono-módulo `src/main/java` | JIRA (LANG) | 58 / 1,721 |
| commons-math | master | 8,339 | 2003-05-12 | 2026-08-31 | 67 | **multi-módulo** (reorganizado) | JIRA (MATH) | 64 / 253 |
| httpcomponents-client | master | 5,099 | 2005-12-21 | 2026-08-26 | 216 | **multi-módulo** | JIRA (HTTPCLIENT) | 12 / 865 |
| junit4 | main | 2,710 | 2000-12-03 | 2026-08-13 | 28 | mono-módulo `src/main/java` | GitHub Issues | 0 / 902 |
| maven | master | 20,081 | 2003-09-01 | 2026-09-14 | 113 | **multi-módulo profundo** | JIRA (MNG) + GitHub Issues | 96 / 4,326 |
| pdfbox | trunk | 23,734 | 2008-02-10 | 2026-09-14 | 84 | **multi-módulo** | JIRA (PDFBOX) | 42 / 484 |

*Ningún proyecto fue excluido: el objetivo de D2 es conocer la observabilidad, no seleccionar.*

### 4.4 Hallazgos principales de D2

1. **El corpus no es homogéneo en dónde vive el contexto de un cambio.** Tres modelos: contexto en
   **GitHub Issues** (checkstyle, junit4), en **JIRA** (los cuatro Apache Commons, httpcomponents,
   pdfbox — con la pestaña Issues de GitHub desactivada), o en **ambos** (maven). *Implicación para
   la Ruta B:* la recolección de contexto (issues/PR) deberá adaptarse por proyecto.
2. **La estructura de código varía mucho.** Cuatro mono-módulo con `src/main/java` limpio y cuatro
   multi-módulo (commons-math, además, reorganizado respecto a su propio snapshot CIMPS). Esto
   condiciona qué tan fácil es seguir un archivo a través del tiempo.
3. **Conviven tres nombres de rama principal** (`master`, `main`, `trunk`), señal de migraciones (por
   ejemplo, pdfbox migró de Subversion). Pueden introducir saltos en el historial.
4. **Un proyecto está en modo mantenimiento:** junit4 (desarrollo migrado a JUnit 5); su historial
   cerrado (836 issues, 902 PR) sigue siendo material útil.

---

## 5. Selección del proyecto piloto

Se eligió **commons-lang** para desarrollar el procedimiento en D3/D4, por los cuatro criterios del
sprint (no por conveniencia de resultados):

- **Historial accesible y largo:** 10,278 commits desde 2002; 113 releases.
- **Estructura Java clara:** `src/main/java` estándar y mono-módulo.
- **Actividad suficiente:** activo hasta 2026-09-13; no está en modo mantenimiento.
- **Tamaño manejable:** mediano; sin ser inmanejable como checkstyle, maven o pdfbox.

*Alternativa (plan B):* commons-collections.

---

## 6. D3 — Identidad de artefactos y dataset de evolución

### 6.1 Identidad del artefacto (`D3_ARTIFACT_IDENTITY.csv`)

Seguir un archivo en el tiempo exige poder afirmar —con evidencia— que dos rutas distintas
corresponden al mismo artefacto pese a renombres/movimientos. Se siguieron **10 archivos** con
`git log --follow --name-status`, registrando 22 eventos de identidad (nacimientos, renames y moves).

**Caso demostrativo — `StringUtils.java`:** nace el 2002-07-19 (`6627f7ad8`) y se mueve dos veces,
ambas detectadas por Git con similitud del 100 % (`R100`):

```
src/java/org/apache/commons/lang/StringUtils.java
        |  debc02c6d (2009-12-10)  "Changing directory name from lang to lang3 ... LANG-563"
        v
src/java/org/apache/commons/lang3/StringUtils.java
        |  fc5c081e2 (2010-01-03)  "Move main source to src/main/java"
        v
src/main/java/org/apache/commons/lang3/StringUtils.java   (ubicación actual)
```

La identidad se sostiene en dos evidencias independientes: el `R100` (100 % de similitud) y el
mensaje de commit (que además cita el ticket JIRA **LANG-563**). Cadena **archivo -> commit ->
movimiento -> ticket JIRA**, rastreable hasta el issue tracker.

**Hallazgo:** la fecha de nacimiento predice la complejidad de identidad. Los 5 archivos anteriores a
2010 vivieron dos migraciones de proyecto (paquete `lang->lang3` y layout `src/java->src/main/java`);
los 4 archivos nacidos después no tienen ningún rename. Esos dos moves **no son actividad de cada
archivo, sino eventos globales del proyecto** que arrastraron a todos los archivos vivos a la vez.

### 6.2 Dataset de evolución (`D3_EVOLUTION_DATASET.csv`)

Para 30 archivos (muestra estratificada: 10 hotspots + 10 medios + 10 tranquilos) se calcularon 6
métricas usando exclusivamente información anterior al `decision_time` (2025-11-12):
`prior_commits`, `lines_added`, `lines_deleted`, `churn`, `days_since_last_change`,
`distinct_contributors`.

**Regla temporal (obligatoria):** `feature_timestamp <= decision_time`. Todos los `git log` llevan
`--before="2025-11-12"`; ningún dato proviene de commits posteriores. Generado por
`scripts/build_evolution_dataset.sh` (reproducible desde el repo + commit).

### 6.3 Verificación manual (criterio de aceptación)

Se comprobaron 3 archivos (uno por estrato) contra el historial de Git; los tres coinciden:

| Archivo | Estrato | prior_commits | distinct_contributors | ¿Coincide? |
|---|---|---|---|---|
| StringUtils | Hotspot | 716 | 93 | Sí |
| TimeZones | Medio | 33 | 10 | Sí |
| AppendableJoiner | Tranquilo | 3 | 2 | Sí |

### 6.4 Análisis (`D3_Analisis_Evolucion.docx`)

Cuatro hallazgos: (1) la estratificación separa tres regímenes de actividad por dos órdenes de
magnitud; (2) `prior_commits` y `distinct_contributors` están casi perfectamente correlacionados
(0.99); (3) el churn se concentra de forma extrema (5 archivos = 79 % del churn total); (4) el commit
`a82f4cb50` ("Update Apache License URL to HTTPS", 2025-05-20) tocó 511 archivos y **contamina**
`days_since_last_change` — un evento global que se disfraza de actividad individual.

---

## 7. Conceptos clave

- **Snapshot vs. longitudinal:** CIMPS analizó una sola *foto*; el estudio longitudinal observa la
  *película* (varios momentos).
- **Identidad del artefacto:** afirmar, con evidencia, que dos rutas son el mismo archivo pese a
  renombres/movimientos.
- **`R100`:** rename detectado por Git con 100 % de similitud de contenido.
- **Churn / hotspot:** cambio acumulado (líneas +/-); un archivo con mucho churn es un *hotspot*.
- **Fuga de información temporal (*temporal leakage*):** usar un dato que en el momento analizado
  todavía no existía.

**Distinciones que el proceso mantiene** (para no sobre-interpretar la evidencia):
análisis estático != deuda técnica total · alta frecuencia de cambio != deuda · refactoring != pago
de deuda · asociación != causalidad.

---

## 8. Respuesta a las tres preguntas de cierre del sprint

1. **¿Podemos seguir archivos de forma confiable a través del tiempo?** **Sí.** De 10 archivos, los
   10 fueron rastreables sin ambigüedad (`R100` en los movidos; sin rename en los nacidos después de
   las migraciones). Cero casos ambiguos en la muestra de commons-lang (mono-módulo).
2. **¿Podemos obtener información histórica sin usar datos futuros?** **Sí.** El dataset aplica la
   regla temporal `--before=decision_time` en todas las métricas; reproducible desde repo + commit.
3. **¿Hay trazabilidad suficiente para diseñar el siguiente experimento?** **Sí, con salvedades:** la
   fuente de contexto (GitHub Issues vs. JIRA) varía por proyecto, y hay eventos globales
   (migraciones, cambio de licencia) que deben distinguirse de la actividad individual.

---

## 9. Amenazas a la validez identificadas (para D4 y D5)

1. **Churn inflado por merges:** el conteo con `--numstat` puede sumar líneas ya contadas en commits
   de fusión. Por eso se hace verificación manual.
2. **Métricas contaminadas por eventos globales:** el commit de licencia afectó a 511 archivos; un
   pipeline futuro deberá filtrar commits masivos/triviales.

---

## 10. Qué sigue

- **D4:** instalar y ejecutar RefactoringMiner sobre un rango acotado; auditar 30 eventos; redactar
  la nota de temporal leakage (>=5 situaciones).
- **D1:** completar la revisión de literatura (incluyendo Tsoukalas 2024) en formato de fichas.
- **D5:** redactar el plan de evolución CIMPS -> estudio longitudinal, derivado de D1–D4.

---

## 11. Estructura de archivos de la entrega

```
WILLIAM_SPRINT_01/
├── README.md                        (este archivo)
├── D2_CIMPS8_OBSERVABILIDAD.csv     (inventario de los 8 proyectos — completo)
├── D3_ARTIFACT_IDENTITY.csv         (identidad de 10 archivos — 22 eventos)
├── D3_EVOLUTION_DATASET.csv         (30 archivos x 6 métricas)
├── D3_SELECCION_30.txt              (lista de los 30 archivos del dataset)
├── D3_Analisis_Evolucion.docx       (análisis de los hallazgos)
├── D1_REVISION_CIMPS_LITERATURA.md  (en curso)
├── D4_REFACTORING_EVENTS_RAW.csv    (pendiente)
├── D4_REFACTORING_AUDIT_30.csv      (pendiente)
├── D4_TEMPORAL_LEAKAGE.md           (pendiente)
├── D5_PLAN_EVOLUCION_CIMPS.md       (pendiente)
├── repos/                           (los 8 repositorios clonados — área de trabajo)
└── scripts/
    └── build_evolution_dataset.sh   (generador del dataset de evolución)
```

---

## 12. Reproducción del dataset de evolución (D3)

Desde la raíz `WILLIAM_SPRINT_01/`, en Git Bash:

```bash
bash scripts/build_evolution_dataset.sh repos/commons-lang 2025-11-12 598dfc163b8b
# genera D3_EVOLUTION_DATASET.csv y D3_SELECCION_30.txt dentro de repos/commons-lang/
```

Verificación manual de un caso (debe dar 716 y 93):

```bash
cd repos/commons-lang
git log --oneline --before=2025-11-12 --follow -- src/main/java/org/apache/commons/lang3/StringUtils.java | wc -l
git log --before=2025-11-12 --follow --format="%an" -- src/main/java/org/apache/commons/lang3/StringUtils.java | sort -u | wc -l
```
