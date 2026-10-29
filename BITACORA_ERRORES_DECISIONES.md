# Bitácora de errores y decisiones — Sprint 1 y Sprint 2

**Proyecto:** Gestión de la Deuda Técnica (continuidad post-CIMPS)
**Estudiante:** William Tehuatle Sosa
**Documento vivo:** se actualiza conforme avanza el proyecto.

> Formato de cada entrada: **fecha → problema/decisión → causa/justificación → acción → evidencia → estado**.
> Los errores documentados también son evidencia del proceso de investigación.
> Las fechas de los eventos del Sprint 1 se verificaron contra el historial de commits del repositorio
> (`414b97c` 2026-09-25, `064687a` 2026-09-26, `991ea46` 2026-09-27).

---

## 1. Errores y problemas técnicos

| # | Fecha | Problema | Causa | Acción / corrección | Evidencia | Estado |
|---|---|---|---|---|---|---|
| E1 | 2026-09-16 | Los comandos `wc` y `head` no se reconocían en la terminal | Son utilidades Unix; PowerShell no las incluye | Migrar el trabajo a **Git Bash** (donde todos los comandos del sprint funcionan) | Mensaje "wc no se reconoce" en PowerShell | Resuelto |
| E2 | 2026-09-16 | Al abrir el CSV en Excel, todo el contenido quedó amontonado en la columna A | Excel en configuración regional en español interpreta `;` como separador de lista, no `,` | Trabajar en una plantilla `.xlsx` y exportar a **CSV UTF-8** al final | Captura del CSV sin separar | Resuelto |
| E3 | 2026-09-17 | `ls src/main/java` falla en 4 proyectos (commons-math, httpcomponents, maven, pdfbox) | Son proyectos **multi-módulo**; el código no está en la raíz | Usar `find . -type d -path "*/src/main/java"` para localizar los módulos | Salida de `find` en D2 | Resuelto (y documentado como hallazgo de observabilidad) |
| E4 | 2026-09-21 | En D2, `first_commit_date` de commons-lang aparecía como 2022 | Error de tecleo al llenar el CSV manualmente (2022 en vez de 2002) | Corregido a **2002-07-19**, verificado contra `git log` y contra D3 | `D2_CIMPS8_OBSERVABILIDAD.csv` corregido | Resuelto |
| E5 | 2026-09-26 | El `README.md` reflejaba solo la POC (días 1–2), quedó desactualizado | Se redactó al inicio y no se actualizó tras completar D3 y D4 | Regenerado con el estado real + versiones reales (Git 2.52.0, Java 17.0.17) | `README.md` (versión actualizada) | Resuelto |
| E6 | 2026-10-14 | En la auditoría, un comando dio falso "NO EXISTE" para F020 en 3.19.0 | Typo `ccd` al inicio: el `cd` falló y el comando corrió en el repo equivocado (no en commons-lang) | Re-ejecutado usando `git -C repos/commons-lang ...`, que no depende del directorio actual | Salidas comparadas de ambas corridas | Resuelto |
| E7 | 2026-10-28 | Al correr el E1, `bash` abrió WSL (roto) y luego `python` abrió el stub de la Microsoft Store | Se ejecutó en PowerShell (no Git Bash) y el alias de ejecución de Windows tapaba el Python real | Correr en **Git Bash** y usar el lanzador **`py`** (Python 3.8.10); el análisis quedó cacheado, así que al relanzar brincó a la exportación | Salida del script `run_e1_sonar_commons-lang.sh` | Resuelto |

---

## 2. Decisiones metodológicas

