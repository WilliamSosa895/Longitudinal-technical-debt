# D4 — Registro de fugas de información temporal (Temporal Leakage Ledger)

**Sprint 1 · Proyecto piloto: commons-lang**
**decision_time (t):** 2025-11-12 (snapshot CIMPS, release 3.20.0, commit `598dfc163b8b`)

---

## 1. Qué es una fuga de información temporal

Una **fuga temporal** (*temporal leakage*) ocurre cuando, para describir o decidir algo en un
momento `t`, se utiliza —por error— información que en ese momento **todavía no existía** porque
pertenece al futuro. En un estudio longitudinal de deuda técnica esto es especialmente peligroso:
si una variable "ve" el futuro, el modelo o el análisis obtendrá resultados **engañosamente buenos**
que no se sostendrían en una situación real, donde el futuro es desconocido.

**Regla general que evita la fuga:**

```
feature_timestamp <= decision_time
```

Ninguna variable usada para caracterizar un artefacto en `t` puede provenir de un commit, issue,
pull request o medición cuya fecha sea posterior a `t`.

Una distinción clave: la información del futuro **no está prohibida en sí misma** — es válida (y
necesaria) como **etiqueta** (aquello que se quiere predecir). Lo que nunca debe hacerse es usarla
como **feature** (variable de entrada). Confundir etiqueta con feature es la forma más común de fuga.

---

## 2. Variables SEGURAS (existen en `t`, no son fuga)

Estas variables son válidas como features porque toda su información es anterior o igual a `t`. Se
listan para contraste, y son las que efectivamente se usaron en el dataset de evolución (D3).

| Variable / información | ¿Existe en t? | ¿Es del futuro? | Riesgo | Regla preventiva |
|---|---|---|---|---|
| Métricas estáticas medidas sobre el estado del código en `t` (p.ej. SonarQube en el snapshot 3.20.0) | Sí | No | Bajo | Medir sobre el commit del snapshot, no sobre versiones posteriores |
| `prior_commits` (nº de commits del archivo antes de `t`) | Sí | No | Bajo | `git log --before=t` |
| `churn` previo (líneas +/− acumuladas hasta `t`) | Sí | No | Bajo | `git log --before=t --numstat` |
| `distinct_contributors` previos (hasta `t`) | Sí | No | Bajo | `git log --before=t --format=%an` |
| `days_since_last_change` (respecto al último commit anterior a `t`) | Sí | No | Bajo* | Calcular con el último commit con fecha `< t` |

\* Ver la nota sobre contaminación por eventos globales en la sección 4.

---

## 3. Situaciones de FUGA (información del futuro — NO usar como feature)

Se identifican **seis** situaciones en las que un experimento futuro podría, por error, usar
información posterior a `t`.

| # | Variable / información | ¿Existe en t? | ¿Es del futuro? | Riesgo | Regla preventiva |
|---|---|---|---|---|---|
| L1 | **Cambios futuros del archivo** (nº de commits posteriores a `t`) | No | Sí | Alto | Solo contar commits con fecha `< t`; los cambios posteriores son etiqueta, no feature |
| L2 | **Churn futuro** (líneas añadidas/eliminadas después de `t`) | No | Sí | Alto | Acumular churn solo hasta `t` (`--before=t`) |
| L3 | **Refactorings futuros** (detectados en commits posteriores a `t`) | No | Sí | Alto | Ejecutar RefactoringMiner solo hasta el commit de `t`; los refactorings del ciclo objetivo son la etiqueta |
| L4 | **Colaboradores futuros** (personas que tocarán el archivo después de `t`) | No | Sí | Alto | Contar autores solo en commits `< t` |
| L5 | **Issues / Pull Requests con fecha posterior a `t`** (contexto de un issue abierto o cerrado después de `t`) | No | Sí | Alto | Filtrar issues/PR por fecha de creación/cierre `< t` antes de usarlos como contexto |
| L6 | **Métricas estáticas calculadas sobre una versión posterior a `t`** (p.ej. medir SonarQube sobre el estado en 3.21.0 y asignarlo al archivo "en `t`") | No | Sí | Alto | Medir siempre sobre el commit exacto del snapshot `t`, nunca sobre un estado más reciente |

---

## 4. Riesgo relacionado: contaminación por eventos globales

Además de la fuga temporal estricta (usar el futuro), el sprint detectó un riesgo **distinto pero
emparentado**: un **evento global del proyecto**, aunque sea anterior a `t` (y por tanto no sea fuga
temporal), puede contaminar una métrica.

**Caso real detectado:** el commit `a82f4cb50` ("Update Apache License URL to HTTPS", 2025-05-20)
tocó **511 archivos** solo para cambiar la URL de la licencia. Como es anterior a `t`, no es fuga
temporal; pero hace que la métrica `days_since_last_change` de muchos archivos tranquilos marque
"cambio reciente" cuando en realidad no hubo actividad real.

**Regla preventiva:** identificar y filtrar commits masivos/triviales (por ejemplo, commits que
tocan un número anómalo de archivos con cambios cosméticos) antes de calcular métricas de recencia.
Este mismo fenómeno se observó con las migraciones de paquete (`lang → lang3`) en el análisis de
identidad (D3): eventos globales que se disfrazan de actividad individual.

---

## 5. Ejemplo concreto de fuga que produce un resultado engañosamente bueno

**Escenario:** se quiere predecir, en `t` = 2025-11-12, qué archivos serán refactorizados durante el
ciclo de la release 3.20.0.

**La fuga:** se usa como feature el "número de refactorings del archivo" obtenido ejecutando
RefactoringMiner sobre **todo el historial**, incluyendo el propio ciclo 3.20.0 (posterior a `t`).

**Por qué engaña:** la feature contiene, literalmente, la respuesta. Un archivo refactorizado en el
ciclo 3.20.0 tendrá un conteo alto *precisamente por esos refactorings que se quieren predecir*. El
modelo alcanzaría una exactitud altísima, pero **falsa**: en un uso real, en `t` nadie conoce los
refactorings que aún no han ocurrido.

**La mitigación:** ejecutar RefactoringMiner **solo hasta el commit de `t`** (como se hizo en D4, con
el rango que termina exactamente en el snapshot 3.20.0). Los refactorings del ciclo objetivo se
reservan como **etiqueta** (lo que se predice), nunca como feature.

---

## 6. Conclusión

El dataset de evolución construido en D3 respeta la regla `feature_timestamp <= decision_time`, y las
seis situaciones de fuga (L1–L6) quedan identificadas con su regla preventiva. Junto con el riesgo de
contaminación por eventos globales (sección 4), este registro define las condiciones mínimas que
cualquier experimento posterior deberá cumplir **antes** de entrenar un modelo. Mientras este control
permanezca abierto o incompleto, no se autoriza el entrenamiento (criterio del Gate G1A, punto 10).
