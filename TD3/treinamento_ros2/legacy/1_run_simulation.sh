#!/usr/bin/env bash

set -e

CONTAINER_NAME="drl_nav_container"

echo "================================================="
echo " [Terminal 1] Subindo Container e Simulação Gazebo"
echo "================================================="

xhost +local:root > /dev/null 2>&1 || true

docker compose build
docker compose up -d drl_nav

echo "Iniciando a simulação..."
docker exec -it "$CONTAINER_NAME" bash -c "
  export TURTLEBOT3_MODEL=waffle && \
  export DRLNAV_BASE_PATH=/root/ros2_ws && \
  export ROS_DOMAIN_ID=1 && \
  source /opt/ros/foxy/setup.bash && \
  source /root/ros2_ws/install/setup.bash && \
  ros2 launch turtlebot3_gazebo ros2_drl.launch.py
"