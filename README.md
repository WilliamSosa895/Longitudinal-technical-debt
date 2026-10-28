# Estudio longitudinal de Deuda Técnica (continuidad CIMPS)
## README — Documentación del proceso (Sprint 1 + Sprint 2)

**Estudiante:** William Tehuatle Sosa
**Proyecto:** Gestión de la Deuda Técnica — línea de investigación **Ruta B**
(archivos que concentran cambios / hotspots y contexto de commits, issues y pull requests)
**Repositorio:** github.com/WilliamSosa895/Longitudinal-technical-debt

---

## 1. Objetivo del proyecto y pregunta rectora

Este proyecto da continuidad al artículo enviado a CIMPS 2026, que analizó la deuda técnica de código
en ocho proyectos Java de código abierto **en un único momento** (un *snapshot* por proyecto). El
objetivo de esta fase **no** es entrenar modelos ni demostrar priorización, sino comprobar la
**factibilidad** de un estudio longitudinal y dejar validada la base temporal.

> **Pregunta rectora (Sprint 1):** ¿Podemos reconstruir de manera trazable la evolución de los
> proyectos usados en CIMPS, seguir los archivos a través del tiempo e identificar eventos posteriores
> que permitan preparar un nuevo estudio experimental **sin utilizar información del futuro**?

> **Pregunta rectora (Sprint 2):** ¿Podemos construir, para un mismo archivo y momento temporal,
> métricas estáticas (E1), información histórica (E2) y evidencia de co-change (E3) utilizando
> únicamente información disponible hasta ese momento?

El Sprint 1 cubre la línea longitudinal (E2). El Sprint 2 la cierra y valida (auditoría, snapshots,
separación temporal) e inicia la integración con las familias E1 y E3.

---

## 2. Información del entorno (reproducibilidad)

| Elemento | Valor |
|---|---|
| Sistema operativo | Windows 10 (build 26200) — terminal Git Bash / MINGW64 |
| Versión de Git | git 2.52.0.windows.1 |
| Versión de Java | OpenJDK 17.0.17 (Temurin-17.0.17+10) |
| Versión de RefactoringMiner | commit `88a299a43`, construido con `./gradlew installDist` |
| Repositorios analizados | Los 8 del corpus CIMPS (ver §4) |
| Proyecto piloto | `apache/commons-lang`, rama `master` |
| Commit de referencia CIMPS (commons-lang) | `rel/commons-lang-3.20.0` → `598dfc163b8b` (2025-11-12) |
| decision_time (D3) | 2025-11-12 (fecha del snapshot CIMPS) |
| Fechas de ejecución Sprint 1 | 2026-09-15 a 2026-09-27 |
| Fechas de ejecución Sprint 2 | 2026-10-14 |

**Nota sobre el commit de referencia:** el inventario y las prácticas se realizaron sobre el
repositorio en su rama `master` (historia completa). El commit exacto que analizó CIMPS
(`598dfc163b8b`) se usa como `decision_time` en D3: todas las métricas emplean exclusivamente
información anterior a esa fecha.

---

## 3. Estado de los entregables

### Sprint 1 — línea longitudinal (completo)

| Entregable | Descripción | Estado |
|---|---|---|
| D1 | Revisión de literatura (CIMPS, Carvalho 2026, Tsoukalas 2024) + matriz y gap | **Completo** — `D1_Estado_Arte_Gap.docx` |
| D2 | Inventario de observabilidad de los 8 proyectos | **Completo** — `D2_CIMPS8_OBSERVABILIDAD.csv` (8/8) |
| D3 | Identidad de artefactos + dataset de evolución | **Completo** — 10 archivos con identidad, 30 con métricas |
| D4 | RefactoringMiner + control de fuga temporal | **Completo** — 93 refactorings, 30 auditados, leakage ledger |
| D5 | Plan de evolución / autoevaluación G1A | **Completo** — `Autoevaluacion_G1A.docx` (PASS CANDIDATE) |

### Sprint 2 — validación y separación temporal (en curso)

| Actividad | Descripción | Estado |
|---|---|---|
| Auditoría | ≥10 registros del dataset verificados contra Git | **Completo** — `D3_AUDITORIA_RESULTADO.csv` (12/12) |
| Snapshots temporales | ≥3 observaciones en formato de 5 campos | **Completo** — `D3_SNAPSHOTS_TEMPORALES_OBS.csv` |
| Separación temporal | Folds walk-forward materializados (sin split aleatorio) | **Completo** — `D3_FOLD_TRAIN.csv` / `D3_FOLD_TEST.csv` |
| Lectura Robredo (2025) | Extracción de método time-dependent | **Completo** |
| Consolidación G1A | Cierre y actualización de evidencias | **En curso** |
| Integración E1+E2+E3 | Tabla conjunta con la línea hotspot/co-change (Yatana) | **Pendiente** |

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
mensaje de commit (que además cita el ticket JIRA **LANG-563**). Cadena **archivo → commit →
movimiento → ticket JIRA**, rastreable hasta el issue tracker.

