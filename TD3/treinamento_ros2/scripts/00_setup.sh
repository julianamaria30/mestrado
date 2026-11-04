#!/usr/bin/env bash
set -e
source "$(dirname "$0")/common.sh"
cd "$ROOT_DIR"
xhost +local:root >/dev/null 2>&1 || true
mkdir -p experiments pesos_treinamento
python3 custom_environments/tools/gen_worlds.py       # (re)gera mundos
python3 custom_environments/tools/gen_jackal_urdf.py  # (re)gera o URDF do Jackal
docker compose build
docker compose up -d drl_nav
build_pkg
echo "Setup concluído. Próximo: scripts/01_sim.sh <mundo> <robo>  ou  scripts/03_experiment.sh ..."
