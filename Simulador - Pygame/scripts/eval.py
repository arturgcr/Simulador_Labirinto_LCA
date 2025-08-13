# Simulador - Pygame/scripts/eval.py
# Versão corrigida: closed-loop + 'steps' inicializado + residual carregado 1x

import argparse, statistics
from include.env import MazeEnv
from include.policy_wavefront import cells_to_actions
from include.policy_residual import ResidualPolicy

def run(env, mode, residual_path=None, episodes=100):
    assert mode in ("professor", "residual")
    respi = None
    if mode == "residual":
        if residual_path is None:
            raise ValueError("Em modo 'residual', passe --residual <modelo.pt>")
        respi = ResidualPolicy(residual_path)

    succ, ratios, turns, colls, lat = [], [], [], [], []

    for _ in range(episodes):
        obs = env.reset()
        steps = 0                       # <<< ESSENCIAL
        num_turns = 0
        done = False
        last_info = {"collisions": 0, "latency_ms": 0.0}

        max_steps = 5 * (env.linhas * env.colunas)  # limite de segurança

        while not done and steps < max_steps:
            # replaneja do estado atual (malha fechada)
            cells = env.optimal_path_cells()
            if not cells or len(cells) < 2:
                break
            next_actions = cells_to_actions(cells)
            a_p = next_actions[0]

            a = a_p if mode == "professor" else respi.decide(obs, a_p)
            if a in ("L", "R"):
                num_turns += 1

            obs, reward, done, info = env.step(a)
            last_info = info
            steps += 1

        opt = env.optimal_cost()
        if opt is None:
            continue

        succ.append(done)
        ratios.append((steps / opt) if done else 999.0)
        turns.append(num_turns)
        colls.append(last_info.get("collisions", 0))
        lat.append(last_info.get("latency_ms", 0.0))

    if not succ:
        return {"episodes": 0}

    return {
        "episodes": len(succ),
        "success_rate": sum(succ) / len(succ),
        "path_cost_ratio_mean": statistics.mean(ratios),
        "turns_mean": statistics.mean(turns),
        "collisions_per_ep": statistics.mean(colls),
        "latency_ms_p50": statistics.median(lat),
        "latency_ms_p95": (statistics.quantiles(lat, n=20)[18] if len(lat) >= 20 else max(lat)),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["professor", "residual"], required=True)
    ap.add_argument("--residual", type=str, default=None)
    ap.add_argument("--linhas", type=int, default=15)
    ap.add_argument("--colunas", type=int, default=15)
    ap.add_argument("--gen", type=str, default="prim")
    ap.add_argument("--slip", type=float, default=0.0)
    ap.add_argument("--turn_err", type=float, default=0.0)
    ap.add_argument("--episodes", type=int, default=200)
    args = ap.parse_args()

    env = MazeEnv(
        linhas=args.linhas,
        colunas=args.colunas,
        gerador=args.gen,
        slip_p=args.slip,
        turn_error_p=args.turn_err,
    )
    res = run(env, args.mode, args.residual, args.episodes)
    print(res)

if __name__ == "__main__":
    main()
