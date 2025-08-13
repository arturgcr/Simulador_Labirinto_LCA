# scripts/build_residual_set.py  (usa o grafo do próprio episódio)
import json, argparse, networkx as nx
from pathlib import Path

def manhattan(a,b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

def label_residual(obs, G, goal):
    """
    Se parede à frente: escolhe LEFT/RIGHT/BACK pelo menor custo heurístico.
    Caso contrário: KEEP.
    """
    if not obs["wall_front"]:
        return "KEEP"

    x,y,d = obs["x"], obs["y"], obs["dir"]
    # candidatos após girar + andar 1 célula
    options = {
        "LEFT":  ( (d-1) % 4 ),
        "RIGHT": ( (d+1) % 4 ),
        "BACK":  ( (d+2) % 4 ),
    }

    def step_from(p, ndir):
        x,y = p
        if ndir==0: return (x, y-1)
        if ndir==1: return (x+1, y)
        if ndir==2: return (x, y+1)
        return (x-1, y)

    best, best_cost = "BACK", 1e9
    for label, ndir in options.items():
        cand = step_from((x,y), ndir)
        if cand not in G.nodes:  # fora da malha válida/sem aresta
            continue
        try:
            dist = nx.shortest_path_length(G, source=cand, target=tuple(goal))
        except Exception:
            dist = manhattan(cand, goal)
        cost = 2 + dist  # 1 giro + 1 passo + dist ao goal
        if cost < best_cost:
            best_cost, best = cost, label
    return best

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=str, required=True)
    ap.add_argument("--out", type=str, required=True)
    args = ap.parse_args()

    with open(args.data,'r',encoding='utf-8') as f_in, open(args.out,'w',encoding='utf-8') as f_out:
        for line in f_in:
            item = json.loads(line)
            edges = item.get("maze_edges", None)
            goal = tuple(item["goal"])
            if edges is None:
                # sem grafo: não rotula
                continue
            G = nx.Graph(); G.add_edges_from([tuple(map(tuple,e)) for e in edges])
            obs = item["obs"]
            item["residual_label"] = label_residual(obs, G, goal)
            f_out.write(json.dumps(item, ensure_ascii=False) + "\n")
    print("OK ->", args.out)

if __name__ == "__main__":
    main()


"""
python scripts/build_residual_set.py \
  --data data/demos_prim_l15_c15_seed1_slip0.0_turn0.0.jsonl \
  --out  data/demos_with_residual.jsonl
"""