# Simulador - Pygame/include/policy_residual.py
import torch
from .policy_wavefront import professor_policy, cells_to_actions
from .env import ACTIONS

RES = ['KEEP','LEFT','RIGHT','BACK']

class ResidualPolicy:
    def __init__(self, residual_model_path):
        from scripts.train_residual import ResidualNet, obs_to_tensor  # reuse
        self.model = ResidualNet(); self.model.load_state_dict(torch.load(residual_model_path, map_location='cpu'))
        self.model.eval()
        self.obs_to_tensor = obs_to_tensor

    def decide(self, obs, professor_action):
        x = self.obs_to_tensor(obs)
        with torch.no_grad():
            r = self.model(x).argmax().item()
        res = RES[r]
        if res == 'KEEP':
            return professor_action
        if res == 'LEFT':  return 'L'
        if res == 'RIGHT': return 'R'
        if res == 'BACK':  return 'B'
        return professor_action
