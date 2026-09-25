#!/usr/bin/env bash
# =============================================================================
# Sprint 1 — D3 Parte C: Construcción del primer dataset de evolución
# =============================================================================
# Qué hace:
#   1. Toma todos los archivos .java del snapshot CIMPS.
#   2. Los rankea por número de commits previos al decision_time.
#   3. Selecciona una muestra ESTRATIFICADA de 30 archivos:
#        - 10 hotspots (los más cambiados)   -> relevantes para la Ruta B
#        - 10 de actividad media
#        - 10 tranquilos (los menos cambiados)
#      Así el dataset tiene contraste, no solo archivos "movidos".
#   4. Calcula 6 métricas de evolución por archivo, usando EXCLUSIVAMENTE
#      información anterior al decision_time (regla: feature_timestamp <= decision_time).
#
# REGLA TEMPORAL: todos los git log llevan --before="$DT". Ningún dato
#   proviene de commits posteriores al momento analizado. Esto evita la
#   fuga de información temporal (temporal leakage).
#
# Uso:
#   bash build_evolution_dataset.sh <ruta_repo> <decision_time> <commit_snapshot>
# Ejemplo (commons-lang, snapshot CIMPS 3.20.0):
#   bash build_evolution_dataset.sh repos/commons-lang 2025-11-12 598dfc163b8b
#
# Salidas:
#   D3_EVOLUTION_DATASET.csv  -> el dataset (30 filas + encabezado)
#   D3_SELECCION_30.txt       -> lista de los 30 archivos seleccionados
#
# Nota metodológica: con --numstat, los commits de merge pueden sumar líneas
#   ya contadas. Para esta fase de factibilidad es aceptable; por eso el
#   sprint exige verificar manualmente 3 archivos contra el historial (abajo).
# =============================================================================
set -e

REPO="${1:-.}"
DT="${2:-2025-11-12}"      # decision_time = fecha del snapshot CIMPS (commons-lang 3.20.0)
SNAP="${3:-598dfc163b8b}"  # commit del snapshot CIMPS

cd "$REPO"
OUT="D3_EVOLUTION_DATASET.csv"
SEL="D3_SELECCION_30.txt"

echo "Rankeando archivos .java por actividad previa al decision_time ($DT)..."
TMP=$(mktemp)
for f in $(git ls-tree -r --name-only "$SNAP" -- src/main/java | grep '\.java$'); do
  n=$(git log --oneline --before="$DT" --follow -- "$f" 2>/dev/null | wc -l)
  echo "$n|$f"
done | sort -rn > "$TMP"

TOTAL=$(wc -l < "$TMP")
echo "Total de archivos .java en el snapshot: $TOTAL"

# Muestra estratificada: 10 top + 10 medios + 10 tranquilos
{ head -10 "$TMP"
  sed -n "$((TOTAL/2 - 4)),$((TOTAL/2 + 5))p" "$TMP"
  tail -10 "$TMP"
} | awk -F'|' '{print $2}' > "$SEL"

echo "Calculando métricas (solo información < $DT)..."
echo "artifact_id,decision_time,path,prior_commits,lines_added,lines_deleted,churn,days_since_last_change,distinct_contributors" > "$OUT"

i=1
while IFS= read -r F; do
  ID=$(printf "F%03d" "$i")
  PC=$(git log --oneline --before="$DT" --follow -- "$F" | wc -l)
  LA=$(git log --before="$DT" --follow --numstat --format="" -- "$F" | awk '{a+=$1} END {print a+0}')
  LD=$(git log --before="$DT" --follow --numstat --format="" -- "$F" | awk '{d+=$2} END {print d+0}')
  CH=$((LA + LD))
  LAST=$(git log -1 --before="$DT" --follow --format="%ad" --date=short -- "$F")
  DAYS=$(( ( $(date -d "$DT" +%s) - $(date -d "$LAST" +%s) ) / 86400 ))
  DC=$(git log --before="$DT" --follow --format="%an" -- "$F" | sort -u | wc -l)
  echo "$ID,$DT,$F,$PC,$LA,$LD,$CH,$DAYS,$DC" >> "$OUT"
  i=$((i+1))
done < "$SEL"

rm -f "$TMP"
echo "Listo: $OUT  ($(($(wc -l < "$OUT")-1)) archivos)"
