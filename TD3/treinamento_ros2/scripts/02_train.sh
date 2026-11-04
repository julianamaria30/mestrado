#!/usr/bin/env bash
# Terminal 2 (modo manual): treina com a simulação já rodando e SALVA tudo em experiments/<run>/.
# Uso: scripts/02_train.sh <SAC|TD3> <mundo> <robo> [tag]
# O train.py upstream é ajustado automaticamente (drl_overrides/apply_overrides.py, chamado em build_pkg).
# Opcionais: DRL_MAX_EPOCHS, DRL_SEED, DRL_PRETRAIN=0|1, DRL_COLLISION_DELTA, DRL_{SCAN,ODOM,CMD_VEL}_TOPIC
set -e
source "$(dirname "$0")/common.sh"
ALGO="${1:-SAC}"; WORLD="${2:-simple_indoor}"; ROBOT="${3:-turtlebot3}"; TAG="${4:-$(date +%Y%m%d_%H%M)}"
check_in "$ALGO" "$VALID_ALGOS" algoritmo; check_in "$WORLD" "$VALID_WORLDS" mundo; check_in "$ROBOT" "$VALID_ROBOTS" robô
ensure_up

RUN="${ALGO}_${WORLD}_${ROBOT}_${TAG}"
RUN_DIR="$ROOT_DIR/experiments/$RUN"
mkdir -p "$RUN_DIR/weights" "$RUN_DIR/tensorboard" "$ROOT_DIR/pesos_treinamento/$ALGO"
cat > "$RUN_DIR/meta.json" <<JSON
{"run": "$RUN", "algo": "$ALGO", "world": "$WORLD", "robot": "$ROBOT", "tag": "$TAG",
 "start": "$(date -Iseconds)", "git": "$(git -C "$ROOT_DIR" rev-parse --short HEAD 2>/dev/null || echo n/a)"}
JSON
echo "[run] $RUN  ->  experiments/$RUN"

# isola os pesos desta rodada (guarda os anteriores em pesos_treinamento/_backup_<ts>/)
if [ -n "$(ls -A "$ROOT_DIR/pesos_treinamento/$ALGO" 2>/dev/null)" ]; then
  BK="$ROOT_DIR/pesos_treinamento/_backup_$(date +%Y%m%d_%H%M%S)"; mkdir -p "$BK"
  mv "$ROOT_DIR/pesos_treinamento/$ALGO" "$BK/"
fi
mkdir -p "$ROOT_DIR/pesos_treinamento/$ALGO"

# repassa variáveis opcionais do host para dentro do container (docker exec não herda o ambiente)
FWD=""
for v in DRL_MAX_EPOCHS DRL_SEED DRL_PRETRAIN DRL_COLLISION_DELTA DRL_STATIC_CLEARANCE DRL_SCAN_TOPIC DRL_ODOM_TOPIC DRL_CMD_VEL_TOPIC; do
  [ -n "${!v}" ] && FWD+="export $v=${!v}; "
done

set +e
dexect "$FWD export DRL_ALGO=$ALGO DRL_WORLD=$WORLD DRL_ROBOT=$ROBOT DRL_METRICS_CSV=/root/experiments/$RUN/metrics.csv; cd /root/ros2_ws && \
  python3 -u src/drl_navigation_ros2/train.py 2>&1 | tee /root/experiments/$RUN/train.log"
STATUS=${PIPESTATUS[0]}
set -e

# coleta artefatos: pesos + tensorboard
dexec "cp -r /root/ros2_ws/src/drl_navigation_ros2/models/$ALGO/. /root/experiments/$RUN/weights/ 2>/dev/null; \
  [ -d /root/ros2_ws/runs ] && find /root/ros2_ws/runs -mindepth 1 -maxdepth 1 -newer /root/experiments/$RUN/meta.json -exec cp -r {} /root/experiments/$RUN/tensorboard/ \; ; true"
python3 - <<PY
import json; p="$RUN_DIR/meta.json"; m=json.load(open(p))
m["end"]="$(date -Iseconds)"; m["exit_status"]=$STATUS
json.dump(m,open(p,"w"),indent=2)
PY
[ -s "$RUN_DIR/metrics.csv" ] || python3 "$ROOT_DIR/analysis/parse_logs.py" "$RUN_DIR" || true  # fallback: regex no log
echo "[ok] artefatos salvos em experiments/$RUN"
