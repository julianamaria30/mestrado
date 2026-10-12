FROM osrf/ros:foxy-desktop

# Evita travar a instalação com prompts de timezone
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependências do sistema e utilitários de compilação
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-colcon-common-extensions \
    git \
    ros-foxy-gazebo-* \
    ros-foxy-cartographer \
    ros-foxy-nav2-bringup \
    ros-foxy-turtlebot3-msgs \
    ros-foxy-turtlebot3 \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    && rm -rf /var/lib/apt/lists/*

# CORREÇÃO DO BUG DE OPENSSL: Atualiza o pip antes de qualquer instalação pesada
RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Instalar PyTorch (CPU version) e dependências de Machine Learning
RUN pip3 install --no-cache-dir \
    torch==1.13.1+cpu \
    torchvision==0.14.1+cpu \
    -f https://download.pytorch.org/whl/torch_stable.html

# Incluído o squaternion aqui para instalação nativa
RUN pip3 install --no-cache-dir \
    tensorboard \
    numpy==1.23.5 \
    scipy \
    squaternion\
    tqdm

# Configurar Workspace do ROS 2
WORKDIR /root/ros2_ws/src

# Clonar os repositórios (o algoritmo e as ferramentas de simulação)
RUN git clone https://github.com/reiniscimurs/DRL-Robot-Navigation-ROS2.git && \
    mv DRL-Robot-Navigation-ROS2/src/turtlebot3_simulations . && \
    mv DRL-Robot-Navigation-ROS2/src/drl_navigation_ros2 . && \
    rm -rf DRL-Robot-Navigation-ROS2

# Copiar o arquivo de launch do DRL para o diretório de simulação correto antes de compilar
RUN cp drl_navigation_ros2/launch/turtlebot3_drl_stage1.launch.py turtlebot3_simulations/turtlebot3_gazebo/launch/ 2>/dev/null || true

# Compilar o workspace ROS 2
WORKDIR /root/ros2_ws
RUN /bin/bash -c "source /opt/ros/foxy/setup.bash && colcon build --symlink-install"

# Configurar variáveis de ambiente essenciais no .bashrc
RUN echo "export TURTLEBOT3_MODEL=waffle" >> /root/.bashrc && \
    echo "export ROS_DOMAIN_ID=1" >> /root/.bashrc && \
    echo "export DRLNAV_BASE_PATH=/root/ros2_ws/src/drl_navigation_ros2" >> /root/.bashrc && \
    echo "source /opt/ros/foxy/setup.bash" >> /root/.bashrc && \
    echo "source /root/ros2_ws/install/setup.bash" >> /root/.bashrc

# Criar diretórios de saída para os pesos do modelo e logs (Incluindo a pasta do SAC)
RUN mkdir -p /root/workspace/models /root/workspace/logs /root/ros2_ws/src/drl_navigation_ros2/models/SAC

# Criar diretórios de saída para os pesos do modelo e logs
RUN mkdir -p /root/workspace/models /root/workspace/logs

# Copiar script de inicialização do container
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
