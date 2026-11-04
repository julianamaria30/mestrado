#!/usr/bin/env python3
"""Compara todas as rodadas de experiments/*/ (meta.json + metrics.csv).
Saídas em experiments/_analysis/: summary.csv, curvas por mundo/robô, barras comparativas."""
import glob, json, os, sys
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

WORLD_ORDER = ['simple_indoor', 'medium_indoor', 'complex_indoor']
LAST_N = 5          # "desempenho final" = média das últimas N avaliações
GOAL_TARGET = 0.8   # época em que a taxa de sucesso atinge este valor


def load(exp_dir):
    runs = []
    for d in sorted(glob.glob(os.path.join(exp_dir, '*/'))):
        meta_p, met_p = os.path.join(d, 'meta.json'), os.path.join(d, 'metrics.csv')
        if os.path.basename(d.rstrip('/')).startswith('_') or not (os.path.exists(meta_p) and os.path.exists(met_p)):
            continue
        meta = json.load(open(meta_p)); df = pd.read_csv(met_p)
        if df.empty: continue
        runs.append((meta, df))
    return runs


def summarize(runs):
    rows = []
    for m, df in runs:
        tail = df.tail(LAST_N)
        # normaliza taxas dadas em % para fração
        goal = df['goal_rate'] / 100 if df['goal_rate'].max(skipna=True) > 1 else df['goal_rate']
        hit = df.loc[goal >= GOAL_TARGET, 'epoch']
        rows.append({'run': m['run'], 'algo': m['algo'], 'world': m['world'], 'robot': m['robot'],
                     'epochs': int(df['epoch'].max()),
                     'final_reward': tail['avg_reward'].mean(), 'best_reward': df['avg_reward'].max(),
                     'final_goal_rate': tail['goal_rate'].mean(), 'final_collision_rate': tail['collision_rate'].mean(),
                     f'epoch_to_goal_{GOAL_TARGET}': int(hit.iloc[0]) if len(hit) else None})
    return pd.DataFrame(rows)


def curves(runs, out):
    for metric, label in [('avg_reward', 'Recompensa média'), ('goal_rate', 'Taxa de sucesso'), ('collision_rate', 'Taxa de colisão')]:
        keys = sorted({(m['world'], m['robot']) for m, _ in runs}, key=lambda k: (WORLD_ORDER.index(k[0]) if k[0] in WORLD_ORDER else 9, k[1]))
        fig, axs = plt.subplots(1, len(keys), figsize=(5 * len(keys), 4), squeeze=False, sharey=True)
        for ax, (w, r) in zip(axs[0], keys):
            for m, df in runs:
                if (m['world'], m['robot']) == (w, r):
                    ax.plot(df['epoch'], df[metric], label=m['algo'])
            ax.set_title(f'{w} | {r}'); ax.set_xlabel('época'); ax.grid(alpha=.3); ax.legend()
        axs[0][0].set_ylabel(label)
        fig.tight_layout(); fig.savefig(os.path.join(out, f'curves_{metric}.png'), dpi=130); plt.close(fig)


def bars(summary, out):
    for metric in ['final_reward', 'final_goal_rate', 'final_collision_rate']:
        s = summary.copy(); s['cenario'] = s['world'] + '\n' + s['robot']
        piv = s.pivot_table(index='cenario', columns='algo', values=metric, aggfunc='mean')
        piv = piv.reindex(sorted(piv.index, key=lambda c: (WORLD_ORDER.index(c.split('\n')[0]) if c.split('\n')[0] in WORLD_ORDER else 9, c)))
        ax = piv.plot(kind='bar', figsize=(max(6, 2 * len(piv)), 4), rot=0)
        ax.set_title(metric); ax.grid(axis='y', alpha=.3)
        plt.tight_layout(); plt.savefig(os.path.join(out, f'bars_{metric}.png'), dpi=130); plt.close()


if __name__ == '__main__':
    exp = sys.argv[1] if len(sys.argv) > 1 else 'experiments'
    for d in glob.glob(os.path.join(exp, '*/train.log')):          # fallback: só se não houver metrics.csv
        if os.path.exists(os.path.join(os.path.dirname(d), 'metrics.csv')): continue
        os.system(f'python3 {os.path.join(os.path.dirname(__file__), "parse_logs.py")} {os.path.dirname(d)} >/dev/null')
    runs = load(exp)
    if not runs:
        sys.exit('Nenhuma rodada com métricas em ' + exp)
    out = os.path.join(exp, '_analysis'); os.makedirs(out, exist_ok=True)
    summary = summarize(runs); summary.to_csv(os.path.join(out, 'summary.csv'), index=False)
    curves(runs, out); bars(summary, out)
    print(summary.round(3).to_string(index=False)); print('\nSaídas em', out)
