# Simulador - Pygame/scripts/train_il.py
import json, argparse, random
from pathlib import Path
import torch, torch.nn as nn, torch.optim as optim

ACTIONS = ['F','B','L','R']

def obs_to_tensor(obs):
    return torch.tensor([
        1.0 if obs["wall_front"] else 0.0,
        1.0 if obs["wall_left"] else 0.0,
        1.0 if obs["wall_right"] else 0.0,
        obs["x"]/max(1, obs["goal_x"]+1),
        obs["y"]/max(1, obs["goal_y"]+1),
        obs["dir"]/3.0,
        obs["goal_x"]/max(1, obs["goal_x"]+1),
        obs["goal_y"]/max(1, obs["goal_y"]+1),
    ], dtype=torch.float32)

class MLP(nn.Module):
    def __init__(self, d_in=8, d_hidden=64, n_out=4):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_in, d_hidden), nn.ReLU(),
            nn.Linear(d_hidden, d_hidden), nn.ReLU(),
            nn.Linear(d_hidden, n_out)
        )
    def forward(self, x): return self.net(x)

def load_jsonl(path, limit=None):
    X, Y = [], []
    with open(path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if limit and i >= limit: break
            item = json.loads(line)
            X.append(obs_to_tensor(item["obs"]))
            Y.append(torch.tensor(ACTIONS.index(item["action"]), dtype=torch.long))
    X = torch.stack(X) if X else torch.empty(0,8)
    Y = torch.stack(Y) if Y else torch.empty(0, dtype=torch.long)
    return X, Y

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=str, required=True)
    ap.add_argument("--epochs", type=int, default=10)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--batch", type=int, default=128)
    ap.add_argument("--limit", type=int, default=None, help="limitar nº de linhas do JSONL (sanidade)")
    ap.add_argument("--out", type=str, default="models/il_mlp.pt")
    args = ap.parse_args()

    X, Y = load_jsonl(args.data, limit=args.limit)
    if len(X) == 0:
        print("Dataset vazio! Verifique o caminho do --data.")
        return

    # split 90/10
    idx = list(range(len(X)))
    random.shuffle(idx)
    cut = int(0.9*len(idx))
    tr_idx, va_idx = idx[:cut], idx[cut:]
    Xtr, Ytr = X[tr_idx], Y[tr_idx]
    Xva, Yva = X[va_idx], Y[va_idx]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = MLP().to(device)
    opt = optim.Adam(model.parameters(), lr=args.lr)
    crit = nn.CrossEntropyLoss()

    def batches(X, Y, bs):
        for i in range(0, len(X), bs):
            yield X[i:i+bs], Y[i:i+bs]

    for ep in range(1, args.epochs+1):
        model.train()
        tot_loss = 0.0
        n_batches = 0
        for xb, yb in batches(Xtr, Ytr, args.batch):
            xb, yb = xb.to(device), yb.to(device)
            opt.zero_grad()
            logits = model(xb)
            loss = crit(logits, yb)
            loss.backward(); opt.step()
            tot_loss += loss.item(); n_batches += 1

        model.eval()
        with torch.no_grad():
            va_logits = model(Xva.to(device))
            va_pred = va_logits.argmax(dim=1).cpu()
            va_acc = (va_pred == Yva).float().mean().item()

        print(f"epoch {ep:02d} | train_loss {tot_loss/max(1,n_batches):.4f} | val_acc {va_acc:.3f} | n_train {len(Xtr)} | n_val {len(Xva)}")

    Path("models").mkdir(exist_ok=True)
    torch.save(model.state_dict(), args.out)
    print("saved ->", args.out)

if __name__ == "__main__":
    main()
