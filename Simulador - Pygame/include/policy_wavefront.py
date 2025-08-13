# Simulador - Pygame/include/policy_wavefront.py
def cells_to_actions(cells):
    """
    Converte [(x0,y0),(x1,y1),...] em ações ['F','L','R',...]
    assumindo dir inicial = 0 (cima) como no teu Robo.
    """
    if not cells or len(cells) < 2:
        return []
    actions = []
    dir = 0  # 0=cima,1=dir,2=baixo,3=esq

    def turn_to(target_dir):
        nonlocal dir, actions
        while dir != target_dir:
            diff = (target_dir - dir) % 4
            if diff == 1:
                actions.append('R'); dir = (dir+1) % 4
            elif diff == 3:
                actions.append('L'); dir = (dir-1) % 4
            else:
                actions += ['R','R']; dir = (dir+2) % 4

    for (x0,y0),(x1,y1) in zip(cells[:-1], cells[1:]):
        dx, dy = x1-x0, y1-y0
        if   dx==0 and dy==-1: turn_to(0); actions.append('F')
        elif dx==1 and dy==0:  turn_to(1); actions.append('F')
        elif dx==0 and dy==1:  turn_to(2); actions.append('F')
        elif dx==-1 and dy==0: turn_to(3); actions.append('F')
        else:
            raise ValueError(f"Passo inválido {x0,y0}->{x1,y1}")
    return actions

def professor_policy(env):
    """Gera a sequência de ações do professor para o episódio atual."""
    cells = env.optimal_path_cells()
    return cells_to_actions(cells) if cells else []
