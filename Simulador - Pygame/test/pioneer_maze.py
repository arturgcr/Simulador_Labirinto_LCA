import pygame
import sys
import math
import random

# Inicializa o pygame
pygame.init()

# Definições de cores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Tamanho da tela e dos quadrados
SCREEN_WIDTH, SCREEN_HEIGHT = 700, 700  # Tamanho da tela
CELL_SIZE = 100  # Tamanho dos quadrados (100px x 100px)

# Definindo a tela
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simulador Pioneer 3DX")
SCALE_FACTOR = 0.1

# Medidas do robô Pioneer 3DX (em mm)
ROBOT_LENGTH = 455  # comprimento
ROBOT_WIDTH = 381   # largura

# Posição inicial do robô
player_x, player_y = 0, 0
angle = 0  # Ângulo inicial do robô (em radianos)

# Ângulo do cone de visão para cada sensor
FOV_ANGLE = math.radians(15)  # 15 graus para cada sensor
FOV_LENGTH = 3500 * SCALE_FACTOR  # Comprimento do cone de visão

# Função para desenhar a grade
def draw_grid():
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, WHITE, rect, 1)

# Função para desenhar a seta na frente do robô
def draw_arrow(x, y, angle):
    arrow_length = 30 * SCALE_FACTOR
    arrow_width = 10 * SCALE_FACTOR

    # Posição do robô
    center_x = x * CELL_SIZE + CELL_SIZE / 2
    center_y = y * CELL_SIZE + CELL_SIZE / 2

    # Calcula os pontos da seta
    point1 = (
        center_x + arrow_length * math.cos(angle),
        center_y + arrow_length * math.sin(angle)
    )
    
    point2 = (
        point1[0] - arrow_width * math.sin(angle),
        point1[1] + arrow_width * math.cos(angle)
    )

    point3 = (
        point1[0] + arrow_width * math.sin(angle),
        point1[1] - arrow_width * math.cos(angle)
    )

    # Desenha a seta
    pygame.draw.polygon(screen, GREEN, [point1, point2, point3])

# Função para desenhar o robô Pioneer 3DX
def draw_robot(x, y, angle):
    # Desenhar o corpo retangular do robô
    robot_rect = pygame.Rect(
        x * CELL_SIZE + (CELL_SIZE - ROBOT_LENGTH * SCALE_FACTOR) // 2,
        y * CELL_SIZE + (CELL_SIZE - ROBOT_WIDTH * SCALE_FACTOR) // 2,
        ROBOT_LENGTH * SCALE_FACTOR,
        ROBOT_WIDTH * SCALE_FACTOR
    )

    # Cria uma superfície para o robô e aplica a rotação
    robot_image = pygame.Surface((ROBOT_LENGTH * SCALE_FACTOR, ROBOT_WIDTH * SCALE_FACTOR), pygame.SRCALPHA)
    pygame.draw.rect(robot_image, RED, (0, 0, ROBOT_LENGTH * SCALE_FACTOR, ROBOT_WIDTH * SCALE_FACTOR), border_radius=15)
    robot_image = pygame.transform.rotate(robot_image, -math.degrees(angle))
    robot_rect = robot_image.get_rect(center=(x * CELL_SIZE + CELL_SIZE / 2, y * CELL_SIZE + CELL_SIZE / 2))

    # Desenha o corpo do robô
    screen.blit(robot_image, robot_rect.topleft)

    # Calcula as posições das pontas do robô
    front_x = robot_rect.centerx + (ROBOT_LENGTH * SCALE_FACTOR / 2) * math.cos(angle)
    front_y = robot_rect.centery + (ROBOT_LENGTH * SCALE_FACTOR / 2) * math.sin(angle)

    back_x = robot_rect.centerx - (ROBOT_LENGTH * SCALE_FACTOR / 2) * math.cos(angle)
    back_y = robot_rect.centery - (ROBOT_LENGTH * SCALE_FACTOR / 2) * math.sin(angle)

    # Desenha os cones de visão dos sensores nas pontas do robô
    for offset in [-90, -50, -30, -10, 10, 30, 50, 90]:  # Ângulos para os sensores
        sensor_angle = angle + math.radians(offset)

        # Ponto do cone de visão
        left_point = (
            front_x + FOV_LENGTH * math.cos(sensor_angle - FOV_ANGLE / 2),
            front_y + FOV_LENGTH * math.sin(sensor_angle - FOV_ANGLE / 2)
        )

        right_point = (
            front_x + FOV_LENGTH * math.cos(sensor_angle + FOV_ANGLE / 2),
            front_y + FOV_LENGTH * math.sin(sensor_angle + FOV_ANGLE / 2)
        )

        # Desenha o cone de visão
        pygame.draw.polygon(screen, GREEN, [(front_x, front_y), left_point, right_point], 1)

