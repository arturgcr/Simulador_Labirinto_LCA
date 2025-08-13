# ===========================
# Pipeline
# ===========================

# 0) Ir para a pasta do simulador
cd "Simulador - Pygame"

# 1) Coletar demonstrações do professor (com grafo salvo por passo)
python -m scripts.collect_dataset --n 2000 --linhas 15 --colunas 15 --gerador prim --seed 1

# 2) Treinar IL (aluno que clona o professor)
python -m scripts.train_il --data "data/demos_prim_l15_c15_seed1_slip0.0_turn0.0.jsonl" --epochs 20

# 3) Rotular resíduo usando o grafo do próprio episódio
python -m scripts.build_residual_set --data "data/demos_prim_l15_c15_seed1_slip0.0_turn0.0.jsonl" --out "data/demos_with_residual.jsonl"

# 4) Treinar rede de resíduo (KEEP/LEFT/RIGHT/BACK)
python -m scripts.train_residual --data "data/demos_with_residual.jsonl" --epochs 20

# 5) Avaliar professor (baseline, sem ruído)
python -m scripts.eval --mode professor --gen prim --episodes 200

# 6) Avaliar professor (com ruído — robustez baseline)
python -m scripts.eval --mode professor --gen prim --slip 0.10 --turn_err 0.05 --episodes 200

# 7) Avaliar professor + resíduo (sanidade, sem ruído)
python -m scripts.eval --mode residual --residual "models/residual.pt" --gen prim --episodes 200

# 8) Avaliar professor + resíduo (robustez, com ruído)
python -m scripts.eval --mode residual --residual "models/residual.pt" --gen prim --slip 0.10 --turn_err 0.05 --episodes 200

# ---- Avaliar em outros geradores ----
python -m scripts.eval --mode professor --gen kruskal --episodes 200
python -m scripts.eval --mode residual --residual "models/residual.pt" --gen kruskal --episodes 200
python -m scripts.eval --mode professor --gen growingtree --episodes 200
python -m scripts.eval --mode residual --residual "models/residual.pt" --gen growingtree --episodes 200
