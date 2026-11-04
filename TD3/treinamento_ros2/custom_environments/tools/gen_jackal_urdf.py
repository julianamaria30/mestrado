#!/usr/bin/env python3
"""Gera custom_environments/launch/jackal_drl.urdf: Jackal autocontido para Gazebo clássico (Foxy).
Motivo: o jackal.urdf.xacro do pacote exige ros2_control/jackal_control e não traz LiDAR nem tração para o gazebo_ros.
Dimensões/massas/inércias vêm do jackal.urdf.xacro oficial; sem meshes (só caixas/cilindros).
Sensor e tração equivalem aos do TurtleBot3 Waffle do upstream, p/ comparação justa:
  LiDAR 180 amostras (-90°..+90°), 0,2-7 m, 30 Hz, tópico 'scan'; diff_drive em 'cmd_vel' / 'odom' (odometria do mundo)."""
import os

WB, TRACK, WR, WW = 0.262, 0.37559, 0.098, 0.040          # wheelbase, track, raio e largura da roda
WZ, CZ = 0.0345, 0.0635                                    # altura do eixo da roda e do chassi sobre o solo/base_link
CL, CW, CH = 0.420, 0.310, 0.184                           # chassi
LIDAR_Z = CH + 0.006                                       # LiDAR logo acima do chassi (plano de scan ~0,25 m do chão)


def wheel(name, x, y):
    return f"""
  <link name="{name}_wheel_link">
    <visual><origin xyz="0 0 0" rpy="1.5708 0 0"/><geometry><cylinder radius="{WR}" length="{WW}"/></geometry><material name="black"/></visual>
    <collision><origin xyz="0 0 0" rpy="1.5708 0 0"/><geometry><cylinder radius="{WR}" length="{WW}"/></geometry></collision>
    <inertial><origin xyz="0 0 0" rpy="0 0 0"/><mass value="0.477"/><inertia ixx="0.0013" ixy="0" ixz="0" iyy="0.0024" iyz="0" izz="0.0013"/></inertial>
  </link>
  <joint name="{name}_wheel_joint" type="continuous">
    <parent link="chassis_link"/><child link="{name}_wheel_link"/>
    <origin xyz="{x} {y} {WZ}" rpy="0 0 0"/><axis xyz="0 1 0"/>
  </joint>
  <gazebo reference="{name}_wheel_link">
    <material>Gazebo/DarkGrey</material><selfCollide>false</selfCollide>
    <mu1>1.0</mu1><mu2>0.2</mu2><kp>10000000.0</kp><kd>1.0</kd><fdir1>1 0 0</fdir1>
  </gazebo>"""


URDF = f"""<?xml version="1.0"?>
<!-- GERADO por tools/gen_jackal_urdf.py. Não editar à mão. -->
<robot name="jackal">
  <material name="dark_grey"><color rgba="0.2 0.2 0.2 1.0"/></material>
  <material name="black"><color rgba="0.15 0.15 0.15 1.0"/></material>
  <material name="yellow"><color rgba="0.8 0.8 0.0 1.0"/></material>

  <link name="base_link"/>   <!-- no nível do solo: o ambiente DRL teletransporta o robô com z=0 -->
  <joint name="base_link_joint" type="fixed">
    <origin xyz="0 0 {CZ}" rpy="0 0 0"/><parent link="base_link"/><child link="chassis_link"/>
  </joint>

  <link name="chassis_link">
    <visual><origin xyz="0 0 {CH/2}"/><geometry><box size="{CL} {CW} {CH}"/></geometry><material name="yellow"/></visual>
    <collision><origin xyz="0 0 {CH/2}"/><geometry><box size="{CL} {CW} {CH}"/></geometry></collision>
    <inertial><origin xyz="0.012 0.002 0.067" rpy="0 0 0"/><mass value="16.523"/>
      <inertia ixx="0.3136" ixy="-0.0008" ixz="0.0164" iyy="0.3922" iyz="-0.0009" izz="0.4485"/></inertial>
  </link>
  <gazebo reference="chassis_link"><material>Gazebo/Yellow</material></gazebo>
{wheel("front_left", WB/2, TRACK/2)}{wheel("front_right", WB/2, -TRACK/2)}{wheel("rear_left", -WB/2, TRACK/2)}{wheel("rear_right", -WB/2, -TRACK/2)}

  <link name="base_scan">
    <visual><geometry><cylinder radius="0.03" length="0.04"/></geometry><material name="black"/></visual>
    <inertial><mass value="0.1"/><inertia ixx="1e-4" ixy="0" ixz="0" iyy="1e-4" iyz="0" izz="1e-4"/></inertial>
  </link>
  <joint name="base_scan_joint" type="fixed">
    <origin xyz="0 0 {LIDAR_Z + 0.02}" rpy="0 0 0"/><parent link="chassis_link"/><child link="base_scan"/>
  </joint>

  <gazebo reference="base_scan">
    <sensor name="lidar" type="ray">
      <always_on>true</always_on><visualize>false</visualize><update_rate>30</update_rate>
      <ray>
        <scan><horizontal><samples>180</samples><resolution>1.0</resolution>
          <min_angle>-1.57079</min_angle><max_angle>1.57079</max_angle></horizontal></scan>
        <range><min>0.2</min><max>7.0</max><resolution>0.015</resolution></range>
        <noise><type>gaussian</type><mean>0.0</mean><stddev>0.01</stddev></noise>
      </ray>
      <plugin name="jackal_lidar" filename="libgazebo_ros_ray_sensor.so">
        <ros><remapping>~/out:=scan</remapping></ros>
        <output_type>sensor_msgs/LaserScan</output_type>
        <frame_name>base_scan</frame_name>
      </plugin>
    </sensor>
  </gazebo>

  <gazebo>
    <plugin name="jackal_diff_drive" filename="libgazebo_ros_diff_drive.so">
      <ros/>
      <update_rate>30</update_rate>
      <num_wheel_pairs>2</num_wheel_pairs>
      <left_joint>front_left_wheel_joint</left_joint><left_joint>rear_left_wheel_joint</left_joint>
      <right_joint>front_right_wheel_joint</right_joint><right_joint>rear_right_wheel_joint</right_joint>
      <wheel_separation>{TRACK}</wheel_separation><wheel_separation>{TRACK}</wheel_separation>
      <wheel_diameter>{2*WR}</wheel_diameter><wheel_diameter>{2*WR}</wheel_diameter>
      <max_wheel_torque>20</max_wheel_torque>
      <max_wheel_acceleration>1.0</max_wheel_acceleration>
      <command_topic>cmd_vel</command_topic>
      <odometry_source>1</odometry_source>
      <publish_odom>true</publish_odom><publish_odom_tf>true</publish_odom_tf><publish_wheel_tf>false</publish_wheel_tf>
      <odometry_topic>odom</odometry_topic><odometry_frame>odom</odometry_frame><robot_base_frame>base_link</robot_base_frame>
    </plugin>
  </gazebo>
</robot>
"""

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "launch", "jackal_drl.urdf")
    open(out, "w").write(URDF)
    print("gerado:", os.path.normpath(out))
