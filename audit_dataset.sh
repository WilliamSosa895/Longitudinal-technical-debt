#!/usr/bin/env bash
# =============================================================================
# Sprint 2 — Auditoría de registros del dataset evolutivo contra Git
# =============================================================================
# Qué hace:
#   Recalcula, DIRECTAMENTE contra el historial de Git y usando EXACTAMENTE
#   la misma regla temporal del dataset (--before=2025-11-12 --follow),
#   las 6 comprobaciones que exige el profesor para cada archivo:
#       1. identidad (commit de origen + cadena de renames)
#       2. commit y fecha (origen y último antes del decision_time)
#       3. prior_commits (numero de cambios previos)
#       4. churn (lines_added + lines_deleted)
#       5. distinct_contributors (colaboradores)
#       6. ausencia de informacion posterior (cuenta de commits DESPUES del DT
#          que quedan correctamente EXCLUIDOS)
#
#   Imprime una fila por archivo lista para comparar contra D3_EVOLUTION_DATASET.csv
#   y escribe D3_AUDITORIA_RESULTADO.csv
#
# Uso (desde la carpeta que contiene repos/commons-lang):
#   bash audit_dataset.sh repos/commons-lang 2025-11-12
# =============================================================================
set -e

REPO="${1:-repos/commons-lang}"
DT="${2:-2025-11-12}"
cd "$REPO"

# Los 12 archivos auditados (ruta tal como existen en el snapshot 3.20.0)
FILES="
F001 src/main/java/org/apache/commons/lang3/StringUtils.java
F002 src/main/java/org/apache/commons/lang3/ArrayUtils.java
F003 src/main/java/org/apache/commons/lang3/ClassUtils.java
F007 src/main/java/org/apache/commons/lang3/SystemUtils.java
F011 src/main/java/org/apache/commons/lang3/time/TimeZones.java
F012 src/main/java/org/apache/commons/lang3/text/translate/EntityArrays.java
F013 src/main/java/org/apache/commons/lang3/Streams.java
F018 src/main/java/org/apache/commons/lang3/function/IntToCharFunction.java
F021 src/main/java/org/apache/commons/lang3/concurrent/UncheckedFutureImpl.java
F027 src/main/java/org/apache/commons/lang3/Charsets.java
F029 src/main/java/org/apache/commons/lang3/AppendableJoiner.java
F030 src/main/java/org/apache/commons/lang3/util/IterableStringTokenizer.java
"

OUT="D3_AUDITORIA_RESULTADO.csv"
echo "artifact_id,path,prior_commits,lines_added,lines_deleted,churn,distinct_contributors,last_before_dt,days_since_last_change,origin_commit,origin_date,commits_after_dt_excluidos" > "$OUT"

printf "%-6s %-9s %-7s %-7s %-7s %-5s %-11s %-6s %-11s %-5s\n" \
  "ID" "prior" "LA" "LD" "churn" "contr" "last_before" "days" "origin" "futuro"

echo "$FILES" | while read ID F; do
  [ -z "$ID" ] && continue

  # 3. prior_commits: commits ANTES del decision_time, siguiendo identidad
  PC=$(git log --oneline --before="$DT" --follow -- "$F" | wc -l)

  # 4. churn: suma de lineas +/- en esos mismos commits
  read LA LD < <(git log --before="$DT" --follow --numstat --format="" -- "$F" \
                 | awk '{a+=$1; d+=$2} END {print a+0, d+0}')
  CH=$((LA + LD))

  # 5. distinct_contributors
  DC=$(git log --before="$DT" --follow --format="%an" -- "$F" | sort -u | wc -l)

  # 2. ultimo commit ANTES del DT + fecha -> days_since_last_change
  LAST=$(git log -1 --before="$DT" --follow --format="%ad" --date=short -- "$F")
  DAYS=$(( ( $(date -d "$DT" +%s) - $(date -d "$LAST" +%s) ) / 86400 ))

  # 1. commit de ORIGEN (el mas antiguo siguiendo la identidad) + fecha
  ORIG=$(git log --before="$DT" --follow --format="%h|%ad" --date=short -- "$F" | tail -1)
  OH=${ORIG%%|*}; OD=${ORIG##*|}

  # 6. ausencia de informacion posterior: commits DESPUES del DT (deben existir
  #    para hotspots y quedar EXCLUIDOS del dataset). Si da 0, el archivo
  #    simplemente no cambio despues del DT (valido tambien).
  FUT=$(git log --oneline --after="$DT" --follow -- "$F" | wc -l)

  echo "$ID,$F,$PC,$LA,$LD,$CH,$DC,$LAST,$DAYS,$OH,$OD,$FUT" >> "$OUT"
  printf "%-6s %-9s %-7s %-7s %-7s %-5s %-11s %-6s %-11s %-5s\n" \
    "$ID" "$PC" "$LA" "$LD" "$CH" "$DC" "$LAST" "$DAYS" "$OH ($OD)" "$FUT"
done

echo ""
echo "Listo: $REPO/$OUT"
