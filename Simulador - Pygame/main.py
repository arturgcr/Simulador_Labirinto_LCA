import pygame
import random
import networkx as nx
import os
import json

# Configurações do labirinto
LARGURA, ALTURA = 600, 600
LARGURA_INFO = 200  # Largura da interface lateral
LINHAS, COLUNAS = 60, 60  # Tamanho do labirinto
TAMANHO_CELULA = min(LARGURA // COLUNAS, ALTURA // LINHAS)  # Ajusta para caber perfeitamente

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
AZUL = (50, 100, 255)
VERMELHO = (255, 50, 50)
VERDE = (50, 255, 100)
CINZA = (200, 200, 200)
ROXO = (150, 50, 255)

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
        """ Gera um labirinto baseado em grafos usando o algoritmo escolhido """
        if self.algoritmo == 'prim':
            self._gerar_labirinto_prim()
        elif self.algoritmo == 'kruskal':
            self._gerar_labirinto_kruskal()

    def _gerar_labirinto_prim(self):
        """ Gera um labirinto usando o algoritmo de Prim """
        G = nx.grid_2d_graph(self.linhas, self.colunas)
        visitados = {self.inicio}
        arestas = [(self.inicio, vizinho) for vizinho in G.neighbors(self.inicio)]
        self.paredes = {(x, y, d) for x in range(self.linhas) for y in range(self.colunas) for d in ['R', 'D']}  # Paredes à direita e abaixo

        # Adiciona paredes ao redor do labirinto
        for x in range(self.linhas):
            self.paredes.add((x, 0, 'D'))  # Parede superior
            self.paredes.add((x, self.colunas - 1, 'D'))  # Parede inferior
        for y in range(self.colunas):
            self.paredes.add((0, y, 'R'))  # Parede esquerda
            self.paredes.add((self.linhas - 1, y, 'R'))  # Parede direita

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
                    self.paredes.discard((x1, min(y1, y2), 'D'))  # Remove parede inferior
                else:
                    self.paredes.discard((min(x1, x2), y1, 'R'))  # Remove parede direita
                for vizinho in G.neighbors(proximo_no):
                    if vizinho not in visitados:
                        arestas.append((proximo_no, vizinho))

    def _gerar_labirinto_kruskal(self):
        """ Gera um labirinto usando o algoritmo de Kruskal """
        # Implementação do algoritmo de Kruskal
        G = nx.grid_2d_graph(self.linhas, self.colunas)
        arestas = list(G.edges())
        random.shuffle(arestas)
        pai = {}
        rank = {}

        def encontrar(v):
            if pai[v] != v:
                pai[v] = encontrar(pai[v])
            return pai[v]

        def unir(v1, v2):
            raiz1 = encontrar(v1)
            raiz2 = encontrar(v2)
            if raiz1 != raiz2:
                if rank[raiz1] > rank[raiz2]:
                    pai[raiz2] = raiz1
                elif rank[raiz1] < rank[raiz2]:
                    pai[raiz1] = raiz2
                else:
                    pai[raiz2] = raiz1
                    rank[raiz1] += 1

        for no in G.nodes():
            pai[no] = no
            rank[no] = 0

        for aresta in arestas:
            u, v = aresta
            if encontrar(u) != encontrar(v):
                self.labirinto.add_edge(u, v)
                x1, y1 = u
                x2, y2 = v
                if x1 == x2:
                    self.paredes.discard((x1, min(y1, y2), 'D'))  # Remove parede inferior
                else:
                    self.paredes.discard((min(x1, x2), y1, 'R'))  # Remove parede direita
                unir(u, v)

    def resolver(self):
        """ Encontra o caminho da solução do labirinto usando Busca em Largura """
        try:
            return nx.shortest_path(self.labirinto, source=self.inicio, target=self.fim)
        except nx.NetworkXNoPath:
            return []

class Robo:
    def __init__(self, inicio):
        self.posicao = list(inicio)

    def mover(self, direcao, paredes):
        """ Move o robô na direção especificada se não houver parede """
        nova_pos = self.posicao.copy()
        if direcao == 'UP' and (self.posicao[0], min(self.posicao[1], nova_pos[1] - 1), 'D') not in paredes:
            nova_pos[1] -= 1
        elif direcao == 'DOWN' and (self.posicao[0], min(self.posicao[1], nova_pos[1] + 1), 'D') not in paredes:
            nova_pos[1] += 1
        elif direcao == 'LEFT' and (min(self.posicao[0], nova_pos[0] - 1), self.posicao[1], 'R') not in paredes:
            nova_pos[0] -= 1
        elif direcao == 'RIGHT' and (min(self.posicao[0], nova_pos[0] + 1), self.posicao[1], 'R') not in paredes:
            nova_pos[0] += 1
        
        self.posicao = nova_pos

class SimuladorLabirinto:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA + LARGURA_INFO, ALTURA))
        self.relogio = pygame.time.Clock()
        self.algoritmo = 'prim'  # Algoritmo padrão
        self.labirinto = Labirinto(LINHAS, COLUNAS, self.algoritmo)
        self.robo = Robo(self.labirinto.inicio)
        self.caminho_solucao = self.labirinto.resolver()
        self.mostrar_caminho = False

    def salvar_labirinto(self):
        """ Salva o labirinto em um arquivo JSON """
        dados_labirinto = {
            'linhas': self.labirinto.linhas,
            'colunas': self.labirinto.colunas,
            'paredes': list(self.labirinto.paredes),
            'inicio': self.labirinto.inicio,
            'fim': self.labirinto.fim
        }
        try:
            if not os.path.exists('data'):
                os.makedirs('data')
            arquivos_existentes = [f for f in os.listdir('data') if f.startswith('maze') and f.endswith('.json')]
            novo_arquivo = f"maze{len(arquivos_existentes) + 1}.json"
            with open(os.path.join('data', novo_arquivo), 'w') as file:
                json.dump(dados_labirinto, file)
        except:
            print("Falha ao salvar o labirinto")

    def carregar_labirinto(self):
        """ Carrega o labirinto de um arquivo JSON """
        try:
            arquivos_existentes = [f for f in os.listdir('data') if f.startswith('maze') and f.endswith('.json')]
            if arquivos_existentes:
                ultimo_arquivo = sorted(arquivos_existentes)[-1]
                with open(os.path.join('data', ultimo_arquivo), 'r') as file:
                    dados_labirinto = json.load(file)
                    self.labirinto = Labirinto(dados_labirinto['linhas'], dados_labirinto['colunas'])
                    self.labirinto.paredes = set(tuple(parede) for parede in dados_labirinto['paredes'])
                    self.labirinto.inicio = tuple(dados_labirinto['inicio'])
                    self.labirinto.fim = tuple(dados_labirinto['fim'])
                    self.robo = Robo(self.labirinto.inicio)
                    self.caminho_solucao = self.labirinto.resolver()
        except:
            print("Falha ao carregar o arquivo")

    def desenhar_labirinto(self):
        """ Desenha o labirinto e a interface do usuário """
        self.tela.fill(BRANCO)
        for x, y, direcao in self.labirinto.paredes:
            if direcao == 'R':
                pygame.draw.line(self.tela, PRETO, ((x + 1) * TAMANHO_CELULA, y * TAMANHO_CELULA), 
                                 ((x + 1) * TAMANHO_CELULA, (y + 1) * TAMANHO_CELULA), 3)
            else:
                pygame.draw.line(self.tela, PRETO, (x * TAMANHO_CELULA, (y + 1) * TAMANHO_CELULA), 
                                 ((x + 1) * TAMANHO_CELULA, (y + 1) * TAMANHO_CELULA), 3)

        # Desenhar o robô e o caminho
        pygame.draw.rect(self.tela, AZUL, (self.labirinto.inicio[0] * TAMANHO_CELULA, self.labirinto.inicio[1] * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA))
        pygame.draw.rect(self.tela, VERMELHO, (self.labirinto.fim[0] * TAMANHO_CELULA, self.labirinto.fim[1] * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA))
        pygame.draw.circle(self.tela, VERDE, (self.robo.posicao[0] * TAMANHO_CELULA + TAMANHO_CELULA // 2, self.robo.posicao[1] * TAMANHO_CELULA + TAMANHO_CELULA // 2), TAMANHO_CELULA // 3)
        
        if self.mostrar_caminho:
            for x, y in self.caminho_solucao:
                pygame.draw.rect(self.tela, ROXO, (x * TAMANHO_CELULA + TAMANHO_CELULA // 4, y * TAMANHO_CELULA + TAMANHO_CELULA // 4, TAMANHO_CELULA // 2, TAMANHO_CELULA // 2))

        pygame.draw.rect(self.tela, CINZA, (LARGURA, 0, LARGURA_INFO, ALTURA))

        # Desenho dos botões na interface
        fonte = pygame.font.Font(None, 36)
        fonte_botao = pygame.font.Font(None, 28)
        texto1 = fonte.render(f"Algoritmo: {self.algoritmo}", True, PRETO)
        self.tela.blit(texto1, (LARGURA + 10, 10))
        
        # Botão para mostrar o caminho
        botao_mostrar_caminho = pygame.draw.rect(self.tela, AZUL, (LARGURA + 10, 50, LARGURA_INFO - 20, 40))
        texto_mostrar_caminho = fonte_botao.render("Mostrar Caminho", True, BRANCO)
        self.tela.blit(texto_mostrar_caminho, (LARGURA + 20, 55))

        # Botão para salvar o labirinto
        botao_salvar_labirinto = pygame.draw.rect(self.tela, AZUL, (LARGURA + 10, 100, LARGURA_INFO - 20, 40))
        texto_salvar_labirinto = fonte_botao.render("Salvar Labirinto", True, BRANCO)
        self.tela.blit(texto_salvar_labirinto, (LARGURA + 20, 105))

        # Botão para carregar o labirinto
        botao_carregar_labirinto = pygame.draw.rect(self.tela, AZUL, (LARGURA + 10, 150, LARGURA_INFO - 20, 40))
        texto_carregar_labirinto = fonte_botao.render("Carregar Labirinto", True, BRANCO)
        self.tela.blit(texto_carregar_labirinto, (LARGURA + 20, 155))

        return botao_mostrar_caminho, botao_salvar_labirinto, botao_carregar_labirinto

    def executar(self):
        """ Executa o loop principal do jogo """
        rodando = True
        while rodando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    rodando = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_UP or evento.key == pygame.K_w:
                        self.robo.mover('UP', self.labirinto.paredes)
                    elif evento.key == pygame.K_DOWN or evento.key == pygame.K_s:
                        self.robo.mover('DOWN', self.labirinto.paredes)
                    elif evento.key == pygame.K_LEFT or evento.key == pygame.K_a:
                        self.robo.mover('LEFT', self.labirinto.paredes)
                    elif evento.key == pygame.K_RIGHT or evento.key == pygame.K_d:
                        self.robo.mover('RIGHT', self.labirinto.paredes)

                # Detectando clique de botão
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    pos_mouse = pygame.mouse.get_pos()
                    botao_mostrar_caminho, botao_salvar_labirinto, botao_carregar_labirinto = self.desenhar_labirinto()
                    if botao_mostrar_caminho.collidepoint(pos_mouse):
                        self.mostrar_caminho = not self.mostrar_caminho
                    if botao_salvar_labirinto.collidepoint(pos_mouse):
                        self.salvar_labirinto()
                    if botao_carregar_labirinto.collidepoint(pos_mouse):
                        self.carregar_labirinto()

            self.desenhar_labirinto()
            pygame.display.flip()
            self.relogio.tick(60)

        pygame.quit()

if __name__ == "__main__":
    jogo = SimuladorLabirinto()
    jogo.executar()