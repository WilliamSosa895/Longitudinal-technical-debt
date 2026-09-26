# Provenance e integridad — Trazabilidad de los resultados

**Sprint 1 · Gate G1A punto 13 · Proyecto piloto: commons-lang**

> Objetivo: que cualquier resultado del sprint pueda rastrearse hasta sus entradas y hasta el código
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

Ningún dato del sprint se inventó: todos provienen del historial de Git de ese repositorio, acotado
por fecha o por commit.

---

## 2. Cadena de trazabilidad (raw → processed → analysis → output)

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

---

## 3. Integridad — cómo se garantiza que nada cambió

1. **Anclaje por commit y fecha.** Cada dato deriva de un commit exacto (SHA-1) o de un filtro
   temporal (`--before=decision_time`). Los SHA-1 son inmutables: identifican contenido, no posición.
2. **Snapshot congelado.** El análisis se ancla al commit `598dfc163b8b` (3.20.0). Aunque el
   repositorio siga avanzando, ese punto de referencia no cambia.
3. **Regla temporal verificable.** Toda métrica del dataset cumple `feature_timestamp <= 2025-11-12`;
   se verificó manualmente en 3 casos (ver `README.md` §6.3).
4. **Scripts conservados.** La extracción del dataset está en `scripts/`, versionada en el
   repositorio, con su comando de ejecución documentado.
5. **Control de versiones.** Todo el avance está en el repositorio privado
   `github.com/WilliamSosa895/Longitudinal-technical-debt`, con el tag `sprint1-g1a` que marca este
   estado exacto (commit `414b97c5…`).

---

## 4. Cómo reconstruir cualquier resultado desde cero

Un tercero puede reconstruir los resultados sin instrucciones verbales:

1. Clonar `apache/commons-lang` y situar el snapshot en `598dfc163b8b`.
2. Ejecutar `scripts/build_evolution_dataset.sh repos/commons-lang 2025-11-12 598dfc163b8b`
   → reproduce `D3_EVOLUTION_DATASET.csv`.
3. Ejecutar RefactoringMiner `-bc` entre `3d1eb7718…` y `598dfc163b…`
   → reproduce `D4_REFACTORING_EVENTS_RAW.json`.
4. Verificar los snapshots con el comando de `SNAPSHOTS_TEMPORALES.md` §5.

Las entradas (repo + commits), el código (`scripts/`) y las salidas (CSVs/JSON) están identificados,
de modo que la cadena completa es auditable.
