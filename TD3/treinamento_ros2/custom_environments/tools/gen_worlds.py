#!/usr/bin/env python3
"""Gera simple/medium/complex_indoor.world + <mundo>.json (retângulos estáticos usados pelo ambiente DRL).

Compatível com o ambiente original (ros_python.py): arena `10by10`, obstacle1..8 (5..8 são reposicionados
a cada episódio), robô e alvo sorteados em [-4,4]. Dificuldade crescente = obstáculos ESTÁTICOS extras.
O robô NÃO está no .world: é spawnado pelo launch (turtlebot3_waffle ou jackal).
Uso: python3 custom_environments/tools/gen_worlds.py"""
import json, os

HEAD = """<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="default">
    <plugin name="gazebo_ros_state" filename="libgazebo_ros_state.so">
      <ros><namespace>/gazebo</namespace></ros>
      <update_rate>1.0</update_rate>
    </plugin>
    <include><uri>model://ground_plane</uri></include>
    <include><uri>model://sun</uri></include>
    <physics type="ode">
      <real_time_update_rate>1000.0</real_time_update_rate>
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1</real_time_factor>
    </physics>
    <include><uri>model://10by10</uri></include>
""" + "".join(f"    <include><uri>model://obstacle{i}</uri></include>\n" for i in range(1, 9))
TAIL = "  </world>\n</sdf>\n"

# (nome, cx, cy, sx, sy)  -- caixas/paredes axis-aligned, dentro de [-4,4]; altura 1.0 m
MEDIUM = [("box_m0", 0.0, 2.2, 0.6, 0.6), ("box_m1", -0.8, -2.6, 0.6, 0.6), ("box_m2", 1.5, 0.3, 0.6, 0.6),
          ("wall_m0", -3.6, 1.5, 1.6, 0.2)]
COMPLEX = MEDIUM + [("box_c0", -1.5, 1.0, 0.6, 0.6), ("box_c1", 0.8, -1.5, 0.6, 0.6), ("box_c2", 3.8, 0.0, 0.6, 0.6),
                    ("box_c3", -3.8, -2.5, 0.6, 0.6), ("box_c4", 1.5, 3.6, 0.6, 0.6),
                    ("wall_c0", 1.0, -3.1, 0.2, 1.8), ("wall_c1", 3.0, 1.2, 1.8, 0.2),
                    ("pillar_c0", -1.2, -1.6, 0.5, 0.5), ("pillar_c1", 3.5, -1.0, 0.5, 0.5)]
WORLDS = {"simple_indoor": [], "medium_indoor": MEDIUM, "complex_indoor": COMPLEX}

def model(name, cx, cy, sx, sy, h=1.0):
    g = f"<box><size>{sx} {sy} {h}</size></box>"
    return f"""    <model name="{name}"><static>true</static><pose>{cx} {cy} {h/2} 0 0 0</pose>
      <link name="link"><collision name="c"><geometry>{g}</geometry></collision>
        <visual name="v"><geometry>{g}</geometry><material><ambient>0.5 0.35 0.2 1</ambient><diffuse>0.5 0.35 0.2 1</diffuse></material></visual>
      </link></model>
"""

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "worlds")
    os.makedirs(out, exist_ok=True)
    for w, items in WORLDS.items():
        with open(os.path.join(out, f"{w}.world"), "w") as f:
            f.write(HEAD + "".join(model(*i) for i in items) + TAIL)
        with open(os.path.join(out, f"{w}.json"), "w") as f:   # lido por drl_overrides/world_config.py
            json.dump({"world": w, "static_rects": [{"name": n, "cx": cx, "cy": cy, "hx": sx / 2, "hy": sy / 2}
                                                   for n, cx, cy, sx, sy in items]}, f, indent=2)
        print("gerado:", w, f"({len(items)} obstáculos estáticos extras)")
