import pygame
import random
import networkx as nx
import os
import json
import time

# Configurações do labirinto
LARGURA, ALTURA = 600, 600
LARGURA_INFO = 200  # Largura da interface lateral
LINHAS, COLUNAS = 50, 50
TAMANHO_CELULA = min(LARGURA // COLUNAS, ALTURA // LINHAS)

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
AZUL = (50, 100, 255)
VERMELHO = (255, 50, 50)
VERDE = (50, 255, 100)
CINZA = (200, 200, 200)
ROXO = (150, 50, 255)
AMARELO = (255, 255, 0)

# Algoritmos de busca disponíveis
ALGORITMOS_BUSCA = ['BFS', 'DFS', 'A*']

class Labirinto:
    def __init__(self, linhas, colunas):
        self.linhas = linhas
        self.colunas = colunas
        self.paredes = set()
        self.labirinto = nx.Graph()
        self.inicio = (0, 0)
        self.fim = (colunas - 1, linhas - 1)
        self.gerar_labirinto()

    def gerar_labirinto(self):
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
    
    def resolver(self, metodo='BFS'):
        visitados = set()
        fila = [(self.inicio, [self.inicio])]
        
        while fila:
            posicao, caminho = fila.pop(0 if metodo == 'BFS' else -1)
            visitados.add(posicao)
            if posicao == self.fim:
                return caminho, visitados
            for vizinho in self.labirinto.neighbors(posicao):
                if vizinho not in visitados:
                    fila.append((vizinho, caminho + [vizinho]))
        return [], visitados

class SimuladorLabirinto:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA + LARGURA_INFO, ALTURA))
        pygame.display.set_caption("Simulador de Labirinto")
        self.relogio = pygame.time.Clock()
        self.labirinto = Labirinto(LINHAS, COLUNAS)
        self.algoritmo = 'BFS'
        self.caminho_solucao, self.visitados = self.labirinto.resolver(self.algoritmo)
        self.executando = False
        self.passo = 0
    
    def desenhar_labirinto(self):
        self.tela.fill(BRANCO)
        for x, y, d in self.labirinto.paredes:
            if d == 'R':
                pygame.draw.line(self.tela, PRETO, (y * TAMANHO_CELULA + TAMANHO_CELULA, x * TAMANHO_CELULA),
                                 (y * TAMANHO_CELULA + TAMANHO_CELULA, x * TAMANHO_CELULA + TAMANHO_CELULA), 2)
            else:
                pygame.draw.line(self.tela, PRETO, (y * TAMANHO_CELULA, x * TAMANHO_CELULA + TAMANHO_CELULA),
                                 (y * TAMANHO_CELULA + TAMANHO_CELULA, x * TAMANHO_CELULA + TAMANHO_CELULA), 2)
        for pos in self.visitados:
            pygame.draw.rect(self.tela, AMARELO, (pos[1] * TAMANHO_CELULA, pos[0] * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA))
        for i in range(min(self.passo, len(self.caminho_solucao))):
            pygame.draw.rect(self.tela, AZUL, (self.caminho_solucao[i][1] * TAMANHO_CELULA, self.caminho_solucao[i][0] * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA))
        pygame.draw.rect(self.tela, VERDE, (self.labirinto.inicio[1] * TAMANHO_CELULA, self.labirinto.inicio[0] * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA))
        pygame.draw.rect(self.tela, VERMELHO, (self.labirinto.fim[1] * TAMANHO_CELULA, self.labirinto.fim[0] * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA))
        pygame.draw.rect(self.tela, PRETO, (LARGURA, 0, LARGURA_INFO, ALTURA))
        font = pygame.font.Font(None, 24)
        for i, algoritmo in enumerate(ALGORITMOS_BUSCA):
            cor = BRANCO if algoritmo == self.algoritmo else CINZA
            pygame.draw.rect(self.tela, cor, (LARGURA + 20, 100 + i * 40, 160, 30))
            texto = font.render(algoritmo, True, PRETO)
            self.tela.blit(texto, (LARGURA + 40, 110 + i * 40))
        pygame.display.flip()
    
    def executar(self):
        rodando = True
        while rodando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    rodando = False
                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    if x > LARGURA:
                        indice = (y - 100) // 40
                        if 0 <= indice < len(ALGORITMOS_BUSCA):
                            self.algoritmo = ALGORITMOS_BUSCA[indice]
                            self.caminho_solucao, self.visitados = self.labirinto.resolver(self.algoritmo)
                            self.passo = 0
                            self.executando = True
            if self.executando and self.passo < len(self.caminho_solucao):
                self.passo += 1
            self.desenhar_labirinto()
            self.relogio.tick(10)
        pygame.quit()

SimuladorLabirinto().executar()
