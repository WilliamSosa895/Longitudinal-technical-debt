# Provenance e integridad — Trazabilidad de los resultados

**Proyecto: Gestión de la Deuda Técnica (continuidad CIMPS) · Proyecto piloto: commons-lang**
**Cubre Sprint 1 (G1A) y Sprint 2 (validación longitudinal)**

> Objetivo: que cualquier resultado del proyecto pueda rastrearse hasta sus entradas y hasta el código
> o el comando que lo generó. La cadena general es **raw → processed → analysis → output**.

---

## 1. Fuente primaria (raw) — el origen de todo

Todo el trabajo se deriva de un único origen inmutable:

| Elemento | Valor |
|---|---|
| Repositorio | `apache/commons-lang` (rama `master`) |
| Snapshot de referencia (CIMPS) | release 3.20.0 · commit `598dfc163b8b410fb3bb8794521206ec8dcec82a` |
| decision_time | 2025-11-12 |
| Puntos temporales | T0…T5 (ver `SNAPSHOTS_TEMPORALES.md`) |

Ningún dato del proyecto se inventó: todos provienen del historial de Git de ese repositorio, acotado
por fecha o por commit.

---

## 2. Cadena de trazabilidad (raw → processed → analysis → output)

### 2.1 Sprint 1

| Salida (output) | Se genera con (código/comando) | A partir de (entrada) | Trazable a |
|---|---|---|---|
| `D2_CIMPS8_OBSERVABILIDAD.csv` | Inspección manual + `git branch/log/tag/rev-list` + GitHub (issues/PR) | Los 8 repos del corpus CIMPS | Comandos en `README.md` §4.2 |
| `D3_ARTIFACT_IDENTITY.csv` | `git log --follow --name-status` (manual, 10 archivos) | commons-lang @ master | Commits citados en cada fila |
| `D3_SELECCION_30.txt` | `scripts/build_evolution_dataset.sh` (ranking por commits < T) | commons-lang @ snapshot | Script + commit + decision_time |
| `D3_EVOLUTION_DATASET.csv` | `scripts/build_evolution_dataset.sh` | Los 30 archivos de la selección | Script + `--before=2025-11-12` |
| `D3_Analisis_Evolucion.docx` | Análisis estadístico del dataset | `D3_EVOLUTION_DATASET.csv` | El propio CSV (re-derivable) |
| `D4_REFACTORING_EVENTS_RAW.json` | RefactoringMiner `-bc` (rango T4→T5) | commons-lang @ 3.19.0→3.20.0 | Comando + commits inicio/fin |
| `D4_REFACTORING_EVENTS_RAW.csv` | Conversión del JSON a CSV | `D4_REFACTORING_EVENTS_RAW.json` | El JSON crudo |
| `D4_REFACTORING_AUDIT_30.csv` | Muestra estratificada + clasificación manual | `D4_REFACTORING_EVENTS_RAW.json` | JSON + criterio de auditoría |
| `D4_Analisis_Refactorings.docx` | Análisis + inspección de 3 commits | RAW + auditoría | CSVs + `git show` de los commits |
| `D4_TEMPORAL_LEAKAGE.md` | Síntesis metodológica | Hallazgos de D3 y D4 | Documentos D3/D4 |
| `SNAPSHOTS_TEMPORALES.md` | `git rev-list` / `git log` sobre tags | Tags `rel/commons-lang-*` | Tags inmutables (verificado) |
| `D_Separacion_Temporal.docx` | Diseño (walk-forward) | Snapshots + leakage ledger | Puntos T0…T5 |

### 2.2 Sprint 2

