# Simulador - Pygame/scripts/pipeline.py
"""
Pipeline completo: coleta -> IL -> rótulo residual -> residual -> avaliações -> relatório.
Roda os módulos certos mesmo que você chame de fora da pasta.
"""

import os, sys, subprocess, shlex, time, ast
from pathlib import Path

# --- garanta CWD = "Simulador - Pygame"
THIS = Path(__file__).resolve()
ROOT = THIS.parent.parent  # .../Simulador - Pygame
if Path.cwd() != ROOT:
    os.chdir(ROOT)

PY = sys.executable

# ----- CONFIGS -----
N = 2000
LINHAS = 15
COLUNAS = 15
GERADOR_TREINO = "prim"
SEED = 1
SLIP_ROBUSTEZ = 0.10
TURNERR_ROBUSTEZ = 0.05
EVAL_EPISODES = 200

OUT_JSONL = f"data/demos_{GERADOR_TREINO}_l{LINHAS}_c{COLUNAS}_seed{SEED}_slip0.0_turn0.0.jsonl"
RESIDUAL_JSONL = "data/demos_with_residual.jsonl"
RESIDUAL_MODEL = "models/residual.pt"

GENS_OOD = ["kruskal", "growingtree"]

LOG_DIR = Path("reports/logs")
REPORT_PATH = Path("reports/pipeline_report.md")

def run_cmd(cmd: str, name: str):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"{name}.log"
    print(f'\n$ {cmd}\n  [log -> {log_file}]')
    proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out_lines = []
    with log_file.open("w", encoding="utf-8") as lf:
        for line in proc.stdout:
            print(line, end="")
            out_lines.append(line)
            lf.write(line)
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"Falha (rc={rc}) em: {cmd}\nVeja o log: {log_file}")
    return "".join(out_lines)

def parse_eval_output(text: str):
    last = ""
    for line in text.strip().splitlines()[::-1]:
        s = line.strip()
        if s.startswith("{") and s.endswith("}"):
            last = s
            break
    if not last:
        return None
    try:
        return ast.literal_eval(last)
    except Exception:
        return None

def write_report(rows):
    def fmt(x):
        if x is None: return "-"
        if isinstance(x, float): return f"{x:.3f}"
        return str(x)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    md = []
    md.append("# Relatório do Pipeline\n")
    md.append(f"- Python: `{sys.executable}`")
    md.append(f"- CWD: `{Path.cwd()}`")
    md.append(f"- Data/Hora: `{time.strftime('%Y-%m-%d %H:%M:%S')}`\n")
    md.append("## Resultados\n")
    md.append("| Modo | Gerador | Slip | TurnErr | Episodes | Success | PathCostRatio | Turns | Collisions/ep | Lat p50 (ms) | Lat p95 (ms) |")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        md.append("| " + " | ".join([
            r["mode"], r["gen"], fmt(r["slip"]), fmt(r["turn_err"]),
            fmt(r.get("episodes")), fmt(r.get("success_rate")),
            fmt(r.get("path_cost_ratio_mean")), fmt(r.get("turns_mean")),
            fmt(r.get("collisions_per_ep")), fmt(r.get("latency_ms_p50")),
            fmt(r.get("latency_ms_p95")),
        ]) + " |")
    REPORT_PATH.write_text("\n".join(md), encoding="utf-8")
    print(f"\n[OK] Relatório salvo em: {REPORT_PATH}")

def main():
    print("== Ambiente ==")
    print("Python:", sys.executable)
    print("CWD   :", Path.cwd())

    rows = []

    # 1) Coleta (com grafo salvo no JSONL)
    run_cmd(f'"{PY}" -m scripts.collect_dataset --n {N} --linhas {LINHAS} --colunas {COLUNAS} --gerador {GERADOR_TREINO} --seed {SEED}', "01_collect")
    if not Path(OUT_JSONL).exists():
        raise FileNotFoundError(f"Esperado: {OUT_JSONL}")

    # 2) IL (rápido: epochs/batch/limit ajustáveis se quiser)
    run_cmd(f'"{PY}" -m scripts.train_il --data "{OUT_JSONL}" --epochs 10 --batch 256 --limit 50000', "02_train_il")

    # 3) Rótulo residual
    run_cmd(f'"{PY}" -m scripts.build_residual_set --data "{OUT_JSONL}" --out "{RESIDUAL_JSONL}"', "03_build_residual")

    # 4) Treino resíduo
    run_cmd(f'"{PY}" -m scripts.train_residual --data "{RESIDUAL_JSONL}" --epochs 20', "04_train_residual")

    # 5) Eval professor (sem ruído)
    out = run_cmd(f'"{PY}" -m scripts.eval --mode professor --gen {GERADOR_TREINO} --episodes {EVAL_EPISODES}', "05_eval_prof_no_noise")
    rows.append({"mode":"professor","gen":GERADOR_TREINO,"slip":0.0,"turn_err":0.0, **(parse_eval_output(out) or {})})

    # 6) Eval professor (com ruído)
    out = run_cmd(f'"{PY}" -m scripts.eval --mode professor --gen {GERADOR_TREINO} --slip {SLIP_ROBUSTEZ} --turn_err {TURNERR_ROBUSTEZ} --episodes {EVAL_EPISODES}', "06_eval_prof_noise")
    rows.append({"mode":"professor","gen":GERADOR_TREINO,"slip":SLIP_ROBUSTEZ,"turn_err":TURNERR_ROBUSTEZ, **(parse_eval_output(out) or {})})

    # 7) Eval residual (sem ruído)
    out = run_cmd(f'"{PY}" -m scripts.eval --mode residual --residual "{RESIDUAL_MODEL}" --gen {GERADOR_TREINO} --episodes {EVAL_EPISODES}', "07_eval_resid_no_noise")
    rows.append({"mode":"residual","gen":GERADOR_TREINO,"slip":0.0,"turn_err":0.0, **(parse_eval_output(out) or {})})

    # 8) Eval residual (com ruído)
    out = run_cmd(f'"{PY}" -m scripts.eval --mode residual --residual "{RESIDUAL_MODEL}" --gen {GERADOR_TREINO} --slip {SLIP_ROBUSTEZ} --turn_err {TURNERR_ROBUSTEZ} --episodes {EVAL_EPISODES}', "08_eval_resid_noise")
    rows.append({"mode":"residual","gen":GERADOR_TREINO,"slip":SLIP_ROBUSTEZ,"turn_err":TURNERR_ROBUSTEZ, **(parse_eval_output(out) or {})})

    # 9) OOD (sem ruído)
    for gen in GENS_OOD:
        out = run_cmd(f'"{PY}" -m scripts.eval --mode professor --gen {gen} --episodes {EVAL_EPISODES}', f"09_eval_prof_{gen}")
        rows.append({"mode":"professor","gen":gen,"slip":0.0,"turn_err":0.0, **(parse_eval_output(out) or {})})
        out = run_cmd(f'"{PY}" -m scripts.eval --mode residual --residual "{RESIDUAL_MODEL}" --gen {gen} --episodes {EVAL_EPISODES}', f"10_eval_resid_{gen}")
        rows.append({"mode":"residual","gen":gen,"slip":0.0,"turn_err":0.0, **(parse_eval_output(out) or {})})

    write_report(rows)

if __name__ == "__main__":
    main()
