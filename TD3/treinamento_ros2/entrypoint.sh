#!/bin/bash
set -e

# Carrega as variáveis e instalações do ROS 2
source /opt/ros/foxy/setup.bash
source /root/ros2_ws/install/setup.bash

export TURTLEBOT3_MODEL=waffle
export DRLNAV_BASE_PATH=/root/ros2_ws
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/root/ros2_ws/src/turtlebot3_simulations/turtlebot3_gazebo/models

# Executa o comando passado para o container
exec "$@"
