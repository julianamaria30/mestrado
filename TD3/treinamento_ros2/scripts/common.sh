#!/usr/bin/env bash
# Funções compartilhadas pelos scripts.
CONTAINER_NAME="${CONTAINER_NAME:-drl_nav_container}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VALID_WORLDS="simple_indoor medium_indoor complex_indoor"
VALID_ROBOTS="turtlebot3 jackal"
VALID_ALGOS="SAC TD3"

# Ambiente ROS dentro do container
ROS_ENV="export TURTLEBOT3_MODEL=waffle DRLNAV_BASE_PATH=/root/ros2_ws ROS_DOMAIN_ID=1 PYTHONUNBUFFERED=1; \
export GAZEBO_MODEL_PATH=\$GAZEBO_MODEL_PATH:/root/ros2_ws/src/turtlebot3_simulations/turtlebot3_gazebo/models:/root/ros2_ws/src/custom_environments/models:/opt/ros/foxy/share/clearpath_gazebo/models; \
source /opt/ros/foxy/setup.bash; [ -f /root/ros2_ws/install/setup.bash ] && source /root/ros2_ws/install/setup.bash;"

check_in() { # valor lista nome
  [[ " $2 " == *" $1 "* ]] || { echo "ERRO: $3 inválido '$1'. Opções: $2"; exit 1; }
}
dexec()  { docker exec -i  "$CONTAINER_NAME" bash -c "$ROS_ENV $*"; }
dexect() { docker exec -it "$CONTAINER_NAME" bash -c "$ROS_ENV $*"; }
ensure_up() {
  docker ps --format '{{.Names}}' | grep -qx "$CONTAINER_NAME" || { echo "Container parado. Rode scripts/00_setup.sh"; exit 1; }
}
build_pkg() {
  # aplica os ajustes no código upstream e garante pastas de pesos
  dexec "python3 /root/ros2_ws/src/custom_environments/drl_overrides/apply_overrides.py && mkdir -p /root/ros2_ws/src/drl_navigation_ros2/models/SAC /root/ros2_ws/src/drl_navigation_ros2/models/TD3"
  dexec "cd /root/ros2_ws && colcon build --symlink-install --packages-select custom_environments >/dev/null && echo '[ok] custom_environments compilado'"
}
sim_launch_cmd() { # world robot gui
  echo "ros2 launch custom_environments indoor_world.launch.py world:=$1 robot:=$2 gui:=$3"
}
kill_sim() {
  # padrões "[x]xx" evitam casar com o próprio comando (o container usa pid: host e enxerga processos do host)
  docker exec "$CONTAINER_NAME" bash -c "pkill -f '[t]rain.py'; pkill -f '[r]os2 launch'; pkill -x gzserver; pkill -x gzclient; pkill -f '[s]pawn_entity'; pkill -f '[r]obot_state_publisher'" >/dev/null 2>&1 || true
  sleep 3
}
