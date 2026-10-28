#!/usr/bin/env bash
# =============================================================================
# Sprint 2 — Materializacion de la separacion temporal (walk-forward)
# =============================================================================
# Convierte el DISENO del Sprint 1 (D_Separacion_Temporal) en datos reales.
# Para los 30 archivos del dataset construye dos folds que respetan el orden
# temporal (NO hay split aleatorio):
#
#   Fold ENTRENAMIENTO : features con --before=3.18.0 ; etiqueta en (3.18.0, 3.19.0]
#   Fold PRUEBA        : features con --before=3.19.0 ; etiqueta en (3.19.0, 3.20.0]
#
# Etiqueta (label_changed): 1 si el archivo tuvo >=1 commit en la ventana futura
#   (evento de cambio). Es un proxy reproducible; la refinacion con
#   RefactoringMiner queda documentada como trabajo posterior.
#
# Invariante verificada por fila:  max(feature_ts) <= T < min(label_ts)
#
# Uso (desde la carpeta WILLIAM_SPRINT_01, que contiene D3_EVOLUTION_DATASET.csv
#      y repos/commons-lang):
#   bash temporal_split.sh
# =============================================================================
set -e

BASE="$(pwd)"
DATASET="$BASE/D3_EVOLUTION_DATASET.csv"
REPO="$BASE/repos/commons-lang"

# Cortes (fecha) de las releases 3.18.0 / 3.19.0 / 3.20.0
T1="2025-07-06"   # 3.18.0  -> corte features fold entrenamiento
T2="2025-09-19"   # 3.19.0  -> corte features fold prueba / fin ventana train
T3="2025-11-12"   # 3.20.0  -> fin ventana prueba (decision_time D3)

secs() { date -d "$1" +%s; }

# Calcula una fila de fold para un archivo F, corte CUT, ventana (CUT, WEND]
fila() {
  local ID="$1" F="$2" CUT="$3" WEND="$4"
  cd "$REPO"
  local PC LA LD CH DC LAST DAYS WCOUNT LABEL MINLAB INV
  PC=$(git log --oneline --before="$CUT" --follow -- "$F" | wc -l)
  read LA LD < <(git log --before="$CUT" --follow --numstat --format="" -- "$F" \
                 | awk '{a+=$1; d+=$2} END {print a+0, d+0}')
  CH=$((LA + LD))
  DC=$(git log --before="$CUT" --follow --format="%an" -- "$F" | sort -u | wc -l)
  LAST=$(git log -1 --before="$CUT" --follow --format="%ad" --date=short -- "$F")
  DAYS=$(( ( $(secs "$CUT") - $(secs "$LAST") ) / 86400 ))
  # Etiqueta: commits en la ventana futura (CUT, WEND]
  WCOUNT=$(git log --oneline --after="$CUT" --before="$WEND" --follow -- "$F" | wc -l)
  if [ "$WCOUNT" -gt 0 ]; then
    LABEL=1
    MINLAB=$(git log --after="$CUT" --before="$WEND" --follow --format="%ad" --date=short -- "$F" | tail -1)
  else
    LABEL=0; MINLAB=""
  fi
  # Invariante: LAST <= CUT  y  (LABEL=0 o MINLAB > CUT)
  if [ "$(secs "$LAST")" -le "$(secs "$CUT")" ] && \
     { [ "$LABEL" -eq 0 ] || [ "$(secs "$MINLAB")" -gt "$(secs "$CUT")" ]; }; then
     INV="OK"; else INV="FALLA"; fi
  echo "$ID,$F,$CUT,$PC,$CH,$DC,$DAYS,$LABEL,$LAST,$MINLAB,$INV"
}

HDR="artifact_id,path,cut_date,prior_commits,churn,distinct_contributors,days_since_last_change,label_changed,max_feature_date,min_label_date,invariante"
echo "$HDR" > "$BASE/D3_FOLD_TRAIN.csv"
echo "$HDR" > "$BASE/D3_FOLD_TEST.csv"

echo "Construyendo folds para los 30 archivos..."
# Lee artifact_id (col1) y path (col3) del dataset, saltando el encabezado
tail -n +2 "$DATASET" | while IFS=',' read -r ID DT PATHF REST; do
  [ -z "$ID" ] && continue
  fila "$ID" "$PATHF" "$T1" "$T2" >> "$BASE/D3_FOLD_TRAIN.csv"
  fila "$ID" "$PATHF" "$T2" "$T3" >> "$BASE/D3_FOLD_TEST.csv"
done

cd "$BASE"
echo ""
echo "=== RESUMEN ==="
for FOLD in TRAIN TEST; do
  FILE="D3_FOLD_${FOLD}.csv"
  N=$(( $(wc -l < "$FILE") - 1 ))
  POS=$(tail -n +2 "$FILE" | awk -F',' '$8==1' | wc -l)
  INVOK=$(tail -n +2 "$FILE" | awk -F',' '$11=="OK"' | wc -l)
  echo "Fold $FOLD: $N filas | etiqueta=1 (cambio en ventana): $POS | invariante OK: $INVOK/$N"
done
echo ""
echo "Listo: D3_FOLD_TRAIN.csv y D3_FOLD_TEST.csv (en WILLIAM_SPRINT_01)"
