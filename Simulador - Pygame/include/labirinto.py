"""
labirinto.py - Módulo para geração e manipulação de labirintos

Implementa dois algoritmos para geração de labirintos:
1. Algoritmo de Prim - Cria labirintos com muitos caminhos curtos
2. Algoritmo de Kruskal - Cria labirintos com menos dead-ends

Também inclui funcionalidades para:
- Resolução automática do labirinto
- Salvamento e carregamento de labirintos em arquivos JSON
"""

import random
import networkx as nx
import json

class Labirinto:
    def __init__(self, linhas, colunas, algoritmo='prim'):
        """
        Inicializa um novo labirinto
        
        Args:
            linhas (int): Número de linhas do labirinto
            colunas (int): Número de colunas do labirinto
            algoritmo (str): 'prim' ou 'kruskal' (algoritmo de geração)
        """
        self.linhas = linhas
        self.colunas = colunas
        self.algoritmo = algoritmo
        self.paredes = set()  # Conjunto de paredes (x, y, direção)
        self.labirinto = nx.Graph()  # Grafo representando os caminhos
        self.inicio = (0, 0)  # Ponto de início
        self.fim = (colunas - 1, linhas - 1)  # Ponto de destino
        
        # Gera o labirinto automaticamente na criação
        self.gerar_labirinto()

    # =============================================
    # MÉTODOS PÚBLICOS
    # =============================================

    def gerar_labirinto(self):
        """
        Gera o labirinto usando o algoritmo especificado
        
        Chama o método apropriado baseado no algoritmo selecionado
        """
        if self.algoritmo == 'prim':
            self._gerar_labirinto_prim()
        elif self.algoritmo == 'kruskal':
            self._gerar_labirinto_kruskal()

    def resolver(self):
        """
        Resolve o labirinto encontrando o caminho mais curto do início ao fim
        
        Returns:
            list: Lista de coordenadas (x,y) representando o caminho ou lista vazia se não houver solução
        """
        try:
            return nx.shortest_path(self.labirinto, source=self.inicio, target=self.fim)
        except nx.NetworkXNoPath:
            return []

    def salvar_para_arquivo(self, nome_arquivo):
        """
        Salva o labirinto em um arquivo JSON
        
        Args:
            nome_arquivo (str): Caminho do arquivo para salvar
        """
        dados = {
            'linhas': self.linhas,
            'colunas': self.colunas,
            'paredes': list(self.paredes),
            'inicio': self.inicio,
            'fim': self.fim,
            'algoritmo': self.algoritmo
        }
        with open(nome_arquivo, 'w') as f:
            json.dump(dados, f)

    @classmethod
    def carregar_de_arquivo(cls, nome_arquivo):
        """
        Carrega um labirinto de um arquivo JSON
        
        Args:
            nome_arquivo (str): Caminho do arquivo para carregar
            
        Returns:
            Labirinto: Instância do labirinto carregado
        """
        with open(nome_arquivo, 'r') as f:
            dados = json.load(f)
        
        labirinto = cls(dados['linhas'], dados['colunas'], dados.get('algoritmo', 'prim'))
        labirinto.paredes = set(tuple(parede) for parede in dados['paredes'])
        labirinto.inicio = tuple(dados['inicio'])
        labirinto.fim = tuple(dados['fim'])
        return labirinto

    # =============================================
    # ALGORITMOS DE GERAÇÃO (MÉTODOS PRIVADOS)
    # =============================================

    def _gerar_labirinto_prim(self):
        """
        Implementação do algoritmo de Prim para geração de labirintos
        
        Cria labirintos com muitas ramificações e caminhos curtos
        """
        # Cria grafo grid completo
        G = nx.grid_2d_graph(self.linhas, self.colunas)
        
        # Inicializa com célula aleatória
        visitados = {self.inicio}
        arestas = [(self.inicio, vizinho) for vizinho in G.neighbors(self.inicio)]
        
        # Inicializa todas as paredes possíveis
        self.paredes = {
            (x, y, d) 
            for x in range(self.linhas) 
            for y in range(self.colunas) 
            for d in ['R', 'D']  # R: Parede à direita, D: Parede abaixo
        }

        # Adiciona paredes nas bordas
        self._adicionar_paredes_borda()

        while arestas:
            # Seleciona aresta aleatória
            aresta = random.choice(arestas)
            arestas.remove(aresta)
            
            no, proximo_no = aresta
            if proximo_no not in visitados:
                # Conecta os nós no labirinto
                visitados.add(proximo_no)
                self.labirinto.add_edge(no, proximo_no)
                
                # Remove a parede entre eles
                self._remover_parede_entre(no, proximo_no)
                
                # Adiciona novas arestas para explorar
                for vizinho in G.neighbors(proximo_no):
                    if vizinho not in visitados:
                        arestas.append((proximo_no, vizinho))

    def _gerar_labirinto_kruskal(self):
        """
        Implementação do algoritmo de Kruskal para geração de labirintos
        
        Cria labirintos com menos dead-ends que Prim
        """
        # Cria grafo grid completo
        G = nx.grid_2d_graph(self.linhas, self.colunas)
        arestas = list(G.edges())
        random.shuffle(arestas)  # Embaralha arestas
        
        # Estruturas para Union-Find
        pai = {no: no for no in G.nodes()}
        rank = {no: 0 for no in G.nodes()}

        # Funções auxiliares para Union-Find
        def encontrar(v):
            """Find com path compression"""
            if pai[v] != v:
                pai[v] = encontrar(pai[v])
            return pai[v]

        def unir(v1, v2):
            """Union by rank"""
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

        # Processa cada aresta
        for aresta in arestas:
            u, v = aresta
            if encontrar(u) != encontrar(v):
                # Conecta os nós no labirinto
                self.labirinto.add_edge(u, v)
                
                # Remove a parede entre eles
                self._remover_parede_entre(u, v)
                
                # Une os conjuntos
                unir(u, v)

    # =============================================
    # MÉTODOS AUXILIARES
    # =============================================

    def _adicionar_paredes_borda(self):
        """Adiciona paredes nas bordas do labirinto"""
        # Paredes horizontais (superior e inferior)
        for x in range(self.linhas):
            self.paredes.add((x, 0, 'D'))           # Borda superior
            self.paredes.add((x, self.colunas - 1, 'D'))  # Borda inferior
        
        # Paredes verticais (esquerda e direita)
        for y in range(self.colunas):
            self.paredes.add((0, y, 'R'))           # Borda esquerda
            self.paredes.add((self.linhas - 1, y, 'R'))  # Borda direita

    def _remover_parede_entre(self, no1, no2):
        """
        Remove a parede entre duas células adjacentes
        
        Args:
            no1 (tuple): Coordenadas (x,y) da primeira célula
            no2 (tuple): Coordenadas (x,y) da segunda célula
        """
        x1, y1 = no1
        x2, y2 = no2
        
        if x1 == x2:  # Células na mesma coluna (movimento vertical)
            self.paredes.discard((x1, min(y1, y2), 'D'))  # Remove parede abaixo
        else:  # Células na mesma linha (movimento horizontal)
            self.paredes.discard((min(x1, x2), y1, 'R'))  # Remove parede à direita