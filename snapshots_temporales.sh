#!/usr/bin/env bash
# =============================================================================
# Sprint 2 — Definicion de snapshots temporales (observacion archivo x tiempo)
# =============================================================================
# Para UN mismo archivo, calcula en 3 decision_time distintos los 5 campos que
# exige el profesor:
#     proyecto + artifact_id + decision_time
#     + informacion DISPONIBLE hasta ese momento  (history <= decision_time)
#     + informacion RESERVADA como futuro         (history  > decision_time)
#
# Demuestra que al mover el corte hacia adelante, lo DISPONIBLE crece y lo
# RESERVADO (futuro) encoge. Regla temporal: --before=DT (disponible) /
# --after=DT (reservado). Identidad: --follow.
#
# Uso (desde la carpeta que contiene repos/commons-lang):
#   bash snapshots_temporales.sh
# =============================================================================
set -e
cd repos/commons-lang

PROY="commons-lang"
AID="F001"
F="src/main/java/org/apache/commons/lang3/StringUtils.java"

# Los 3 decision_time (releases 3.18.0, 3.19.0, 3.20.0)
DTS="2025-07-06 2025-09-19 2025-11-12"

OUT="../../D3_SNAPSHOTS_TEMPORALES_OBS.csv"
echo "proyecto,artifact_id,path,decision_time,disp_prior_commits,disp_churn,disp_contributors,disp_last_commit,fut_commits_reservados,fut_churn_reservado" > "$OUT"

printf "%-12s %-6s %-9s | DISPONIBLE: %-8s %-8s %-6s | FUTURO reservado: %-8s %-8s\n" \
  "decision_t" "id" "" "prior" "churn" "contr" "commits" "churn"
echo "-------------------------------------------------------------------------------------------"

for DT in $DTS; do
  # ---- INFORMACION DISPONIBLE (<= decision_time) ----
  PC=$(git log --oneline --before="$DT" --follow -- "$F" | wc -l)
  read LA LD < <(git log --before="$DT" --follow --numstat --format="" -- "$F" \
                 | awk '{a+=$1; d+=$2} END {print a+0, d+0}')
  CH=$((LA + LD))
  DC=$(git log --before="$DT" --follow --format="%an" -- "$F" | sort -u | wc -l)
  LAST=$(git log -1 --before="$DT" --follow --format="%h %ad" --date=short -- "$F")

  # ---- INFORMACION RESERVADA COMO FUTURO (> decision_time) ----
  FPC=$(git log --oneline --after="$DT" --follow -- "$F" | wc -l)
  read FLA FLD < <(git log --after="$DT" --follow --numstat --format="" -- "$F" \
                   | awk '{a+=$1; d+=$2} END {print a+0, d+0}')
  FCH=$((FLA + FLD))

  echo "$PROY,$AID,$F,$DT,$PC,$CH,$DC,\"$LAST\",$FPC,$FCH" >> "$OUT"
  printf "%-12s %-6s %-9s | %-8s %-8s %-6s | %-8s %-8s\n" \
    "$DT" "$AID" "" "$PC" "$CH" "$DC" "$FPC" "$FCH"
done

echo ""
echo "Listo: D3_SNAPSHOTS_TEMPORALES_OBS.csv (en la carpeta WILLIAM_SPRINT_01)"
