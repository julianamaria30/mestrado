FROM osrf/ros:foxy-desktop

ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependências do sistema, TurtleBot3 e Jackal
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-colcon-common-extensions \
    git \
    ros-foxy-gazebo-* \
    ros-foxy-cartographer \
    ros-foxy-nav2-bringup \
    ros-foxy-turtlebot3-msgs \
    ros-foxy-turtlebot3 \
    ros-foxy-jackal-description \
    ros-foxy-xacro \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    && rm -rf /var/lib/apt/lists/*

# CORREÇÃO DO BUG DE OPENSSL: Atualiza o pip antes de qualquer instalação pesada
RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Instalar PyTorch e dependências de Machine Learning
RUN pip3 install --no-cache-dir \
    torch==1.13.1+cpu \
    torchvision==0.14.1+cpu \
    -f https://download.pytorch.org/whl/torch_stable.html

# Instalar dependências adicionais
RUN pip3 install --no-cache-dir \
    tensorboard \
    numpy==1.23.5 \
    scipy \
    squaternion \
    tqdm

# Configurar Workspace do ROS 2
WORKDIR /root/ros2_ws/src

# Clonar os repositórios (incluindo as simulações originais do TurtleBot3 e o DRL Navigation)
RUN git clone https://github.com/reiniscimurs/DRL-Robot-Navigation-ROS2.git && \
    mv DRL-Robot-Navigation-ROS2/src/turtlebot3_simulations . && \
    mv DRL-Robot-Navigation-ROS2/src/drl_navigation_ros2 . && \
    rm -rf DRL-Robot-Navigation-ROS2

# Copiar o arquivo de launch do DRL original
RUN cp drl_navigation_ros2/launch/turtlebot3_drl_stage1.launch.py turtlebot3_simulations/turtlebot3_gazebo/launch/ 2>/dev/null || true

# Compilar o workspace ROS 2
WORKDIR /root/ros2_ws
RUN /bin/bash -c "source /opt/ros/foxy/setup.bash && colcon build --symlink-install"

# Configurar variáveis de ambiente padrão no .bashrc (mantendo o TurtleBot3 por padrão, mas com suporte ao Jackal disponível)
RUN echo "export TURTLEBOT3_MODEL=waffle" >> /root/.bashrc && \
    echo "export ROS_DOMAIN_ID=1" >> /root/.bashrc && \
    echo "export DRLNAV_BASE_PATH=/root/ros2_ws/src/drl_navigation_ros2" >> /root/.bashrc && \
    echo "source /opt/ros/foxy/setup.bash" >> /root/.bashrc && \
    echo "source /root/ros2_ws/install/setup.bash" >> /root/.bashrc

# Criar diretórios de saída para os pesos do modelo e logs
RUN mkdir -p /root/workspace/models /root/workspace/logs /root/ros2_ws/src/drl_navigation_ros2/models/SAC

# Copiar script de inicialização do container
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]