#!/usr/bin/env bash

set -e

CONTAINER_NAME="drl_nav_container"

echo "================================================="
echo " [Terminal 1] Compilando Pacotes e Abrindo Simulação"
echo "================================================="

xhost +local:root > /dev/null 2>&1 || true

docker compose build
docker compose up -d drl_nav

echo "Compilando pacotes e iniciando simulação indoor..."
docker exec -it "$CONTAINER_NAME" bash -c "
  export TURTLEBOT3_MODEL=waffle && \
  export DRLNAV_BASE_PATH=/root/ros2_ws && \
  export ROS_DOMAIN_ID=1 && \
  export GAZEBO_MODEL_PATH=\$GAZEBO_MODEL_PATH:/root/ros2_ws/src/turtlebot3_simulations/turtlebot3_gazebo/models:/root/ros2_ws/src/custom_environments/models && \
  source /opt/ros/foxy/setup.bash && \
  cd /root/ros2_ws && \
  colcon build --symlink-install --packages-select custom_environments && \
  source /root/ros2_ws/install/setup.bash && \
  ros2 launch custom_environments simple_indoor.launch.py
"