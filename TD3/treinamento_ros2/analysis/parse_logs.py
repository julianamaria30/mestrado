#!/usr/bin/env python3
"""Extrai métricas de avaliação de experiments/<run>/train.log -> metrics.csv
Uso: parse_logs.py <pasta_da_run> [<outra> ...]   |   parse_logs.py <arquivo.txt>

AJUSTE AQUI se o formato do print do seu train.py for diferente:"""
import csv, re, sys, os

RE_EPOCH = re.compile(r'epoch\D{0,5}(\d+)', re.I)
RE_REWARD = re.compile(r'average\s+reward\D*?(-?\d+(?:\.\d+)?(?:e-?\d+)?)', re.I)
RE_COLL = re.compile(r'average\s+collision\D*?(-?\d+(?:\.\d+)?(?:e-?\d+)?)', re.I)
RE_GOAL = re.compile(r'average\s+goal\D*?(-?\d+(?:\.\d+)?(?:e-?\d+)?)', re.I)


def parse(path):
    rows, cur, epoch = [], None, 0
    with open(path, errors='ignore') as f:
        for line in f:
            m = RE_EPOCH.search(line)
            if m:
                epoch = int(m.group(1))
            m = RE_REWARD.search(line)
            if m:
                cur = {'epoch': epoch if epoch else len(rows) + 1, 'avg_reward': float(m.group(1)),
                       'collision_rate': None, 'goal_rate': None}
                rows.append(cur)
                continue
            if cur is not None:
                m = RE_COLL.search(line)
                if m: cur['collision_rate'] = float(m.group(1))
                m = RE_GOAL.search(line)
                if m: cur['goal_rate'] = float(m.group(1))
    return rows


def main(targets):
    for t in targets:
        log = t if os.path.isfile(t) else os.path.join(t, 'train.log')
        out = os.path.join(os.path.dirname(log), 'metrics.csv')
        if not os.path.exists(log):
            print(f'[aviso] sem log: {log}'); continue
        rows = parse(log)
        with open(out, 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=['epoch', 'avg_reward', 'collision_rate', 'goal_rate'])
            w.writeheader(); w.writerows(rows)
        print(f'[parse] {len(rows)} avaliações -> {out}')
        if not rows:
            print('        nenhuma métrica reconhecida: ajuste as regex no topo de parse_logs.py')


if __name__ == '__main__':
    main(sys.argv[1:] or ['.'])
