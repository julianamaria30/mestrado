import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node

def generate_launch_description():
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_custom_env = get_package_share_directory('custom_environments')
    
    # Substitui o pacote do turtlebot3 pelo do jackal_description
    pkg_jackal_description = get_package_share_directory('jackal_description')

    # Caminho do mundo customizado
    world_path = os.path.join(pkg_custom_env, 'worlds', 'empty_indoor.world')

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    x_pose = LaunchConfiguration('x_pose', default='-2.0')
    y_pose = LaunchConfiguration('y_pose', default='-2.0')

    # 1. Servidor do Gazebo
    gazebo_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': world_path}.items()
    )

    # 2. Cliente do Gazebo (GUI)
    gazebo_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
        )
    )

    # 3. Processa o arquivo Xacro do Jackal dinamicamente para gerar a descrição do robô
    jackal_xacro_path = os.path.join(pkg_jackal_description, 'urdf', 'jackal.urdf.xacro')
    
    # Usamos o comando xacro para compilar o modelo em tempo de execução
    robot_description_content = Command([
        'xacro ', jackal_xacro_path, 
        ' sim_gazebo:=true'
    ])

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': robot_description_content
        }]
    )

    # 4. Spawna o Jackal usando o tópico 'robot_description' gerado pelo state publisher
    spawn_jackal = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'jackal',
            '-x', x_pose,
            '-y', y_pose,
            '-z', '0.1'
        ],
        output='screen'
    )

    return LaunchDescription([
        gazebo_server,
        gazebo_client,
        robot_state_publisher,
        spawn_jackal,
    ])