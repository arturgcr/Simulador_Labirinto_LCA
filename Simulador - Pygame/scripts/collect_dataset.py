# scripts/collect_dataset.py  (versão com export do grafo)
import os, json, argparse
from pathlib import Path
from include.env import MazeEnv
from include.policy_wavefront import professor_policy

def run_episode(env):
    traj = []
    actions = professor_policy(env)
    if not actions:
        return traj

    # exporta grafo (edges) uma vez
    G = env._lab.labirinto
    edges = list(G.edges())
    goal = tuple(env._lab.fim)
    size = (env.linhas, env.colunas)
    gen = env.gerador

    for a in actions:
        obs, reward, done, info = env.step(a)
        traj.append({
            "obs": obs,
            "action": a,
            "done": done,
            "info": info,
            "maze_edges": edges,
            "goal": goal,
            "size": size,
            "gen": gen
        })
        if done:
            break
    return traj

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--n', type=int, default=500)
    p.add_argument('--linhas', type=int, default=15)
    p.add_argument('--colunas', type=int, default=15)
    p.add_argument('--gerador', type=str, default='prim', choices=['prim','kruskal','growingtree'])
    p.add_argument('--seed', type=int, default=123)
    p.add_argument('--slip', type=float, default=0.0)
    p.add_argument('--turn_err', type=float, default=0.0)
    args = p.parse_args()

    env = MazeEnv(linhas=args.linhas, colunas=args.colunas, gerador=args.gerador,
                  seed=args.seed, slip_p=args.slip, turn_error_p=args.turn_err)
    out = Path("data"); out.mkdir(parents=True, exist_ok=True)
    tag = f"{args.gerador}_l{args.linhas}_c{args.colunas}_seed{args.seed}_slip{args.slip}_turn{args.turn_err}"
    path = out / f"demos_{tag}.jsonl"

    with path.open("w", encoding="utf-8") as f:
        for i in range(args.n):
            env.reset()
            traj = run_episode(env)
            for step in traj:
                f.write(json.dumps(step, ensure_ascii=False) + "\n")
    print(f"OK -> {path}")

if __name__ == "__main__":
    main()

"""
cd "Simulador - Pygame"
python -m scripts.collect_dataset --n 2000 --linhas 15 --colunas 15 --gerador prim --seed 1
"""