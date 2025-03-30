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
        self.linhas = linhas
        self.colunas = colunas
        self.algoritmo = algoritmo
        self.paredes = set()
        self.paredes_externas = set()
        self.labirinto = nx.Graph()
        self.inicio = (0, 0)
        self.fim = (colunas - 1, linhas - 1)
        self.gerar_labirinto()
        self._definir_paredes_externas()

    def _definir_paredes_externas(self):
        """Define paredes externas ao redor de todo o labirinto"""
        # Paredes horizontais externas (acima e abaixo do labirinto)
        for x in range(-1, self.linhas + 1):
            self.paredes_externas.add((x, -1, 'D'))  # Acima
            self.paredes_externas.add((x, self.colunas, 'D'))  # Abaixo

        # Paredes verticais externas (esquerda e direita do labirinto)
        for y in range(-1, self.colunas + 1):
            self.paredes_externas.add((-1, y, 'R'))  # Esquerda
            self.paredes_externas.add((self.linhas, y, 'R'))  # Direita
    def _adicionar_paredes_externas(self):
        """Adiciona paredes externas ao redor de todo o labirinto"""
        # Paredes horizontais (acima da primeira linha e abaixo da última)
        for x in range(-1, self.linhas + 1):
            self.paredes_externas.add((x, -1, 'D'))  # Parede acima do labirinto
            self.paredes_externas.add((x, self.colunas, 'D'))  # Parede abaixo do labirinto
        
        # Paredes verticais (à esquerda da primeira coluna e à direita da última)
        for y in range(-1, self.colunas + 1):
            self.paredes_externas.add((-1, y, 'R'))  # Parede à esquerda do labirinto
            self.paredes_externas.add((self.linhas, y, 'R'))  # Parede à direita do labirinto
    def _reconstruir_grafo(self):
        """Reconstrói o grafo do labirinto com base nas paredes atuais"""
        self.labirinto = nx.grid_2d_graph(self.linhas, self.colunas)
        
        # Remove arestas onde existem paredes
        for x, y, direcao in self.paredes:
            if direcao == 'R' and x < self.linhas - 1:
                self.labirinto.remove_edge((x, y), (x + 1, y))
            elif direcao == 'D' and y < self.colunas - 1:
                self.labirinto.remove_edge((x, y), (x, y + 1))

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
        labirinto._reconstruir_grafo()  # RECONSTRÓI O GRAFO
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
        Implementação corrigida do algoritmo de Kruskal para geração de labirintos
        """
        # Cria grafo grid completo com todas as paredes possíveis
        self.paredes = {
            (x, y, d) 
            for x in range(self.linhas) 
            for y in range(self.colunas) 
            for d in ['R', 'D']  # R: Parede à direita, D: Parede abaixo
        }
        
        # Adiciona paredes nas bordas
        self._adicionar_paredes_borda()
        
        # Cria lista de todas as arestas possíveis (paredes internas)
        arestas = []
        for x in range(self.linhas):
            for y in range(self.colunas):
                if x < self.linhas - 1:
                    arestas.append(((x, y), (x+1, y)))  # Parede à direita
                if y < self.colunas - 1:
                    arestas.append(((x, y), (x, y+1)))  # Parede abaixo
        
        # Embaralha as arestas
        random.shuffle(arestas)
        
        # Estruturas para Union-Find
        pai = {no: no for no in [(x, y) for x in range(self.linhas) for y in range(self.colunas)]}
        rank = {no: 0 for no in pai.keys()}

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
                else:
                    pai[raiz1] = raiz2
                    if rank[raiz1] == rank[raiz2]:
                        rank[raiz2] += 1

        # Processa cada aresta
        for u, v in arestas:
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
        Remove a parede entre duas células adjacentes de forma consistente
        """
        x1, y1 = no1
        x2, y2 = no2
        
        if x1 == x2:  # Células na mesma coluna (vertical)
            # Remove parede abaixo da célula de cima
            if y1 < y2:
                self.paredes.discard((x1, y1, 'D'))
            else:
                self.paredes.discard((x2, y2, 'D'))
        else:  # Células na mesma linha (horizontal)
            # Remove parede à direita da célula da esquerda
            if x1 < x2:
                self.paredes.discard((x1, y1, 'R'))
            else:
                self.paredes.discard((x2, y2, 'R'))