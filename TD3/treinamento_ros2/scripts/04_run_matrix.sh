#!/usr/bin/env bash
# Roda uma matriz de experimentos em sequência.
# Uso: scripts/04_run_matrix.sh [fase]
#   fase: algos   -> SAC vs TD3 no mundo simples (turtlebot3)
#         worlds  -> SAC e TD3 nos 3 mundos (turtlebot3)
#         robots  -> SAC e TD3 nos 3 mundos com jackal
#         all     -> worlds + robots   (padrão: worlds)
set -e
D="$(dirname "$0")"; source "$D/common.sh"
PHASE="${1:-worlds}"; GUI="${GUI:-false}"
run() { "$D/03_experiment.sh" "$1" "$2" "$3" "$GUI" || echo "[FALHOU] $1 $2 $3"; }
case "$PHASE" in
  algos)  for a in SAC TD3; do run $a simple_indoor turtlebot3; done ;;
  worlds) for w in $VALID_WORLDS; do for a in SAC TD3; do run $a $w turtlebot3; done; done ;;
  robots) for w in $VALID_WORLDS; do for a in SAC TD3; do run $a $w jackal; done; done ;;
  all)    "$0" worlds; "$0" robots ;;
  *) echo "fase inválida"; exit 1 ;;
esac
# "$D/05_analyze.sh"