| # | Fecha | Decisión | Justificación | Evidencia | Estado |
|---|---|---|---|---|---|
| D1 | 2026-09-17 | Proyecto piloto: **commons-lang** | Cumple los 4 criterios: mono-módulo con `src/main/java` limpio, historial largo (10,278 commits), actividad reciente, tamaño manejable | `README.md` §5 | Vigente |
| D2 | 2026-09-25 | `decision_time` = **2025-11-12** | Es la fecha del snapshot que analizó CIMPS (release 3.20.0, commit `598dfc163b8b`); asegura coherencia con el estudio original | `README.md` §2 | Vigente |
| D3 | 2026-09-25 | Muestra **estratificada** de 30 archivos (10 hotspots + 10 medios + 10 tranquilos) | Necesidad de contraste para la Ruta B; una muestra solo de hotspots no permitiría comparar | `scripts/build_evolution_dataset.sh` | Vigente (ver H9: el estrato medio se vio afectado por el linaje de `--follow`) |
| D4 | 2026-09-26 | Rango de RefactoringMiner: **3.19.0 → 3.20.0** (117 commits) | Es el ciclo que termina exactamente en el snapshot CIMPS; manejable y respeta la regla temporal | `D4_Analisis_Refactorings.docx` | Vigente |
| D5 | 2026-09-26 | Auditoría **estratificada por tipo** (30 refactorings, cubriendo los 12 tipos) | Evitar que "Extract And Move Method" (54 % del total) domine la muestra y reste variedad | `D4_REFACTORING_AUDIT_30.csv` | Vigente |
| D6 | 2026-09-25 | Repositorio **privado** en GitHub | Confidencialidad del artículo CIMPS, que sigue en proceso de publicación | `github.com/WilliamSosa895/Longitudinal-technical-debt` | **Resuelto** (2026-10-28: el repositorio se puso en privado; ver H8) |
| D7 | 2026-10-14 | Anclar `artifact_id` al **path** como identificador canónico | La llave de integración `project + artifact_id + decision_time` requiere un id estable; los dos archivos D3 usaban numeraciones distintas (ver H6) | `D_Auditoria_Dataset.docx` §7 | Vigente |
| D8 | 2026-10-14 | Etiqueta de separación temporal = **evento de cambio** (≥1 commit en la ventana) | Proxy reproducible con un comando de Git; la refinación con RefactoringMiner se reserva, respetando "refactoring ≠ pago de deuda" | `D_Separacion_Temporal_Materializada.docx` §2 | Vigente |
| D9 | 2026-10-14 | Control reforzado por **tag** (`git cat-file -e`) además de la invariante por fecha | Detecta artefactos no presentes en el snapshot del corte que la invariante por fecha deja pasar (ver H7) | `D_Separacion_Temporal_Materializada.docx` §6 | Vigente |
| D10 | 2026-10-28 | Recalcular E2 con **`git log --follow -M90%`** y **documentar ambos valores** (original y corregido), sin sustituir en silencio ni eliminar archivos | El `--follow` por defecto (umbral de similitud 50 %) asigna historia de otros archivos (ver H9); subir el umbral a 90 % corta los saltos falsos **sin perder los renames legítimos** (StringUtils conserva 716 y ArrayUtils 314). Se conservan ambas versiones para hacer visible la diferencia | `E2_CORREGIDO_commons-lang.csv` | Vigente |
| D11 | 2026-10-28 | **Control de versiones:** rama `sprint2-e2` para el trabajo del Sprint 2; `main` intacta con el G1A etiquetado (`sprint1-g1a-v2`); **conventional commits** (`feat`, `fix`, `docs`, `chore`) | Aísla el trabajo en curso del estado calificado; el historial queda legible y auditable, como pide el sprint ("conservar código y registrar comandos, versiones, commits y fecha") | Historial de la rama `sprint2-e2` en GitHub | Vigente |
| D12 | 2026-10-28 | **Piloto oficial de la integración = commons-lang; E1 real con SonarQube** | Consensuado con Y. Roa y avalado por el profesor ("el piloto que mejor exprese la información"): commons-lang combina la E2 longitudinal validada (W. Tehuatle) con la E3 de co-change (Y. Roa), y su `decision_time` (2025-11-12 = release 3.20.0) coincide con el snapshot CIMPS. El E1 por archivo se generó con **SonarQube 26.6.0.123539** (misma versión que Y. Roa) sobre el snapshot 3.20.0, reemplazando el E1 provisional (solo LOC) | `INTEGRATED_E1_E2_E3_commons-lang_2025-11-12_mf50.csv` (30 archivos; `keys_e2=30`, `keys_e3=30`, `issues=[]`) + `E1_FILE_METRICS_commons-lang_2025-11-12.csv` | Vigente |

