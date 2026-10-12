FROM osrf/ros:humble-desktop-full

ENV DEBIAN_FRONTEND=noninteractive
# Aumenta o tempo limite do pip para 100 segundos para evitar quedas por oscilação
ENV PIP_DEFAULT_TIMEOUT=100

# Instala dependências do sistema e pacotes do TurtleBot4
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-colcon-common-extensions \
    git \
    tmux \
    wget \
    ros-humble-turtlebot4-simulator \
    ros-humble-turtlebot4-desktop \
    ros-humble-turtlebot4-navigation \
    && rm -rf /var/lib/apt/lists/*

# Instala a versão leve de CPU do PyTorch para evitar o erro de download pesado
RUN pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip3 install --no-cache-dir numpy tensorboard

# Cria o workspace no local correto do repositório (~/ros2_GDAE)
WORKDIR /root/ros2_GDAE/src

# Clona o repositório
RUN git clone https://github.com/akifbayram/ros2_GDAE.git .

WORKDIR /root/ros2_GDAE

# Instala dependências restantes do ROS
RUN . /opt/ros/humble/setup.sh && \
    apt-get update && \
    rosdep update && \
    rosdep install --from-paths src --ignore-src -r -y && \
    rm -rf /var/lib/apt/lists/*

# Cria o arquivo fake do setup do turtlebot4 se ele não existir na instalação padrão
RUN mkdir -p /etc/turtlebot4 && echo "source /opt/ros/humble/setup.bash" > /etc/turtlebot4/setup.bash

# Builda o workspace
RUN . /opt/ros/humble/setup.sh && \
    colcon build --symlink-install

RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc && \
    echo "source /root/ros2_GDAE/install/setup.bash" >> ~/.bashrc

CMD ["bash"]
