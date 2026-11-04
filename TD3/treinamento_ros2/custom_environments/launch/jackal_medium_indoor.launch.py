"""Atalho: mundo 'medium_indoor' com robô 'jackal'."""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg = get_package_share_directory('custom_environments')
    return LaunchDescription([
        DeclareLaunchArgument('gui', default_value='true'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(pkg, 'launch', 'indoor_world.launch.py')),
            launch_arguments={'world': 'medium_indoor', 'robot': 'jackal',
                              'gui': LaunchConfiguration('gui')}.items()),
    ])
