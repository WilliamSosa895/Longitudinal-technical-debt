# Bitácora de errores y decisiones — Sprint 1

**Proyecto:** Gestión de la Deuda Técnica (continuidad post-CIMPS)
**Estudiante:** William Tehuatle Sosa
**Documento vivo:** se actualiza conforme avanza el proyecto.

> Formato de cada entrada: **fecha → problema/decisión → causa/justificación → acción → evidencia → estado**.
> Los errores documentados también son evidencia del proceso de investigación.

---

## 1. Errores y problemas técnicos

| # | Fecha | Problema | Causa | Acción / corrección | Evidencia | Estado |
|---|---|---|---|---|---|---|
| E1 | 2026-09-16 | Los comandos `wc` y `head` no se reconocían en la terminal | Son utilidades Unix; PowerShell no las incluye | Migrar el trabajo a **Git Bash** (donde todos los comandos del sprint funcionan) | Mensaje "wc no se reconoce" en PowerShell | Resuelto |
| E2 | 2026-09-16 | Al abrir el CSV en Excel, todo el contenido quedó amontonado en la columna A | Excel en configuración regional en español interpreta `;` como separador de lista, no `,` | Trabajar en una plantilla `.xlsx` y exportar a **CSV UTF-8** al final | Captura del CSV sin separar | Resuelto |
| E3 | 2026-09-17 | `ls src/main/java` falla en 4 proyectos (commons-math, httpcomponents-client, maven, pdfbox) | Son proyectos **multi-módulo**; el código no está en la raíz | Usar `find . -type d -path "*/src/main/java"` para localizar los módulos | Salida de `find` en D2 | Resuelto (y documentado como hallazgo de observabilidad) |
| E4 | 2026-09-21 | En D2, `first_commit_date` de commons-lang aparecía como 2022 | Error de tecleo al llenar el CSV manualmente (2022 en vez de 2002) | Corregido a **2002-07-19**, verificado contra `git log` y contra D3 | `D2_CIMPS8_OBSERVABILIDAD.csv` corregido | Resuelto |
| E5 | 2026-09-21 | El `README.md` reflejaba solo la POC (días 1–2), quedó desactualizado | Se redactó al inicio y no se actualizó tras completar D3 y D4 | Regenerado con el estado real + versiones reales (Git 2.52.0, Java 17.0.17) | `README.md` (versión actualizada) | Resuelto |
| E6 | 2026-09-2X | *(reservado para lo que hayas resuelto por tu cuenta, p.ej. algún tropiezo al compilar RefactoringMiner)* | — | — | — | — |

---

## 2. Decisiones metodológicas

| # | Fecha | Decisión | Justificación | Evidencia | Estado |
|---|---|---|---|---|---|
| D1 | 2026-09-17 | Proyecto piloto: **commons-lang** | Cumple los 4 criterios: mono-módulo con `src/main/java` limpio, historial largo (10,278 commits), actividad reciente, tamaño manejable | `README.md` §5 | Vigente |
| D2 | 2026-09-21 | `decision_time` = **2025-11-12** | Es la fecha del snapshot que analizó CIMPS (release 3.20.0, commit `598dfc163b8b`); asegura coherencia con el estudio original | `README.md` §2 | Vigente |
| D3 | 2026-09-21 | Muestra **estratificada** de 30 archivos (10 hotspots + 10 medios + 10 tranquilos) | Necesidad de contraste para la Ruta B; una muestra solo de hotspots no permitiría comparar | `scripts/build_evolution_dataset.sh` | Vigente |
| D4 | 2026-09-2X | Rango de RefactoringMiner: **3.19.0 → 3.20.0** (119 commits) | Es el ciclo que termina exactamente en el snapshot CIMPS; manejable y respeta la regla temporal | `D4_Analisis_Refactorings.docx` | Vigente |
| D5 | 2026-09-2X | Auditoría **estratificada por tipo** (30 refactorings, cubriendo los 12 tipos) | Evitar que "Extract And Move Method" (54 % del total) domine la muestra y reste variedad | `D4_REFACTORING_AUDIT_30.csv` | Vigente |
| D6 | 2026-09-2X | Repositorio **privado** en GitHub | Confidencialidad del artículo CIMPS, que sigue en proceso de publicación | `github.com/WilliamSosa895/Longitudinal-technical-debt` | Vigente |

---

## 3. Hallazgos que condicionaron decisiones

Estos no son errores, sino descubrimientos del proceso que deberán tenerse en cuenta en etapas
posteriores (registrados aquí para no perderlos):

| # | Fecha | Hallazgo | Consecuencia para el estudio |
|---|---|---|---|
| H1 | 2026-09-17 | El corpus no es homogéneo: el contexto vive en GitHub Issues, en JIRA, o en ambos, según el proyecto | La recolección de contexto (Ruta B) deberá adaptarse por proyecto |
| H2 | 2026-09-2X | Las migraciones de paquete (`lang → lang3`) son **eventos globales del proyecto**, no actividad de cada archivo | Un pipeline no debe interpretar esos renames como cambios individuales |
| H3 | 2026-09-2X | El commit `a82f4cb50` (cambio de licencia) tocó 511 archivos y contamina `days_since_last_change` | Hay que filtrar commits masivos/triviales antes de calcular métricas de recencia |
| H4 | 2026-09-2X | El commit `c9ff6aa44` concentra 54 de 93 refactorings, pero es un fix funcional (no pago de deuda) | El conteo de refactorings requiere contexto; refactoring ≠ pago de deuda técnica |

---

## 4. Nota

Este documento se seguirá actualizando en los próximos sprints. Las fechas marcadas como `2026-09-2X`
deben ajustarse a la fecha real en que ocurrió cada evento (verificar contra el historial de commits
del repositorio del proyecto).
