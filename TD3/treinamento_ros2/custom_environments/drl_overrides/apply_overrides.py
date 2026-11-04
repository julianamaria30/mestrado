#!/usr/bin/env python3
"""Aplica os ajustes sobre o código ORIGINAL do DRL-Robot-Navigation-ROS2 clonado na imagem.
Uso: apply_overrides.py [/root/ros2_ws/src/drl_navigation_ros2]"""
import os, shutil, sys

DST = sys.argv[1] if len(sys.argv) > 1 else "/root/ros2_ws/src/drl_navigation_ros2"
HERE = os.path.dirname(os.path.abspath(__file__))
MARK = "# [custom-patch]"


def patch(fname, edits):
    p = os.path.join(DST, fname)
    s = open(p).read()
    if MARK in s:
        print(f"[patch] {fname}: já aplicado"); return
    for old, new in edits:
        if s.count(old) < 1:
            sys.exit(f"[patch] ERRO em {fname}: trecho não encontrado (upstream mudou?):\n{old}")
        s = s.replace(old, new)
    open(p, "w").write(MARK + "\n" + s)
    print(f"[patch] {fname}: ok")


shutil.copy(os.path.join(HERE, "world_config.py"), os.path.join(DST, "world_config.py"))

patch("ros_python.py", [
    ("from squaternion import Quaternion\n", "from squaternion import Quaternion\nfrom world_config import CFG\n"),
    ("rclpy.init(args=args)", "rclpy.init(args=CFG.rclpy_args(args))"),
    ("collision_delta=0.4,", "collision_delta=CFG.collision_delta,"),
    ("        pos = True\n        for element in self.element_positions:",
     "        pos = CFG.free_of_static(x, y)\n        for element in self.element_positions:"),
    ('"turtlebot3_waffle"', "CFG.robot_entity"),
])

patch("utils.py", [
    ("import numpy as np\n", "import numpy as np\nfrom world_config import CFG\n"),
    ("    pos = True\n    for element in element_positions:",
     "    pos = CFG.free_of_static(x, y)\n    for element in element_positions:"),
    ('"turtlebot3_waffle"', "CFG.robot_entity"),
])

patch("train.py", [
    ("from pathlib import Path\n", "from pathlib import Path\nimport os, random\n"),
    ('    """Main training function"""\n',
     '    """Main training function"""\n'
     '    seed = int(os.environ.get("DRL_SEED", 42))\n'
     '    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)\n'),
    ("max_epochs = 100 ", 'max_epochs = int(os.environ.get("DRL_MAX_EPOCHS", 100)) '),
    ("load_saved_buffer = True ", 'load_saved_buffer = os.environ.get("DRL_PRETRAIN", "1") == "1" '),
    ("pretrain = True ", 'pretrain = os.environ.get("DRL_PRETRAIN", "1") == "1" '),
    ("    model = SAC(\n",
     '    ModelClass = TD3 if os.environ.get("DRL_ALGO", "SAC").upper() == "TD3" else SAC\n'
     "    model = ModelClass(\n"),
    ("\n\ndef eval(model, env, scenarios, epoch, max_steps):",
     "\n    model.save(filename=model.model_name, directory=model.save_directory)  # salva pesos finais\n"
     "\n\ndef eval(model, env, scenarios, epoch, max_steps):"),
    ('    print(f"Average Goal rate: {avg_goal}")\n',
     '    print(f"Average Goal rate: {avg_goal}")\n'
     '    csv_path = os.environ.get("DRL_METRICS_CSV")\n'
     "    if csv_path:\n"
     "        new = not os.path.exists(csv_path)\n"
     '        with open(csv_path, "a") as f:\n'
     '            if new: f.write("epoch,avg_reward,collision_rate,goal_rate\\n")\n'
     '            f.write(f"{epoch},{avg_reward},{avg_col},{avg_goal}\\n")\n'),
])
