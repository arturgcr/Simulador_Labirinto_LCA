import pygame
import random
import networkx as nx

# Configurações do labirinto
WIDTH, HEIGHT = 600, 600
INFO_WIDTH = 320  # Largura da interface lateral
ROWS, COLS = 20, 20  # Tamanho do labirinto
CELL_SIZE = min(WIDTH // COLS, HEIGHT // ROWS)  # Ajusta para caber perfeitamente

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)

def generate_maze(rows, cols, seed=None):
    """ Gera um labirinto baseado em grafos, onde as células são espaços e os limites entre elas são paredes."""
    if seed:
        random.seed(seed)
    else:
        seed = random.randint(0, 999999)
    
    G = nx.grid_2d_graph(rows, cols)
    maze = nx.Graph()
    start = (0, 0)
    visited = {start}
    edges = [(start, neighbor) for neighbor in G.neighbors(start)]
    walls = {(x, y, d) for x in range(rows) for y in range(cols) for d in ['R', 'D']}  # Paredes à direita e abaixo
    
    while edges:
        edge = random.choice(edges)
        edges.remove(edge)
        node, next_node = edge
        if next_node not in visited:
            visited.add(next_node)
            maze.add_edge(node, next_node)
            x1, y1 = node
            x2, y2 = next_node
            if x1 == x2:
                walls.discard((x1, min(y1, y2), 'D'))  # Remove parede inferior
            else:
                walls.discard((min(x1, x2), y1, 'R'))  # Remove parede direita
            for neighbor in G.neighbors(next_node):
                if neighbor not in visited:
                    edges.append((next_node, neighbor))
    
    return maze, walls, seed

def get_walls_binary(x, y, walls):
    """ Retorna um número binário indicando a presença de paredes ao redor."""
    return f"L: {1 if (x - 1, y, 'R') not in walls else 0}, " \
           f"R: {1 if (x, y, 'R') not in walls else 0}, " \
           f"U: {1 if (x, y - 1, 'D') not in walls else 0}, " \
           f"D: {1 if (x, y, 'D') not in walls else 0}"

def draw_maze(screen, walls, start, end, player_pos, seed):
    screen.fill(WHITE)
    for x, y, direction in walls:
        if direction == 'R':  # Parede à direita
            pygame.draw.line(screen, BLACK, ((x + 1) * CELL_SIZE, y * CELL_SIZE), 
                             ((x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE), 5)
        else:  # Parede inferior
            pygame.draw.line(screen, BLACK, (x * CELL_SIZE, (y + 1) * CELL_SIZE), 
                             ((x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE), 5)
    pygame.draw.rect(screen, BLUE, (start[0] * CELL_SIZE, start[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, RED, (end[0] * CELL_SIZE, end[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.draw.circle(screen, GREEN, (player_pos[0] * CELL_SIZE + CELL_SIZE // 2, player_pos[1] * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)
    
    pygame.draw.rect(screen, GRAY, (WIDTH, 0, INFO_WIDTH, HEIGHT))
    font = pygame.font.Font(None, 36)
    text1 = font.render(f"Pos: {player_pos}", True, BLACK)
    text2 = font.render(f"Walls: {get_walls_binary(*player_pos, walls)}", True, BLACK)
    text3 = font.render(f"Seed: {seed}", True, BLACK)
    button = pygame.Rect(WIDTH + 20, 100, 160, 50)
    pygame.draw.rect(screen, BLUE, button)
    button_text = font.render("Salvar Seed", True, WHITE)
    screen.blit(text1, (WIDTH + 10, 10))
    screen.blit(text2, (WIDTH + 10, 40))
    screen.blit(text3, (WIDTH + 10, 70))
    screen.blit(button_text, (WIDTH + 30, 110))
    return button

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH + INFO_WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    
    maze, walls, seed = generate_maze(ROWS, COLS)
    start = (0, 0)
    end = (COLS - 1, ROWS - 1)
    player_pos = list(start)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                x, y = player_pos
                new_pos = list(player_pos)
                if event.key == pygame.K_UP and (x, y - 1, 'D') not in walls and y > 0:
                    new_pos[1] -= 1
                elif event.key == pygame.K_DOWN and (x, y, 'D') not in walls and y < ROWS - 1:
                    new_pos[1] += 1
                elif event.key == pygame.K_LEFT and (x - 1, y, 'R') not in walls and x > 0:
                    new_pos[0] -= 1
                elif event.key == pygame.K_RIGHT and (x, y, 'R') not in walls and x < COLS - 1:
                    new_pos[0] += 1
                player_pos = new_pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and button.collidepoint(event.pos):
                    with open("saved_seed.txt", "w") as file:
                        file.write(str(seed))
                    print(f"Seed salva: {seed}")
        
        button = draw_maze(screen, walls, start, end, player_pos, seed)
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()