**Hallazgo:** la fecha de nacimiento predice la complejidad de identidad. Los archivos anteriores a
2010 vivieron dos migraciones de proyecto (paquete `lang→lang3` y layout `src/java→src/main/java`);
los nacidos después no tienen ningún rename. Esos dos moves **no son actividad de cada archivo, sino
eventos globales del proyecto** que arrastraron a todos los archivos vivos a la vez.

### 6.2 Dataset de evolución (`D3_EVOLUTION_DATASET.csv`)

Para 30 archivos (muestra estratificada: 10 hotspots + 10 medios + 10 tranquilos) se calcularon 6
métricas usando exclusivamente información anterior al `decision_time` (2025-11-12):
`prior_commits`, `lines_added`, `lines_deleted`, `churn`, `days_since_last_change`,
`distinct_contributors`.

**Regla temporal (obligatoria):** `feature_timestamp <= decision_time`. Todos los `git log` llevan
`--before="2025-11-12"`; ningún dato proviene de commits posteriores. Generado por
`scripts/build_evolution_dataset.sh` (reproducible desde el repo + commit).

### 6.3 Verificación / auditoría (criterio de aceptación)

En el Sprint 1 se verificaron 3 casos (uno por estrato). En el **Sprint 2 la auditoría se amplió a 12
registros** contra Git, confirmando las seis dimensiones (identidad, commit/fecha, cambios previos,
churn, colaboradores y ausencia de información posterior). Resultado: **12/12 coinciden**
(`D3_AUDITORIA_RESULTADO.csv`).

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

## 7. D4 — RefactoringMiner y control de fuga temporal

Se ejecutó **RefactoringMiner** (`-bc`) sobre el ciclo `3.19.0 → 3.20.0` (117 commits no-merge, 0
errores, 93 refactorings), de modo que todos los eventos son anteriores o iguales al `decision_time`.
Se auditaron 30 eventos (estratificados por tipo) y se inspeccionaron 3 commits a fondo. Hallazgo
central: **un refactoring detectado ≠ pago de deuda técnica** (el commit `c9ff6aa44` concentra el 58 %
de los refactorings pero es un fix funcional para Java 25). Evidencia en `D4_Analisis_Refactorings.docx`,
`D4_REFACTORING_EVENTS_RAW.json/.csv` y `D4_REFACTORING_AUDIT_30.csv`.

El **registro de fuga temporal** (`D4_TEMPORAL_LEAKAGE.md`) define la regla
`feature_timestamp <= decision_time`, enumera seis situaciones de fuga (L1–L6) con su regla
preventiva, y documenta el riesgo de contaminación por eventos globales.

---

## 8. Sprint 2 — Snapshots temporales y separación temporal

### 8.1 Snapshots temporales (`D3_SNAPSHOTS_TEMPORALES_OBS.csv`)

Se definieron ≥3 observaciones archivo × tiempo con el formato de cinco campos: `proyecto +
artifact_id + decision_time + información disponible + información reservada como futuro`. Con
StringUtils en los cortes 3.18.0, 3.19.0 y 3.20.0 se demuestra que, al avanzar el corte, lo disponible
crece (700→709→716 commits) y el futuro reservado encoge (69→60→53), coincidiendo en 3.20.0 con el
dataset auditado.

### 8.2 Separación temporal materializada (`D3_FOLD_TRAIN.csv`, `D3_FOLD_TEST.csv`)

Se materializó el diseño walk-forward (sin split aleatorio): fold de entrenamiento con features ≤
3.18.0 y etiqueta en (3.18.0, 3.19.0]; fold de prueba con features ≤ 3.19.0 y etiqueta en
(3.19.0, 3.20.0]. Se verificó la invariante `max(feature_ts) ≤ T < min(label_ts)` fila por fila
(29/29 válidas en entrenamiento, 30/30 en prueba). Se detectó y previno un caso de validez temporal
(F020, ByteSupplier), reforzando el control con una verificación de existencia por tag
(`git cat-file -e`).

---

## 9. Conceptos clave

- **Snapshot vs. longitudinal:** CIMPS analizó una sola *foto*; el estudio longitudinal observa la
  *película* (varios momentos).
- **Identidad del artefacto:** afirmar, con evidencia, que dos rutas son el mismo archivo pese a
  renombres/movimientos.
- **`R100`:** rename detectado por Git con 100 % de similitud de contenido.
- **Churn / hotspot:** cambio acumulado (líneas +/-); un archivo con mucho churn es un *hotspot*.
- **Fuga de información temporal (*temporal leakage*):** usar un dato que en el momento analizado
  todavía no existía.

