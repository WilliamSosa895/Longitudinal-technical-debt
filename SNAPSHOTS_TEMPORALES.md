# Snapshots temporales (T0 … Tn) — Manifiesto

**Sprint 1 · Gate G1A punto 7 · Proyecto piloto: commons-lang**
**Repositorio:** apache/commons-lang (rama `master`)

> Un único snapshot no permite afirmar evolución, acumulación, persistencia ni predicción de deuda
> técnica. Por eso el estudio longitudinal requiere **múltiples puntos temporales** con fecha y commit
> exactos. Este documento los define y explica la regla usada para seleccionarlos.

---

## 1. Regla de selección de los puntos temporales

Los puntos temporales se toman de las **releases oficiales** del proyecto (tags `rel/commons-lang-*`),
por cuatro razones:

1. **Exactitud e inmutabilidad:** cada release es un tag de Git con un commit y una fecha exactos que
   no cambian; cualquiera puede reconstruir el estado del código en ese punto.
2. **Estados estables:** una release marca un estado publicado y coherente del código (no un commit
   intermedio a mitad de un cambio).
3. **Reproducibilidad:** el punto temporal se identifica por su tag y su hash, no por una fecha
   arbitraria elegida por el investigador.
4. **Continuidad con CIMPS:** el último punto (`3.20.0`) coincide exactamente con el snapshot que
   analizó el estudio CIMPS, garantizando que la serie longitudinal se ancla al trabajo base.

**Rango elegido:** las seis releases más recientes de la línea 3.x, desde `3.15.0` hasta el snapshot
CIMPS `3.20.0`.

---

## 2. Manifiesto de snapshots

| ID | Release | Fecha | Commit (SHA-1 completo) | Días desde el anterior |
|----|---------|-------|--------------------------|------------------------|
| T0 | 3.15.0 | 2024-07-13 | `535ec32c680a6581739a41bf97ecb8b8718c73b8` | — |
| T1 | 3.16.0 | 2024-08-01 | `6a2a10d88885343cfe37c1d9fa42ac5edda7cab5` | 19 |
| T2 | 3.17.0 | 2024-08-24 | `29ccc7665f3bc5d84155a3092ab2209a053324e6` | 23 |
| T3 | 3.18.0 | 2025-07-06 | `5b59487808d0b86a94ad7a1ebd4c200e09b7be09` | 316 |
| T4 | 3.19.0 | 2025-09-19 | `3d1eb7718a79d18cc2ab57e7ab3b894426ec7c2f` | 75 |
| T5 | 3.20.0 | 2025-11-12 | `598dfc163b8b410fb3bb8794521206ec8dcec82a` | 54 |

`T5` (3.20.0) es el **decision_time** usado en D3 y el **snapshot CIMPS**.

---

## 3. Nota: los intervalos NO son uniformes

Los puntos temporales están separados por intervalos muy distintos: entre `T2` (3.17.0) y `T3`
(3.18.0) transcurrieron **316 días**, frente a las tres semanas que separan los primeros. Esto tiene
una implicación para el diseño del estudio:

- **No debe asumirse que los puntos están equiespaciados.** Si un análisis longitudinal comparara
  "cambios entre releases" sin considerar el tiempo transcurrido, mezclaría un intervalo de 3 semanas
  con uno de casi un año.
- Cuando el intervalo importe (por ejemplo, para tasas de cambio), conviene **normalizar por el
  tiempo transcurrido** o usar la fecha real, no solo el número de release.

Este es un hallazgo de observabilidad, análogo a los eventos globales detectados en D3/D4: el
calendario real del proyecto condiciona cómo deben interpretarse las métricas.

---

## 4. Relación con el resto del sprint

- Estos puntos son los **cortes temporales** del diseño de separación temporal (punto 11): los folds
  de entrenamiento y prueba se construyen sobre ellos.
- El **dataset de evolución** (D3) se calculó en `T5`; el mismo procedimiento (con `--before=T`)
  puede repetirse en `T0…T4` para construir la serie longitudinal completa en un sprint posterior.
- Todos los eventos analizados con RefactoringMiner (D4) caen dentro del intervalo `T4 → T5`.

---

## 5. Verificación (reproducibilidad)

Para confirmar que cada punto temporal corresponde al commit indicado, ejecutar en el repositorio:

```bash
cd repos/commons-lang
for v in 3.15.0 3.16.0 3.17.0 3.18.0 3.19.0 3.20.0; do
  tag="rel/commons-lang-$v"
  echo "$v | $(git log -1 --format=%ad --date=short $tag) | $(git rev-list -1 $tag)"
done
```

La salida debe coincidir, línea por línea, con la tabla de la sección 2.
