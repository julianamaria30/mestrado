"""Configuração por mundo/robô lida pelo ambiente DRL (ros_python.py / utils.py patchados).
Variáveis de ambiente: DRL_WORLD, DRL_ROBOT, e opcionais DRL_COLLISION_DELTA, DRL_STATIC_CLEARANCE,
DRL_SCAN_TOPIC / DRL_ODOM_TOPIC / DRL_CMD_VEL_TOPIC (remap de 'scan', 'odom', 'cmd_vel')."""
import json, os

WORLDS_DIR = os.environ.get("DRL_WORLDS_DIR", "/root/ros2_ws/src/custom_environments/worlds")

# collision_delta: distância mínima do LiDAR a um obstáculo p/ contar colisão (upstream: 0.4 para o Waffle, raio ~0.22).
# static_clearance: folga p/ sortear robô/alvo/obstáculos móveis longe dos obstáculos estáticos extras.
ROBOTS = {
    "turtlebot3": {"entity": "turtlebot3_waffle", "collision_delta": 0.4, "static_clearance": 0.7},
    "jackal":     {"entity": "jackal",            "collision_delta": 0.5, "static_clearance": 0.9},
}


class _Cfg:
    def __init__(self):
        self.world = os.environ.get("DRL_WORLD", "simple_indoor")
        self.robot = os.environ.get("DRL_ROBOT", "turtlebot3")
        r = ROBOTS[self.robot]
        self.robot_entity = r["entity"]
        self.collision_delta = float(os.environ.get("DRL_COLLISION_DELTA", r["collision_delta"]))
        self.static_clearance = float(os.environ.get("DRL_STATIC_CLEARANCE", r["static_clearance"]))
        path = os.path.join(WORLDS_DIR, f"{self.world}.json")
        self.rects = json.load(open(path))["static_rects"] if os.path.exists(path) else []
        print(f"[world_config] world={self.world} robot={self.robot} entity={self.robot_entity} "
              f"collision_delta={self.collision_delta} static_rects={len(self.rects)}")

    def free_of_static(self, x, y):
        """True se (x,y) está a mais de `static_clearance` de todos os retângulos estáticos."""
        for r in self.rects:
            dx = max(abs(x - r["cx"]) - r["hx"], 0.0)
            dy = max(abs(y - r["cy"]) - r["hy"], 0.0)
            if (dx * dx + dy * dy) ** 0.5 < self.static_clearance:
                return False
        return True

    def rclpy_args(self, args=None):
        """Remaps globais de tópico (útil p/ Jackal, cujos tópicos podem diferir de scan/odom/cmd_vel)."""
        out = list(args) if args else []
        remaps = [(n, os.environ.get(f"DRL_{n.upper()}_TOPIC")) for n in ("scan", "odom", "cmd_vel")]
        remaps = [(a, b) for a, b in remaps if b]
        if remaps:
            out += ["--ros-args"] + sum([["-r", f"{a}:={b}"] for a, b in remaps], [])
        return out or None


CFG = _Cfg()
