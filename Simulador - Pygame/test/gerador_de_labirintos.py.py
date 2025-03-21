import tkinter as tk
import random

# Configurações do labirinto
GRID_SIZE = 10
CELL_SIZE = 40

# Direções (cima, direita, baixo, esquerda)
DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]

class Maze:
    def __init__(self, size):
        self.size = size
        self.grid = [[1] * size for _ in range(size)]
        self.generate_maze()

    def generate_maze(self):
        """Gera o labirinto usando DFS."""
        visited = [[False] * self.size for _ in range(self.size)]

        def dfs(x, y):
            visited[y][x] = True
            self.grid[y][x] = 0
            random.shuffle(DIRECTIONS)
            for dx, dy in DIRECTIONS:
                nx, ny = x + dx * 2, y + dy * 2
                if 0 <= nx < self.size and 0 <= ny < self.size and not visited[ny][nx]:
                    self.grid[y + dy][x + dx] = 0
                    dfs(nx, ny)

        dfs(0, 0)  # Começa no canto superior esquerdo

    def is_wall(self, x, y):
        return self.grid[y][x] == 1 if 0 <= x < self.size and 0 <= y < self.size else True

class Micromouse:
    def __init__(self, canvas, maze):
        self.canvas = canvas
        self.maze = maze
        self.x, self.y = 0, 0
        self.rect = canvas.create_oval(5, 5, CELL_SIZE-5, CELL_SIZE-5, fill="blue")
        self.update_position()

    def move(self, dx, dy):
        """Move o robô se não houver parede."""
        new_x, new_y = self.x + dx, self.y + dy
        if not self.maze.is_wall(new_x, new_y):
            self.x, self.y = new_x, new_y
            self.update_position()

    def update_position(self):
        """Atualiza a posição do robô na tela."""
        self.canvas.coords(
            self.rect,
            self.x * CELL_SIZE + 5,
            self.y * CELL_SIZE + 5,
            (self.x + 1) * CELL_SIZE - 5,
            (self.y + 1) * CELL_SIZE - 5
        )

class MicromouseSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Micromouse Simulator")
        self.canvas = tk.Canvas(root, width=GRID_SIZE * CELL_SIZE, height=GRID_SIZE * CELL_SIZE, bg="white")
        self.canvas.pack()

        self.maze = Maze(GRID_SIZE)
        self.draw_maze()
        self.micromouse = Micromouse(self.canvas, self.maze)

        # Mapeia as teclas para movimento
        self.root.bind("<Up>", lambda _: self.micromouse.move(0, -1))
        self.root.bind("<Down>", lambda _: self.micromouse.move(0, 1))
        self.root.bind("<Left>", lambda _: self.micromouse.move(-1, 0))
        self.root.bind("<Right>", lambda _: self.micromouse.move(1, 0))

    def draw_maze(self):
        """Desenha o labirinto na tela."""
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if self.maze.grid[y][x] == 1:
                    self.canvas.create_rectangle(
                        x * CELL_SIZE, y * CELL_SIZE, 
                        (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                        fill="black"
                    )

if __name__ == "__main__":
    root = tk.Tk()
    app = MicromouseSimulator(root)
    root.mainloop()
