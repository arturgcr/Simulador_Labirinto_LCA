import pygame
import math

class Robo:
    def __init__(self, inicio):
        self.posicao = list(inicio)
        self.direcao = 0  # 0: cima, 1: direita, 2: baixo, 3: esquerda
        self.cor = (50, 255, 100)  # Verde
        self.cor_seta = (0, 0, 0)  # Preto

    def girar_esquerda(self):
        self.direcao = (self.direcao - 1) % 4

    def girar_direita(self):
        self.direcao = (self.direcao + 1) % 4

    def mover(self, acao, paredes):
        if acao == 'FRENTE':
            self._mover_na_direcao(1, paredes)
        elif acao == 'TRAS':
            self._mover_na_direcao(-1, paredes)

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
        raio = tamanho_celula // 3

        # Desenha o corpo do robô
        pygame.draw.circle(superficie, self.cor, (centro_x, centro_y), raio)

        # Desenha a seta (triângulo apontando na direção atual)
        pontos = []
        tamanho_seta = raio * 0.8
        
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