import pygame
import random
import networkx as nx
import os
import json
import time

# Configurações do labirinto
LARGURA, ALTURA = 600, 600
LARGURA_INFO = 200  # Largura da interface lateral
LINHAS, COLUNAS = 20, 20  # Tamanho do labirinto
TAMANHO_CELULA = min(LARGURA // COLUNAS, ALTURA // LINHAS)  # Ajusta para caber perfeitamente

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
AZUL = (50, 100, 255)
VERMELHO = (255, 50, 50)    
VERDE = (50, 255, 100)
CINZA = (200, 200, 200)
ROXO = (150, 50, 255)
AMARELO = (255, 255, 0)  # Cor para células visitadas

class Labirinto:
    def __init__(self, linhas, colunas, algoritmo='prim'):
        self.linhas = linhas
        self.colunas = colunas
        self.algoritmo = algoritmo
        self.paredes = set()
        self.labirinto = nx.Graph()
        self.inicio = (0, 0)
        self.fim = (colunas - 1, linhas - 1)
        self.gerar_labirinto()

    def gerar_labirinto(self):
        if self.algoritmo == 'prim':
            self._gerar_labirinto_prim()
        elif self.algoritmo == 'kruskal':
            self._gerar_labirinto_kruskal()

    def _gerar_labirinto_prim(self):
        G = nx.grid_2d_graph(self.linhas, self.colunas)
        visitados = {self.inicio}
        arestas = [(self.inicio, vizinho) for vizinho in G.neighbors(self.inicio)]
        self.paredes = {(x, y, d) for x in range(self.linhas) for y in range(self.colunas) for d in ['R', 'D']}

        while arestas:
            aresta = random.choice(arestas)
            arestas.remove(aresta)
            no, proximo_no = aresta
            if proximo_no not in visitados:
                visitados.add(proximo_no)
                self.labirinto.add_edge(no, proximo_no)
                x1, y1 = no
                x2, y2 = proximo_no
                if x1 == x2:
                    self.paredes.discard((x1, min(y1, y2), 'D'))
                else:
                    self.paredes.discard((min(x1, x2), y1, 'R'))
                for vizinho in G.neighbors(proximo_no):
                    if vizinho not in visitados:
                        arestas.append((proximo_no, vizinho))

    def resolver(self):
        try:
            return nx.shortest_path(self.labirinto, source=self.inicio, target=self.fim)
        except nx.NetworkXNoPath:
            return []

class SimuladorLabirinto:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA + LARGURA_INFO, ALTURA))
        self.relogio = pygame.time.Clock()
        self.labirinto = Labirinto(LINHAS, COLUNAS, 'prim')
        self.caminho_solucao = self.labirinto.resolver()
        self.visitados = []
        self.executando = True

    def executar(self):
        for celula in self.caminho_solucao:
            if not self.executando:
                break
            self.visitados.append(celula)
            self.atualizar_tela()
            time.sleep(0.1)
        while self.executando:
            self.atualizar_tela()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.executando = False

    def atualizar_tela(self):
        self.tela.fill(BRANCO)
        for x in range(LINHAS):
            for y in range(COLUNAS):
                cor = BRANCO
                if (x, y) in self.visitados:
                    cor = AMARELO
                pygame.draw.rect(self.tela, cor, (y * TAMANHO_CELULA, x * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA))
                pygame.draw.rect(self.tela, PRETO, (y * TAMANHO_CELULA, x * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA), 1)
        pygame.display.flip()
        self.relogio.tick(30)

if __name__ == "__main__":
    simulador = SimuladorLabirinto()
    simulador.executar()
    pygame.quit()
