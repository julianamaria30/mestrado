#!/usr/bin/env bash

set -e

CONTAINER_NAME="drl_nav_container"

echo "================================================="
echo " [Terminal 1] Compilando Pacotes e Iniciando Simulação (Jackal)"
echo "================================================="

xhost +local:root > /dev/null 2>&1 || true

docker compose build
docker compose up -d drl_nav

echo "Compilando pacotes e iniciando simulação com o robô Jackal..."
docker exec -it "$CONTAINER_NAME" bash -c "
  export DRLNAV_BASE_PATH=/root/ros2_ws && \
  export ROS_DOMAIN_ID=1 && \
  export GAZEBO_MODEL_PATH=\$GAZEBO_MODEL_PATH:/root/ros2_ws/src/custom_environments/models:/opt/ros/foxy/share/clearpath_gazebo/models && \
  source /opt/ros/foxy/setup.bash && \
  cd /root/ros2_ws && \
  colcon build --symlink-install --packages-select custom_environments && \
  source /root/ros2_ws/install/setup.bash && \
  ros2 launch custom_environments jackal_simple_indoor.launch.py
"