#!/usr/bin/env bash
# Automatizado: sobe simulação (em background) + treina + coleta + derruba a simulação.
# Uso: scripts/03_experiment.sh <SAC|TD3> <mundo> <robo> [gui=false] [tag]
set -e
source "$(dirname "$0")/common.sh"
ALGO="${1:?algo}"; WORLD="${2:?mundo}"; ROBOT="${3:?robo}"; GUI="${4:-false}"; TAG="${5:-$(date +%Y%m%d_%H%M)}"
check_in "$ALGO" "$VALID_ALGOS" algoritmo; check_in "$WORLD" "$VALID_WORLDS" mundo; check_in "$ROBOT" "$VALID_ROBOTS" robô
ensure_up; xhost +local:root >/dev/null 2>&1 || true
SCAN_TOPIC="${SCAN_TOPIC:-/scan}"
RUN="${ALGO}_${WORLD}_${ROBOT}_${TAG}"
mkdir -p "$ROOT_DIR/experiments/$RUN"
trap 'echo "[cleanup] encerrando simulação"; kill_sim' EXIT

build_pkg; kill_sim
echo "[sim] subindo $WORLD / $ROBOT (gui=$GUI)"
docker exec -d "$CONTAINER_NAME" bash -c "$ROS_ENV $(sim_launch_cmd "$WORLD" "$ROBOT" "$GUI") > /root/experiments/$RUN/sim.log 2>&1"

echo -n "[sim] aguardando $SCAN_TOPIC "
for i in $(seq 1 90); do
  if dexec "ros2 topic list 2>/dev/null | grep -qx '$SCAN_TOPIC'"; then echo " pronto"; break; fi
  echo -n "."; sleep 2
  [ "$i" = 90 ] && { echo; echo "ERRO: sensor não apareceu (veja experiments/$RUN/sim.log)"; exit 1; }
done
sleep 5
"$(dirname "$0")/02_train.sh" "$ALGO" "$WORLD" "$ROBOT" "$TAG"