**Distinciones que el proceso mantiene** (para no sobre-interpretar la evidencia):
análisis estático ≠ deuda técnica total · alta frecuencia de cambio ≠ deuda · refactoring ≠ pago
de deuda · asociación ≠ causalidad.

---

## 10. Amenazas a la validez identificadas

1. **Churn inflado por merges:** el conteo con `--numstat` puede sumar líneas ya contadas en commits
   de fusión. Por eso se hace verificación manual/auditoría.
2. **Métricas contaminadas por eventos globales:** el commit de licencia afectó a 511 archivos; un
   pipeline futuro deberá filtrar commits masivos/triviales.
3. **`--follow` y sobre-atribución de identidad:** en archivos de creación reciente, `--follow` puede
   rastrear por contenido hasta un ancestro muy antiguo (p.ej. F020 rastreado hasta el commit
   fundacional de 2002). La verificación por tag de release acota este efecto.

---

## 11. Estructura de archivos de la entrega

```
Longitudinal-technical-debt/
├── README.md                             (este archivo)
├── Objetivo_Investigacion.docx           (objetivo de investigación)
├── D1_Estado_Arte_Gap.docx               (estado del arte + gap)
├── D2_CIMPS8_OBSERVABILIDAD.csv          (inventario de los 8 proyectos)
├── D3_ARTIFACT_IDENTITY.csv              (identidad de 10 archivos — 22 eventos)
├── D3_EVOLUTION_DATASET.csv              (30 archivos x 6 métricas)
├── D3_SELECCION_30.txt                   (lista de los 30 archivos)
├── D3_Analisis_Evolucion.docx            (análisis del dataset)
├── D4_REFACTORING_EVENTS_RAW.json/.csv   (salida cruda de RefactoringMiner)
├── D4_REFACTORING_AUDIT_30.csv           (auditoría de 30 eventos)
├── D4_Analisis_Refactorings.docx         (análisis de refactorings)
├── D4_TEMPORAL_LEAKAGE.md                (registro de fuga temporal L1–L6)
├── SNAPSHOTS_TEMPORALES.md               (manifiesto de snapshots T0–T5)
├── D_Separacion_Temporal.docx            (diseño walk-forward)
├── PROVENANCE_INTEGRIDAD.md              (cadena raw → output)
├── BITACORA_ERRORES_DECISIONES.md        (bitácora de errores y decisiones)
├── Autoevaluacion_G1A.docx               (autoevaluación Gate G1A)
├── (Sprint 2) D3_AUDITORIA_RESULTADO.csv
├── (Sprint 2) D3_SNAPSHOTS_TEMPORALES_OBS.csv
├── (Sprint 2) D3_FOLD_TRAIN.csv / D3_FOLD_TEST.csv
├── (Sprint 2) D_Auditoria_Dataset.docx
├── (Sprint 2) D_Snapshots_Temporales.docx
├── (Sprint 2) D_Separacion_Temporal_Materializada.docx
├── repos/                                (repositorios clonados — área de trabajo, ignorada en git)
└── scripts/
    ├── build_evolution_dataset.sh        (generador del dataset de evolución — Sprint 1)
    ├── audit_dataset.sh                  (auditoría de registros contra Git — Sprint 2)
    ├── snapshots_temporales.sh           (observaciones archivo × tiempo — Sprint 2)
    └── temporal_split.sh                 (materialización de folds walk-forward — Sprint 2)
```

---

## 12. Reproducción

Desde la raíz del proyecto (que contiene `repos/commons-lang`), en Git Bash:

```bash
# Dataset de evolución (D3)
bash scripts/build_evolution_dataset.sh repos/commons-lang 2025-11-12 598dfc163b8b

# Auditoría de registros (Sprint 2)
bash scripts/audit_dataset.sh repos/commons-lang 2025-11-12

# Snapshots temporales (Sprint 2)
bash scripts/snapshots_temporales.sh

# Separación temporal walk-forward (Sprint 2)
bash scripts/temporal_split.sh
```

Verificación manual de un caso (debe dar 716 y 93):

```bash
cd repos/commons-lang
git log --oneline --before=2025-11-12 --follow -- src/main/java/org/apache/commons/lang3/StringUtils.java | wc -l
git log --before=2025-11-12 --follow --format="%an" -- src/main/java/org/apache/commons/lang3/StringUtils.java | sort -u | wc -l
```

---

## 13. Estado del repositorio

- **Tag `sprint1-g1a-v2`** → commit `064687a` (cierre propuesto del Gate G1A).
- **Último commit Sprint 1:** `991ea46` (2026-09-27, "Cierre G1A: autoevaluacion + provenance").
- **Sprint 2:** sus evidencias se incorporarán en un commit y tag propios al cierre del sprint.
