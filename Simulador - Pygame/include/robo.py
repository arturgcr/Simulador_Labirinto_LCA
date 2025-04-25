import pygame
import math

class Robo:
    def __init__(self, inicio, labirinto):
        self.posicao = list(inicio)
        self.labirinto = labirinto
        self.labirinto.simulador = None  # default
        self.direcao = 0  # 0: cima, 1: direita, 2: baixo, 3: esquerda
        self.cor = (220, 120, 245)
        self.cor_seta = (0, 0, 0)
        self.cor_sensor = (0, 255, 0)
        self.deteccoes = {
            'frente': False,
            'esquerda': False,
            'direita': False
        }
        print(self.get_estado())  # Imprime o estado inicial do robô

    def detectar_paredes(self):
        """Detecta paredes ao redor do robô de forma consistente em todas as direções"""
        x, y = self.posicao
        self.deteccoes = {'frente': False, 'esquerda': False, 'direita': False}

        # Verifica primeiro se está contra as paredes externas
        if x == 0:
            self.deteccoes['esquerda'] = True if self.direcao == 3 else False
        if x == self.labirinto.linhas - 1:
            self.deteccoes['direita'] = True if self.direcao == 1 else False
        if y == 0:
            self.deteccoes['cima'] = True if self.direcao == 0 else False
        if y == self.labirinto.colunas - 1:
            self.deteccoes['baixo'] = True if self.direcao == 2 else False

        # Verifica paredes internas baseado na direção atual
        if self.direcao == 0:  # Cima
            self.deteccoes['frente'] = self._parede_em(x, y, 'cima')
            self.deteccoes['esquerda'] = self._parede_em(x, y, 'esquerda')
            self.deteccoes['direita'] = self._parede_em(x, y, 'direita')
        
        elif self.direcao == 1:  # Direita
            self.deteccoes['frente'] = self._parede_em(x, y, 'direita')
            self.deteccoes['esquerda'] = self._parede_em(x, y, 'cima')
            self.deteccoes['direita'] = self._parede_em(x, y, 'baixo')
        
        elif self.direcao == 2:  # Baixo
            self.deteccoes['frente'] = self._parede_em(x, y, 'baixo')
            self.deteccoes['esquerda'] = self._parede_em(x, y, 'direita')
            self.deteccoes['direita'] = self._parede_em(x, y, 'esquerda')
        
        else:  # Esquerda (3)
            self.deteccoes['frente'] = self._parede_em(x, y, 'esquerda')
            self.deteccoes['esquerda'] = self._parede_em(x, y, 'baixo')
            self.deteccoes['direita'] = self._parede_em(x, y, 'cima')

    def _parede_em(self, x, y, lado):
        """Verifica se há parede em um lado específico da célula"""
        # Primeiro verifica se está tentando sair dos limites
        if lado == 'cima' and y == 0:
            return True
        if lado == 'baixo' and y == self.labirinto.colunas - 1:
            return True
        if lado == 'esquerda' and x == 0:
            return True
        if lado == 'direita' and x == self.labirinto.linhas - 1:
            return True
        
        # Verifica paredes internas
        if lado == 'cima':
            return (x, y-1, 'D') in self.labirinto.paredes if y > 0 else True
        elif lado == 'baixo':
            return (x, y, 'D') in self.labirinto.paredes
        elif lado == 'esquerda':
            return (x-1, y, 'R') in self.labirinto.paredes if x > 0 else True
        elif lado == 'direita':
            return (x, y, 'R') in self.labirinto.paredes
        
        return False

    def girar_esquerda(self):
        self.direcao = (self.direcao - 1) % 4

    def girar_direita(self):
        self.direcao = (self.direcao + 1) % 4

    def mover(self, comando):
        """
        Move ou rotaciona o robô baseado em comandos:
        - 'F' ou 'FRENTE': Move para frente
        - 'B' ou 'TRAS': Move para trás
        - 'R': Apenas vira 90° à direita (sem mover)
        - 'L': Apenas vira 90° à esquerda (sem mover)
        - Teclas de seta mantêm comportamento original
        """
        comando = comando.upper() if isinstance(comando, str) else comando
        
        if comando in ['F', 'FRENTE', pygame.K_UP]:
            self._mover_na_direcao(1, self.labirinto.paredes.union(self.labirinto.paredes_externas))
        elif comando in ['B', 'TRAS', pygame.K_DOWN]:
            self._mover_na_direcao(-1, self.labirinto.paredes.union(self.labirinto.paredes_externas))
        elif comando == 'R':
            self.girar_direita()  # Apenas rotaciona
        elif comando == 'L':
            self.girar_esquerda()  # Apenas rotaciona
        
        # Imprime o estado após qualquer ação
        print(self.get_estado())

    def _mover_na_direcao(self, passo, paredes):
        nova_pos = self.posicao.copy()
        
        if self.direcao == 0:  # Cima
            nova_pos[1] -= passo
            parede_dir = 'D'
            y_parede = min(self.posicao[1], nova_pos[1])
            x_parede = self.posicao[0]
        elif self.direcao == 1:  # Direita
            nova_pos[0] += passo
            parede_dir = 'R'
            x_parede = min(self.posicao[0], nova_pos[0])
            y_parede = self.posicao[1]
        elif self.direcao == 2:  # Baixo
            nova_pos[1] += passo
            parede_dir = 'D'
            y_parede = min(self.posicao[1], nova_pos[1])
            x_parede = self.posicao[0]
        else:  # Esquerda
            nova_pos[0] -= passo
            parede_dir = 'R'
            x_parede = min(self.posicao[0], nova_pos[0])
            y_parede = self.posicao[1]

        if (x_parede, y_parede, parede_dir) not in paredes:
            self.posicao = nova_pos

    def desenhar(self, superficie, tamanho_celula):
        centro_x = self.posicao[0] * tamanho_celula + tamanho_celula // 2
        centro_y = self.posicao[1] * tamanho_celula + tamanho_celula // 2
        self.raio = tamanho_celula // 3  # Definindo o raio aqui

        pygame.draw.circle(superficie, self.cor, (centro_x, centro_y), self.raio)
        self.desenhar_sensores(superficie, centro_x, centro_y, tamanho_celula)
        self.desenhar_seta(superficie, centro_x, centro_y)

    def desenhar_seta(self, superficie, centro_x, centro_y):
        tamanho_seta = self.raio * 0.8
        pontos = []
        
        if self.direcao == 0:  # Cima
            pontos = [
                (centro_x, centro_y - tamanho_seta),
                (centro_x - tamanho_seta/2, centro_y),
                (centro_x + tamanho_seta/2, centro_y)
            ]
        elif self.direcao == 1:  # Direita
            pontos = [
                (centro_x + tamanho_seta, centro_y),
                (centro_x, centro_y - tamanho_seta/2),
                (centro_x, centro_y + tamanho_seta/2)
            ]
        elif self.direcao == 2:  # Baixo
            pontos = [
                (centro_x, centro_y + tamanho_seta),
                (centro_x - tamanho_seta/2, centro_y),
                (centro_x + tamanho_seta/2, centro_y)
            ]
        else:  # Esquerda
            pontos = [
                (centro_x - tamanho_seta, centro_y),
                (centro_x, centro_y - tamanho_seta/2),
                (centro_x, centro_y + tamanho_seta/2)
            ]
        
        pygame.draw.polygon(superficie, self.cor_seta, pontos)

    def desenhar_sensores(self, superficie, centro_x, centro_y, tamanho_celula):
        comprimento = tamanho_celula
        espessura = 2
        
        if self.direcao == 0:  # Cima
            # Frente
            pygame.draw.line(superficie, self.cor_sensor, 
                           (centro_x, centro_y - self.raio),
                           (centro_x, centro_y - comprimento), espessura)
            # Esquerda (-60°)
            end_x = centro_x - comprimento * math.sin(math.radians(60))
            end_y = centro_y - comprimento * math.cos(math.radians(60))
            pygame.draw.line(superficie, self.cor_sensor,
                           (centro_x, centro_y), (end_x, end_y), espessura)
            # Direita (+60°)
            end_x = centro_x + comprimento * math.sin(math.radians(60))
            end_y = centro_y - comprimento * math.cos(math.radians(60))
            pygame.draw.line(superficie, self.cor_sensor,
                           (centro_x, centro_y), (end_x, end_y), espessura)

        elif self.direcao == 1:  # Direita
            # Frente
            pygame.draw.line(superficie, self.cor_sensor,
                           (centro_x + self.raio, centro_y),
                           (centro_x + comprimento, centro_y), espessura)
            # Esquerda (-60°)
            end_x = centro_x + comprimento * math.cos(math.radians(60))
            end_y = centro_y - comprimento * math.sin(math.radians(60))
            pygame.draw.line(superficie, self.cor_sensor,
                           (centro_x, centro_y), (end_x, end_y), espessura)
            # Direita (+60°)
            end_x = centro_x + comprimento * math.cos(math.radians(60))
            end_y = centro_y + comprimento * math.sin(math.radians(60))
            pygame.draw.line(superficie, self.cor_sensor,
                           (centro_x, centro_y), (end_x, end_y), espessura)

        elif self.direcao == 2:  # Baixo
            # Frente
            pygame.draw.line(superficie, self.cor_sensor,
                           (centro_x, centro_y + self.raio),
                           (centro_x, centro_y + comprimento), espessura)
            # Esquerda (-60°)
            end_x = centro_x + comprimento * math.sin(math.radians(60))
            end_y = centro_y + comprimento * math.cos(math.radians(60))
            pygame.draw.line(superficie, self.cor_sensor,
                           (centro_x, centro_y), (end_x, end_y), espessura)
            # Direita (+60°)
            end_x = centro_x - comprimento * math.sin(math.radians(60))
            end_y = centro_y + comprimento * math.cos(math.radians(60))
            pygame.draw.line(superficie, self.cor_sensor,
                           (centro_x, centro_y), (end_x, end_y), espessura)

        else:  # Esquerda
            # Frente
            pygame.draw.line(superficie, self.cor_sensor,
                           (centro_x - self.raio, centro_y),
                           (centro_x - comprimento, centro_y), espessura)
            # Esquerda (-60°)
            end_x = centro_x - comprimento * math.cos(math.radians(60))
            end_y = centro_y + comprimento * math.sin(math.radians(60))
            pygame.draw.line(superficie, self.cor_sensor,
                           (centro_x, centro_y), (end_x, end_y), espessura)
            # Direita (+60°)
            end_x = centro_x - comprimento * math.cos(math.radians(60))
            end_y = centro_y - comprimento * math.sin(math.radians(60))
            pygame.draw.line(superficie, self.cor_sensor,
                           (centro_x, centro_y), (end_x, end_y), espessura)

    def get_deteccoes(self):
        return self.deteccoes
    
    def get_estado(self):
        """Retorna um dicionário com a posição e estado dos sensores"""
        self.detectar_paredes()  # Atualiza as detecções
        
        return {
            'posicao': tuple(self.posicao),
            'sensores': {
                'frente': 1 if self.deteccoes['frente'] else 0,
                'esquerda': 1 if self.deteccoes['esquerda'] else 0,
                'direita': 1 if self.deteccoes['direita'] else 0
            },
            'direcao': self.direcao
        }
    
    def _rotacionar_para(self, nova_direcao):
        """Gira o robô para a direção desejada"""
        while self.direcao != nova_direcao:
            self.girar_direita()

    def _parede_a_frente(self):
        self.detectar_paredes()
        return self.deteccoes['frente']

    def resolver_com_movimento(self, algoritmo='dfs'):
        visitado = set()
        caminho = []

        if not hasattr(self.labirinto, 'simulador') or self.labirinto.simulador is None:
            print("ERRO: self.labirinto.simulador está None")
            return

        def animar():
            self.labirinto.simulador.desenhar_labirinto()
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            self.labirinto.simulador.relogio.tick(100)  # ajuste de velocidade

        def dfs(x, y):
            pos = (x, y)
            if pos in visitado:
                return False
            visitado.add(pos)
            caminho.append(pos)

            if pos == self.labirinto.fim:
                return True

            for nova_direcao in range(4):
                self._rotacionar_para(nova_direcao)
                animar()

                if not self._parede_a_frente():
                    self.mover('F')
                    animar()

                    if dfs(*self.posicao):
                        return True

                    self.mover('B')  # backtrack
                    animar()

            caminho.pop()
            return False

        dfs(*self.posicao)
        self.caminho_encontrado = caminho