---

## 3. Hallazgos que condicionaron decisiones

Estos no son errores, sino descubrimientos del proceso que deberán tenerse en cuenta en etapas
posteriores (registrados aquí para no perderlos):

| # | Fecha | Hallazgo | Consecuencia para el estudio |
|---|---|---|---|
| H1 | 2026-09-17 | El corpus no es homogéneo: el contexto vive en GitHub Issues, en JIRA, o en ambos, según el proyecto | La recolección de contexto (Ruta B) deberá adaptarse por proyecto |
| H2 | 2026-09-25 | Las migraciones de paquete (`lang → lang3`) son **eventos globales del proyecto**, no actividad de cada archivo | Un pipeline no debe interpretar esos renames como cambios individuales |
| H3 | 2026-09-25 | El commit `a82f4cb50` (cambio de licencia) tocó 511 archivos y contamina `days_since_last_change` | Hay que filtrar commits masivos/triviales antes de calcular métricas de recencia |
| H4 | 2026-09-26 | El commit `c9ff6aa44` concentra 54 de 93 refactorings, pero es un fix funcional (no pago de deuda) | El conteo de refactorings requiere contexto; refactoring ≠ pago de deuda técnica |
| H5 | 2026-10-14 | F020 (ByteSupplier) no existe en el árbol de la release 3.18.0: es un **artefacto no nacido** en ese corte | Debe excluirse del fold de entrenamiento; una observación sin pasado no es válida |
| H6 | 2026-10-14 | El `artifact_id` difiere entre `D3_ARTIFACT_IDENTITY.csv` y `D3_EVOLUTION_DATASET.csv` (coinciden solo en F001/F002) | Anclar la llave de integración al `path` (decisión D7) para no romper el join E1+E2+E3 |
| H7 | 2026-10-14 | `git log --follow` rastreó a F020 (nacido en 2025) hasta el commit fundacional de **2002** por similitud de contenido | La verificación por tag (decisión D9) acota la sobre-atribución de identidad; cuantificado después en H9 |
| H8 | 2026-10-14 | El repositorio figuraba como **público** en GitHub, pese a la decisión D6 (repo privado por CIMPS) | **Resuelto (2026-10-28):** el repositorio se puso en privado |
| H9 | 2026-10-28 | **Cuantificación de la sobre-atribución de `git log --follow` — hallazgo compartido con Y. Roa Moreno (H-04 en su bitácora).** Al cruzar E2 con la evidencia de co-change (E3), la diferencia `prior_commits − (commits reales)` es ≠ 0 en **10 de 30 archivos**. Caso extremo: ByteSupplier (F020) reportaba 32 commits pero su historia real es **1** (`--follow` saltó al `LICENSE` y a archivos de prueba como `GenericParent`). El **estrato medio** quedó contaminado: varios archivos "medios" (≈32 commits) eran en realidad "tranquilos" | Se adopta `--follow -M90%` (D10), que corrige los 10 archivos y mantiene los renames legítimos; se conservan ambos valores en `E2_CORREGIDO_commons-lang.csv`. Afecta la selección estratificada (D3) y se declara como **limitación** del dataset. Verificado en vivo con `git log --follow -M90%` sobre commons-lang |
| H10 | 2026-10-28 | La integración E1+E2+E3 cerró **limpia** (`issues=[]`, `keys_e2=30`, `keys_e3=30`): las tres familias empatan por la llave `project + artifact_id + decision_time` sin huecos. E1 real (SonarQube) difiere de CIMPS en los conteos absolutos por la **versión de las reglas**, no por el alcance (totales por archivo consistentes con el instrumento) | La observación común E1+E2+E3 es construible y temporalmente válida; los resultados son **piloto/exploratorios**, no confirmatorios |

---

## 4. Nota

Este documento se seguirá actualizando en los próximos sprints. Las fechas del Sprint 1 corresponden a
los commits del repositorio; las del Sprint 2 corresponden a las sesiones de validación longitudinal:
`2026-10-14` (auditoría, snapshots y separación temporal), `2026-10-28` (corrección de linaje H-04,
control de versiones y **generación del E1 real con SonarQube + integración E1+E2+E3**).