| Salida (output) | Se genera con (código/comando) | A partir de (entrada) | Trazable a |
|---|---|---|---|
| `D3_AUDITORIA_RESULTADO.csv` | `scripts/audit_dataset.sh repos/commons-lang 2025-11-12` | `D3_EVOLUTION_DATASET.csv` + commons-lang | Script + `--before`/`--after=2025-11-12` + `--follow` |
| `D_Auditoria_Dataset.docx` | Redacción sobre los resultados de auditoría | `D3_AUDITORIA_RESULTADO.csv` | El CSV (12 registros verificados) |
| `D3_SNAPSHOTS_TEMPORALES_OBS.csv` | `scripts/snapshots_temporales.sh` | commons-lang @ cortes 3.18.0/3.19.0/3.20.0 | Script + fechas de release + `--follow` |
| `D_Snapshots_Temporales.docx` | Redacción sobre las observaciones | `D3_SNAPSHOTS_TEMPORALES_OBS.csv` | El CSV (3 snapshots, 5 campos) |
| `D3_FOLD_TRAIN.csv` / `D3_FOLD_TEST.csv` | `scripts/temporal_split.sh` | `D3_EVOLUTION_DATASET.csv` (rutas) + commons-lang | Script + cortes 3.18.0/3.19.0 + verificación por tag |
| `D_Separacion_Temporal_Materializada.docx` | Redacción sobre los folds | `D3_FOLD_TRAIN.csv` / `D3_FOLD_TEST.csv` | Los CSV + verificación de invariante |

Nota de identidad: la llave de integración del proyecto es `project + artifact_id + decision_time`. Los
artefactos se anclan a su `path` como identificador canónico de los 30 archivos del dataset.

---

## 3. Integridad — cómo se garantiza que nada cambió

1. **Anclaje por commit y fecha.** Cada dato deriva de un commit exacto (SHA-1) o de un filtro
   temporal (`--before=decision_time`). Los SHA-1 son inmutables: identifican contenido, no posición.
2. **Snapshot congelado.** El análisis se ancla al commit `598dfc163b8b` (3.20.0). Aunque el
   repositorio siga avanzando, ese punto de referencia no cambia.
3. **Regla temporal verificable.** Toda métrica del dataset cumple `feature_timestamp <= 2025-11-12`;
   verificada en 3 casos en Sprint 1 y ampliada a **12 registros auditados** en Sprint 2
   (`D3_AUDITORIA_RESULTADO.csv`).
4. **Doble control de existencia temporal.** Además de la invariante por fecha, el Sprint 2 incorpora
   la verificación de existencia por tag (`git cat-file -e rel/...:<path>`), que acota la
   sobre-atribución de identidad de `--follow` en archivos de creación reciente (caso F020).
5. **Scripts conservados.** La extracción está en `scripts/` (4 scripts), versionada en el
   repositorio, con su comando de ejecución documentado.
6. **Control de versiones.** Todo el avance está en el repositorio
   `github.com/WilliamSosa895/Longitudinal-technical-debt`. Estado del Sprint 1: tag
   `sprint1-g1a-v2` → commit `064687a`; último commit del Sprint 1 `991ea46` (2026-09-27). Las
   evidencias del Sprint 2 se incorporarán en un commit y tag propios al cierre del sprint.

---

## 4. Cómo reconstruir cualquier resultado desde cero

Un tercero puede reconstruir los resultados sin instrucciones verbales:

1. Clonar `apache/commons-lang` y situar el snapshot en `598dfc163b8b`.
2. Ejecutar `scripts/build_evolution_dataset.sh repos/commons-lang 2025-11-12 598dfc163b8b`
   → reproduce `D3_EVOLUTION_DATASET.csv`.
3. Ejecutar RefactoringMiner `-bc` entre `3d1eb7718…` y `598dfc163b…`
   → reproduce `D4_REFACTORING_EVENTS_RAW.json`.
4. Ejecutar `scripts/audit_dataset.sh repos/commons-lang 2025-11-12`
   → reproduce `D3_AUDITORIA_RESULTADO.csv`.
5. Ejecutar `scripts/snapshots_temporales.sh`
   → reproduce `D3_SNAPSHOTS_TEMPORALES_OBS.csv`.
6. Ejecutar `scripts/temporal_split.sh`
   → reproduce `D3_FOLD_TRAIN.csv` y `D3_FOLD_TEST.csv`.
7. Verificar los snapshots con el comando de `SNAPSHOTS_TEMPORALES.md` §5.

Las entradas (repo + commits), el código (`scripts/`) y las salidas (CSVs/JSON) están identificados,
de modo que la cadena completa es auditable.
