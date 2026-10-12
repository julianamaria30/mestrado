# #!/usr/bin/env bash

# set -e

# CONTAINER_NAME="drl_nav_container"

# echo "================================================="
# echo " [Terminal 2] Conectando e Iniciando Treinamento"
# echo "================================================="

# docker exec -it "$CONTAINER_NAME" bash -c "
#   export TURTLEBOT3_MODEL=waffle && \
#   export DRLNAV_BASE_PATH=/root/workspace && \
#   source /opt/ros/foxy/setup.bash && \
#   source /root/ros2_ws/install/setup.bash && \
#   cd /root/ros2_ws && \
#   python3 src/drl_navigation_ros2/train.py
# "
#!/usr/bin/env bash

set -e

CONTAINER_NAME="drl_nav_container"

echo "================================================="
echo " [Terminal 2] Conectando e Iniciando Treinamento"
echo "================================================="

docker exec -it "$CONTAINER_NAME" bash -c "
  export TURTLEBOT3_MODEL=waffle && \
  export DRLNAV_BASE_PATH=/root/ros2_ws && \
  export ROS_DOMAIN_ID=1 && \
  export PYTHONUNBUFFERED=1 && \
  source /opt/ros/foxy/setup.bash && \
  source /root/ros2_ws/install/setup.bash && \
  cd /root/ros2_ws && \
  python3 -u src/drl_navigation_ros2/train.py  | tee "~/ros2_ws/src/custom_environments/logs/exp1_ddpg_$(date +'%Y%m%d_%H%M').txt"
"

# mkdir -p logs
# python3 -u train.py 2>&1 | tee "~/ros2_ws/custom_environments/logs/exp1_ddpg_$(date +'%Y%m%d_%H%M').txt"