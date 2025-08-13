# scripts/train_residual.py
import json, argparse, random
from pathlib import Path
import torch, torch.nn as nn, torch.optim as optim

RES = ['KEEP','LEFT','RIGHT','BACK']

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

class ResidualNet(nn.Module):
    def __init__(self, d=8, h=32, k=4):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d, h), nn.ReLU(),
            nn.Linear(h, h), nn.ReLU(),
            nn.Linear(h, k)
        )
    def forward(self, x): return self.net(x)

def load_jsonl(path):
    ds = []
    with open(path,'r',encoding='utf-8') as f:
        for line in f:
            it = json.loads(line)
            if "residual_label" not in it: continue
            x = obs_to_tensor(it["obs"])
            y = torch.tensor(RES.index(it["residual_label"]), dtype=torch.long)
            ds.append((x,y))
    return ds

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=str, required=True)
    ap.add_argument("--epochs", type=int, default=10)
    ap.add_argument("--out", type=str, default="models/residual.pt")
    args = ap.parse_args()

    ds = load_jsonl(args.data); random.shuffle(ds)
    split = int(0.9*len(ds)); train, val = ds[:split], ds[split:]
    model = ResidualNet(); opt = optim.Adam(model.parameters(), lr=1e-3)
    crit = nn.CrossEntropyLoss()

    for ep in range(1, args.epochs+1):
        model.train(); tot=0.0
        for x,y in train:
            opt.zero_grad(); loss = crit(model(x).unsqueeze(0), y.unsqueeze(0))
            loss.backward(); opt.step(); tot+=loss.item()
        model.eval()
        with torch.no_grad():
            acc = sum( (model(x).argmax().item()==y.item()) for x,y in val )/max(1,len(val))
        print(f"epoch {ep} | loss {tot/len(train):.4f} | val_acc {acc:.3f}")
    Path("models").mkdir(exist_ok=True); torch.save(model.state_dict(), args.out)
    print("saved ->", args.out)

if __name__ == "__main__":
    main()
