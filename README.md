# Mestrado
Desenvolvimento da pesquisa de mestrado - UFBA

## Branch

* Version 1: Código adaptado do repositorio reiniscimurs
/
DRL-Robot-Navigation-ROS2. Adaptado para subir versão de mundo simples. Funcional.

* Version 2: Modelo do Jackal adicionado.

* Version 3: Reorganização do repositório. Ajuste com 3 modelos de mundo. Automatizações para rodar os diferentes cenários de testes.


# DRL Navigation ROS2 — SAC vs TD3, mundos e robôs diferentes

Base: [reiniscimurs/DRL-Robot-Navigation-ROS2](https://github.com/reiniscimurs/DRL-Robot-Navigation-ROS2) (clonado dentro da imagem pelo `Dockerfile`).
Este repositório **complementa** o upstream: mundos, launches, scripts, ajustes automáticos no código clonado e análise de métricas.

## Como o ambiente upstream funciona (e por que os ajustes existem)

O `ros_python.py` original é **fixo**: tópicos relativos `scan`/`odom`/`cmd_vel`; a cada episódio teletransporta o robô
(`turtlebot3_waffle`), os obstáculos `obstacle5..8` e o alvo para posições aleatórias em **[-4, 4]²**, evitando só os 4
obstáculos fixos conhecidos; colisão = mínimo do LiDAR < 0,4 m. Por isso:

* Todos os mundos usam a arena `10by10` e `obstacle1..8` do upstream. A complexidade vem de **obstáculos estáticos extras**,
  declarados em `worlds/<mundo>.json`.
* `apply_overrides.py` (chamado por `00_setup`/`01_sim`/`03_experiment`; falha se o upstream mudar) faz:
  * `ros_python.py`/`utils.py`: sorteio de robô/alvo/obstáculos evita os obstáculos estáticos do mundo; nome da entidade e
    `collision_delta` por robô; remap opcional de tópicos.
  * `train.py`: escolhe SAC/TD3 (`DRL_ALGO`), `DRL_MAX_EPOCHS`, `DRL_SEED`, `DRL_PRETRAIN`, grava `metrics.csv` a cada avaliação
    (`DRL_METRICS_CSV`) e **salva os pesos ao final** (o upstream só salva a cada `save_every`).
* O robô **não** vai no `.world`: o launch o spawna (`turtlebot3_waffle` ou `jackal`) e o ambiente o reposiciona a cada episódio.

## Cenários

| Mundo | Conteúdo (além de arena 10×10 e obstacle1..8 do upstream) |
|---|---|
| `simple_indoor` | (equivale ao mundo original do upstream) |
| `medium_indoor` | 3 caixas + 1 parede curta |
| `complex_indoor` | 9 caixas/pilares + 3 paredes curtas (13 estáticos) |

| Robô | Observação |
|---|---|
| `turtlebot3` | nativo (Waffle), `collision_delta` 0,4 m (valor do upstream) |
| `jackal` | maior; `collision_delta` 0,5 m e folga maior no sorteio de posições (ajustáveis em `world_config.py`) |

> `worlds/simple_indoor.world` é **regenerado** por `gen_worlds.py` (substitui o anterior).

## Scripts

* **00_setup.sh**: garante que os mundos 3D, o modelo do Jackal, o container Docker, os ajustes no código do upstream e a compilação do ROS 2 estejam prontos antes de qualquer simulação ou treino.

* **01_sim.sh**: abre apenas a simulação (mundo e robô à escolha), com ou sem interface gráfica, para inspeção visual e depuração.

* **02_train.sh**: treina o algoritmo escolhido (SAC ou TD3) com a simulação já rodando e salva logs, métricas e pesos em experiments/<rodada>/.

* **03_experiment.sh**: executa um experimento completo com um comando: sobe a simulação, treina, coleta os resultados e encerra a simulação.

* **04_run_matrix.sh**: roda vários experimentos em sequência (algoritmos, mundos e robôs) e gera a análise ao final.

* **05_analyze.sh**: consolida os resultados de todas as rodadas em tabela e gráficos comparativos em experiments/_analysis/.

* **common.sh**: biblioteca de funções e variáveis utilitárias usada por todos os outros scripts (validação de argumentos, comandos no container, compilação e encerramento da simulação).


## Ordem de execução

**Primeira vez:** `scripts/00_setup.sh`

**A) Manual (2 terminais):**
```bash
scripts/01_sim.sh medium_indoor turtlebot3          # Terminal 1
scripts/02_train.sh SAC medium_indoor turtlebot3    # Terminal 2, após o Gazebo abrir
```
**B) Automático (headless por padrão):**
```bash
scripts/03_experiment.sh TD3 complex_indoor jackal [gui=true|false] [tag]
```
**C) Campanha, do simples ao complexo:**
```bash
scripts/04_run_matrix.sh algos     # 1) SAC×TD3, mundo simples, TurtleBot3
scripts/04_run_matrix.sh worlds    # 2) SAC/TD3 nos 3 mundos, TurtleBot3
scripts/04_run_matrix.sh robots    # 3) SAC/TD3 nos 3 mundos, Jackal
scripts/05_analyze.sh              # 4) comparação (também roda ao fim da matriz) - Pendente implementação
```
Exemplo: 

``` bash 
DRL_MAX_EPOCHS=2 DRL_PRETRAIN=0 scripts/03_experiment.sh SAC simple_indoor turtlebot3 
```

(o pré-treino leva ~25 min; as variáveis DRL_* são repassadas ao container pelo `02_train.sh`). Outras variáveis: `DRL_SEED`, `DRL_PRETRAIN=0` (desliga o pré-treino com `assets/data.yml`, que vem do mundo original), `GUI=true` na matriz.

Comando para batelada de testes:
``` bash 
 sudo DRL_MAX_EPOCHS=50 DRL_PRETRAIN=0 DRL_SEED=1 ./scripts/04_run_matrix.sh all
```

## Notas

| Pergunta | Comparar |
|---|---|
| Qual algoritmo é melhor? | SAC × TD3, mesmo mundo/robô (usar a mesma `DRL_SEED`) |
| Efeito da complexidade? | simple → medium → complex, mesmo algoritmo/robô |
| Efeito do tamanho do robô? | turtlebot3 × jackal, mesmo mundo/algoritmo |
