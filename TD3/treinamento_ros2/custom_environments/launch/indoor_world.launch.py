"""Launch genérico: qualquer mundo x qualquer robô.
  ros2 launch custom_environments indoor_world.launch.py world:=medium_indoor robot:=jackal gui:=false
Os launches simple_/medium_/complex_indoor(.launch.py) e jackal_* são só atalhos para este."""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node


def _setup(context, *args, **kwargs):
    world = LaunchConfiguration('world').perform(context)
    robot = LaunchConfiguration('robot').perform(context)
    gui = LaunchConfiguration('gui').perform(context).lower() == 'true'
    x_pose = LaunchConfiguration('x_pose')
    y_pose = LaunchConfiguration('y_pose')
    use_sim_time = LaunchConfiguration('use_sim_time')
    entity = LaunchConfiguration('entity_name').perform(context) or \
        ('turtlebot3_waffle' if robot == 'turtlebot3' else 'jackal')  # nomes esperados pelo ambiente DRL

    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_custom_env = get_package_share_directory('custom_environments')
    world_path = os.path.join(pkg_custom_env, 'worlds', f'{world}.world')

    actions = [IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')),
        launch_arguments={'world': world_path}.items())]
    if gui:
        actions.append(IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py'))))

    if robot == 'turtlebot3':
        pkg_tb3 = get_package_share_directory('turtlebot3_gazebo')
        actions.append(IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(pkg_tb3, 'launch', 'robot_state_publisher.launch.py')),
            launch_arguments={'use_sim_time': use_sim_time}.items()))
        actions.append(Node(
            package='gazebo_ros', executable='spawn_entity.py', output='screen',
            arguments=['-entity', entity,
                       '-file', os.path.join(pkg_tb3, 'models', 'turtlebot3_waffle', 'model.sdf'),
                       '-x', x_pose, '-y', y_pose, '-z', '0.01',
                       '-spawn_service_timeout', '300', '-timeout', '300']))
    elif robot == 'jackal':
        # URDF próprio (gerado por tools/gen_jackal_urdf.py): o xacro oficial exige jackal_control/ros2_control
        urdf_path = os.path.join(pkg_custom_env, 'launch', 'jackal_drl.urdf')
        with open(urdf_path) as f:
            robot_description = f.read()
        actions.append(Node(
            package='robot_state_publisher', executable='robot_state_publisher', output='screen',
            parameters=[{'use_sim_time': use_sim_time, 'robot_description': robot_description}]))
        actions.append(Node(
            package='gazebo_ros', executable='spawn_entity.py', output='screen',
            arguments=['-file', urdf_path, '-entity', entity,
                       '-x', x_pose, '-y', y_pose, '-z', '0.1',
                       '-spawn_service_timeout', '300', '-timeout', '300']))
    else:
        raise RuntimeError(f"robot desconhecido: '{robot}' (use turtlebot3 ou jackal)")
    return actions


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('world', default_value='simple_indoor'),
        DeclareLaunchArgument('robot', default_value='turtlebot3'),
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument('x_pose', default_value='0.0'),
        DeclareLaunchArgument('y_pose', default_value='0.0'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('entity_name', default_value=''),
        OpaqueFunction(function=_setup),
    ])