# Funções para desenhar as paredes do labirinto
def draw_walls(grid):
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell.bottom != 1:
                draw_bottom(x, y, WHITE)
            if cell.right != 1:
                draw_right(x, y, WHITE)

def draw_bottom(x, y, color):
    pygame.draw.rect(screen, color, pygame.Rect(x * CELL_SIZE, (y + 1) * CELL_SIZE, CELL_SIZE, 1))

def draw_right(x, y, color):
    pygame.draw.rect(screen, color, pygame.Rect((x + 1) * CELL_SIZE, y * CELL_SIZE, 1, CELL_SIZE))

# Gerador de labirinto
class NODE:
    def __init__(self):
        self.set = '0'
        self.left = None
        self.right = None
        self.top = None
        self.bottom = None

    def __str__(self):
        return str(self.set)

def create_edge_list(width, height):
    edge_list = []
    for y in range(height):
        for x in range(width):
            if x > 0:
                edge_list.append(((x - 1, y), (x, y)))
            if y > 0:
                edge_list.append(((x, y - 1), (x, y)))
    return edge_list

def generate_maze(width, height):
    grid = [[NODE() for _ in range(width)] for _ in range(height)]
    edge_list = create_edge_list(width, height)
    random.shuffle(edge_list)

    for edge_a, edge_b in edge_list:
        # Simplificação: vamos remover aleatoriamente algumas paredes
        if random.choice([True, False]):
            if edge_a[0] == edge_b[0]:  # mesma coluna
                grid[edge_a[1]][edge_a[0]].bottom = 1
            else:  # mesma linha
                grid[edge_a[1]][edge_a[0]].right = 1

    return grid

# Labirinto 7x7
maze = generate_maze(7, 7)

# Loop principal
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Movimentação do robô com as setas do teclado
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                angle -= math.radians(90)  # Gira para a esquerda
            if event.key == pygame.K_RIGHT:
                angle += math.radians(90)  # Gira para a direita
            if event.key == pygame.K_UP:
                new_x = player_x + int(math.cos(angle))  # Move para frente
                new_y = player_y + int(math.sin(angle))  # Move para frente
                # Verifica se a nova posição está dentro da tela
                if 0 <= new_x < 7 and 0 <= new_y < 7:
                    player_x, player_y = new_x, new_y
            if event.key == pygame.K_DOWN:
                new_x = player_x - int(math.cos(angle))  # Move para trás
                new_y = player_y - int(math.sin(angle))  # Move para trás
                # Verifica se a nova posição está dentro da tela
                if 0 <= new_x < 7 and 0 <= new_y < 7:
                    player_x, player_y = new_x, new_y

    # Preenche a tela com a cor preta
    screen.fill(BLACK)

    # Desenha a grade, o labirinto, o robô Pioneer 3DX e a seta
    draw_grid()
    draw_walls(maze)
    draw_robot(player_x, player_y, angle)
    draw_arrow(player_x, player_y, angle)

    # Atualiza a tela
    pygame.display.flip()
