#!/usr/bin/env bash
# Terminal 1 (modo manual): sobe só a simulação.
# Uso: scripts/01_sim.sh <simple_indoor|medium_indoor|complex_indoor> <turtlebot3|jackal> [gui=true|false]
set -e
source "$(dirname "$0")/common.sh"
WORLD="${1:-simple_indoor}"; ROBOT="${2:-turtlebot3}"; GUI="${3:-true}"
check_in "$WORLD" "$VALID_WORLDS" mundo; check_in "$ROBOT" "$VALID_ROBOTS" robô
ensure_up; xhost +local:root >/dev/null 2>&1 || true
build_pkg
dexect "$(sim_launch_cmd "$WORLD" "$ROBOT" "$GUI")"
