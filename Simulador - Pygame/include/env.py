# Simulador - Pygame/include/env.py
"""
MazeEnv: wrapper minimalista tipo Gym para o seu simulador.

Uso:
    from include.env import MazeEnv
    env = MazeEnv(linhas=15, colunas=15, gerador='prim', seed=123)
    obs = env.reset()
    obs, reward, done, info = env.step('F')  # 'F','B','L','R'
"""
import random, time
import networkx as nx
from .labirinto import Labirinto
from .robo import Robo

ACTIONS = ['F', 'B', 'L', 'R']

class MazeEnv:
    def __init__(self, linhas=15, colunas=15, gerador='prim', seed=None,
                 slip_p=0.05, turn_error_p=0.0):
        self.linhas = linhas
        self.colunas = colunas
        self.gerador = gerador
        self.seed = seed
        self.rng = random.Random(seed)
        self.slip_p = slip_p          # prob. de ignorar ação/mudar ação
        self.turn_error_p = turn_error_p  # prob. de inverter L<->R
        self._lab = None
        self._robo = None
        self._max_steps = 10 * (linhas * colunas)
        self._steps = 0
        self._last_action = None
        self._collisions = 0

    def _new_start_goal(self):
        while True:
            sx, sy = self.rng.randrange(self.colunas), self.rng.randrange(self.linhas)
            gx, gy = self.rng.randrange(self.colunas), self.rng.randrange(self.linhas)
            if (sx, sy) != (gx, gy):
                return (sx, sy), (gx, gy)

    def reset(self, start=None, goal=None):
        if self.seed is not None:
            random.seed(self.seed)
        self._lab = Labirinto(self.linhas, self.colunas, algoritmo=self.gerador)
        if start is None or goal is None:
            start, goal = self._new_start_goal()
        # teu Labirinto não tem setter; ajusta direto:
        self._lab.inicio = start
        self._lab.fim = goal
        self._robo = Robo(self._lab.inicio, self._lab)
        self._steps = 0
        self._collisions = 0
        self._last_action = None
        self._sense()  # primeira leitura
        return self._obs()

    def _sense(self):
        # atualiza 'deteccoes' no Robo
        if hasattr(self._robo, 'detectar_paredes'):
            self._robo.detectar_paredes()

    def step(self, action):
        assert action in ACTIONS
        t0 = time.perf_counter()

        # --- aplica ruído simples ---
        a = action
        if a in ['L', 'R'] and self.rng.random() < self.turn_error_p:
            a = 'L' if a == 'R' else 'R'
        if self.rng.random() < self.slip_p:
            a = self.rng.choice(ACTIONS)

        # colisão é “intenção de ir pra frente com parede à frente”
        self._sense()
        pre_front_blocked = bool(getattr(self._robo, 'deteccoes', {}).get('frente', False))
        if a == 'F' and pre_front_blocked:
            self._collisions += 1

        # executa
        self._robo.mover(a)
        self._sense()

        done = (tuple(self._robo.posicao) == tuple(self._lab.fim))
        self._steps += 1
        if self._steps >= self._max_steps:
            done = True

        # recompensa simples: -1/step, +100 no goal, penaliza giro
        reward = -1.0 + (100.0 if done else 0.0) + (-0.1 if a in ['L','R'] else 0.0)

        latency_ms = (time.perf_counter() - t0) * 1000.0
        info = {
            "pos": tuple(self._robo.posicao),
            "dir": int(self._robo.direcao),
            "goal": tuple(self._lab.fim),
            "collisions": self._collisions,
            "latency_ms": latency_ms,
            "action_used": a,
            "action_intended": action
        }
        self._last_action = a
        return self._obs(), reward, done, info

    def _obs(self):
        det = getattr(self._robo, 'deteccoes', {})
        return {
            "wall_front": bool(det.get('frente', False)),
            "wall_left": bool(det.get('esquerda', False)),
            "wall_right": bool(det.get('direita', False)),
            "x": int(self._robo.posicao[0]),
            "y": int(self._robo.posicao[1]),
            "dir": int(self._robo.direcao),
            "goal_x": int(self._lab.fim[0]),
            "goal_y": int(self._lab.fim[1]),
        }

    # utilidades para métricas
    def optimal_path_cells(self):
        try:
            g = self._lab.labirinto  # networkx.Graph
            return list(nx.shortest_path(g, source=tuple(self._lab.inicio), target=tuple(self._lab.fim)))
        except Exception:
            return []

    def optimal_cost(self):
        try:
            g = self._lab.labirinto
            return nx.shortest_path_length(g, source=tuple(self._lab.inicio), target=tuple(self._lab.fim))
        except Exception:
            return None
