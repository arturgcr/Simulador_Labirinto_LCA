import pygame
from include.labirinto import Labirinto
from include.robo import Robo
import os

# =============================================
# CONFIGURAÇÕES DO JOGO
# =============================================

# Dimensões da janela principal e do painel lateral
LARGURA, ALTURA = 700, 700
LARGURA_INFO = 200

# Tamanho do labirinto (em células)
LINHAS, COLUNAS = 20, 20

# Tamanho de cada célula (ajustado para caber na janela)
TAMANHO_CELULA = min(LARGURA // COLUNAS, ALTURA // LINHAS)

# Paleta de cores
BRANCO = (255, 255, 255)     # Fundo
PRETO = (0, 0, 0)            # Paredes
AZUL = (50, 100, 255)        # Ponto de início
VERMELHO = (255, 50, 50)     # Ponto final
VERDE = (50, 255, 100)       # Robô
CINZA = (200, 200, 200)      # Painel lateral
ROXO = (150, 50, 255)        # Caminho da solução
AZUL_CLARO = (100, 150, 255) # Botão ativo

# =============================================
# CLASE PRINCIPAL DO SIMULADOR
# =============================================

class SimuladorLabirinto:
    def __init__(self):
        """Inicializa o simulador com configurações padrão"""
        pygame.init()
        
        # Configuração da janela
        self.tela = pygame.display.set_mode((LARGURA + LARGURA_INFO, ALTURA))
        pygame.display.set_caption("Labirinto com Robô")
        
        # Configurações de tempo e fonte
        self.relogio = pygame.time.Clock()
        self.fonte = pygame.font.Font(None, 28)          # Fonte para texto normal
        self.fonte_titulo = pygame.font.Font(None, 36)   # Fonte para títulos
        
        # Cria a pasta para salvar labirintos
        self.criar_pasta_dados()
        
        # Inicializa os componentes principais
        self.labirinto = Labirinto(LINHAS, COLUNAS, 'prim')  # Labirinto com algoritmo Prim
        self.robo = Robo(self.labirinto.inicio)               # Robô na posição inicial
        self.caminho_solucao = self.labirinto.resolver()      # Solução do labirinto
        
        # Estados do jogo
        self.mostrar_caminho = False   # Se deve mostrar o caminho da solução
        self.algoritmo = 'prim'        # Algoritmo atual de geração
        self.ultimo_evento = None      # Último evento processado

    def criar_pasta_dados(self):
        """Cria a pasta 'data' se não existir para armazenar labirintos salvos"""
        if not os.path.exists('Simulador - Pygame/data'):
            os.makedirs('Simulador - Pygame/data')

    # =============================================
    # MÉTODOS DE RENDERIZAÇÃO
    # =============================================

    def desenhar_labirinto(self):
        """Renderiza todos os elementos do labirinto na tela"""
        # Fundo branco
        self.tela.fill(BRANCO)
        
        # Desenha todas as paredes do labirinto
        self.desenhar_paredes()
        
        # Desenha os pontos de início (azul) e fim (vermelho)
        self.desenhar_pontos_referencia()
        
        # Se ativado, desenha o caminho da solução (roxo)
        if self.mostrar_caminho:
            self.desenhar_caminho_solucao()
        
        # Desenha o robô na posição atual
        self.robo.desenhar(self.tela, TAMANHO_CELULA)
        
        # Renderiza o painel lateral com controles e informações
        self.desenhar_painel_lateral()

    def desenhar_paredes(self):
        """Renderiza todas as paredes do labirinto"""
        for x, y, direcao in self.labirinto.paredes:
            if direcao == 'R':  # Parede à direita da célula
                pygame.draw.line(self.tela, PRETO, 
                               ((x + 1) * TAMANHO_CELULA, y * TAMANHO_CELULA), 
                               ((x + 1) * TAMANHO_CELULA, (y + 1) * TAMANHO_CELULA), 3)
            else:  # Parede abaixo da célula
                pygame.draw.line(self.tela, PRETO, 
                               (x * TAMANHO_CELULA, (y + 1) * TAMANHO_CELULA), 
                               ((x + 1) * TAMANHO_CELULA, (y + 1) * TAMANHO_CELULA), 3)

    def desenhar_pontos_referencia(self):
        """Renderiza o ponto de início (azul) e fim (vermelho)"""
        # Ponto de início
        pygame.draw.rect(self.tela, AZUL, 
                        (self.labirinto.inicio[0] * TAMANHO_CELULA, 
                         self.labirinto.inicio[1] * TAMANHO_CELULA, 
                         TAMANHO_CELULA, TAMANHO_CELULA))
        
        # Ponto final
        pygame.draw.rect(self.tela, VERMELHO, 
                        (self.labirinto.fim[0] * TAMANHO_CELULA, 
                         self.labirinto.fim[1] * TAMANHO_CELULA, 
                         TAMANHO_CELULA, TAMANHO_CELULA))

    def desenhar_caminho_solucao(self):
        """Renderiza o caminho da solução (se existir)"""
        for x, y in self.caminho_solucao:
            pygame.draw.rect(self.tela, ROXO, 
                           (x * TAMANHO_CELULA + TAMANHO_CELULA // 4, 
                            y * TAMANHO_CELULA + TAMANHO_CELULA // 4, 
                            TAMANHO_CELULA // 2, TAMANHO_CELULA // 2))

    def desenhar_painel_lateral(self):
        """Renderiza o painel lateral com controles e informações"""
        # Fundo cinza do painel
        pygame.draw.rect(self.tela, CINZA, (LARGURA, 0, LARGURA_INFO, ALTURA))
        
        # Título do painel
        titulo = self.fonte_titulo.render("Configurações", True, PRETO)
        self.tela.blit(titulo, (LARGURA + 10, 10))

        # Exibe a direção atual do robô
        direcoes = ['Cima', 'Direita', 'Baixo', 'Esquerda']
        texto_direcao = self.fonte.render(f"Direção: {direcoes[self.robo.direcao]}", True, PRETO)
        self.tela.blit(texto_direcao, (LARGURA + 10, 50))

        # Botões interativos
        botao_caminho = self.criar_botao(90, "Mostrar Caminho", AZUL_CLARO if self.mostrar_caminho else AZUL)
        botao_novo = self.criar_botao(140, "Novo Labirinto", AZUL)
        botao_algoritmo = self.criar_botao(190, f"Algoritmo: {self.algoritmo}", AZUL)
        botao_salvar = self.criar_botao(240, "Salvar Labirinto", AZUL)
        botao_carregar = self.criar_botao(290, "Carregar Labirinto", AZUL)

        # Instruções de controle
        self.desenhar_instrucoes()

        return botao_caminho, botao_novo, botao_algoritmo, botao_salvar, botao_carregar

    def criar_botao(self, y, texto, cor):
        """Cria um botão retangular na posição vertical y com o texto especificado"""
        botao = pygame.draw.rect(self.tela, cor, (LARGURA + 10, y, LARGURA_INFO - 20, 40))
        texto_render = self.fonte.render(texto, True, BRANCO)
        self.tela.blit(texto_render, (LARGURA + 20, y + 10))
        return botao

    def desenhar_instrucoes(self):
        """Exibe as instruções de controle no painel lateral"""
        instrucoes = [
            "Controles:",
            "Setas: Mover",
            "ESQ/DIR: Girar",
            "Espaço: Caminho"
        ]
        
        for i, texto in enumerate(instrucoes):
            render = self.fonte.render(texto, True, PRETO)
            self.tela.blit(render, (LARGURA + 10, 350 + i * 30))

    # =============================================
    # LÓGICA DO JOGO E CONTROLES
    # =============================================

    def tratar_eventos(self):
        """Processa todos os eventos do jogo"""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False  # Encerra o jogo
            
            # Controles por teclado
            elif evento.type == pygame.KEYDOWN:
                self.processar_teclado(evento)
            
            # Controles por mouse (painel lateral)
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                self.processar_mouse()
        
        return True  # Continua o jogo

    def processar_teclado(self, evento):
        """Processa as entradas do teclado"""
        if evento.key == pygame.K_LEFT:
            self.robo.girar_esquerda()  # Gira o robô para esquerda
        elif evento.key == pygame.K_RIGHT:
            self.robo.girar_direita()   # Gira o robô para direita
        elif evento.key == pygame.K_UP:
            self.robo.mover('FRENTE', self.labirinto.paredes)  # Move para frente
        elif evento.key == pygame.K_DOWN:
            self.robo.mover('TRAS', self.labirinto.paredes)    # Move para trás
        elif evento.key == pygame.K_SPACE:
            self.mostrar_caminho = not self.mostrar_caminho    # Alterna visão do caminho

    def processar_mouse(self):
        """Processa cliques no painel lateral"""
        pos = pygame.mouse.get_pos()
        if pos[0] > LARGURA:  # Verifica se clique foi no painel
            botoes = self.desenhar_painel_lateral()
            botao_caminho, botao_novo, botao_algoritmo, botao_salvar, botao_carregar = botoes

            if botao_caminho.collidepoint(pos):
                self.mostrar_caminho = not self.mostrar_caminho  # Alterna caminho
            elif botao_novo.collidepoint(pos):
                self.criar_novo_labirinto()  # Gera novo labirinto
            elif botao_algoritmo.collidepoint(pos):
                self.alternar_algoritmo()    # Troca algoritmo de geração
            elif botao_salvar.collidepoint(pos):
                self.salvar_labirinto()      # Salva labirinto atual
            elif botao_carregar.collidepoint(pos):
                self.carregar_labirinto()    # Carrega labirinto salvo

    def criar_novo_labirinto(self):
        """Gera um novo labirinto com o algoritmo atual"""
        self.labirinto = Labirinto(LINHAS, COLUNAS, self.algoritmo)
        self.robo = Robo(self.labirinto.inicio)
        self.caminho_solucao = self.labirinto.resolver()

    def alternar_algoritmo(self):
        """Alterna entre os algoritmos de geração de labirinto"""
        self.algoritmo = 'kruskal' if self.algoritmo == 'prim' else 'prim'
        self.criar_novo_labirinto()

    # =============================================
    # PERSISTÊNCIA DE DADOS
    # =============================================

    def salvar_labirinto(self):
        """Salva o labirinto atual em um arquivo JSON"""
        try:
            # Encontra o próximo número disponível para nome do arquivo
            arquivos = [f for f in os.listdir('Simulador - Pygame/data') if f.startswith('labirinto_')]
            numero = len(arquivos) + 1
            nome_arquivo = f"Simulador - Pygame/data/labirinto_{numero}.json"
            
            # Salva o labirinto
            self.labirinto.salvar_para_arquivo(nome_arquivo)
            print(f"Labirinto salvo como {nome_arquivo}")
        except Exception as e:
            print(f"Erro ao salvar labirinto: {e}")

    def carregar_labirinto(self):
        """Carrega o último labirinto salvo"""
        try:
            arquivos = [f for f in os.listdir('Simulador - Pygame/data') if f.startswith('labirinto_')]
            if arquivos:
                # Carrega o arquivo mais recente
                ultimo_arquivo = sorted(arquivos)[-1]
                self.labirinto = Labirinto.carregar_de_arquivo(f"Simulador - Pygame/data/{ultimo_arquivo}")
                self.robo = Robo(self.labirinto.inicio)
                self.caminho_solucao = self.labirinto.resolver()
                print(f"Labirinto {ultimo_arquivo} carregado com sucesso!")
        except Exception as e:
            print(f"Erro ao carregar labirinto: {e}")

    # =============================================
    # LOOP PRINCIPAL
    # =============================================

    def executar(self):
        """Inicia e mantém o loop principal do jogo"""
        rodando = True
        while rodando:
            # Processa eventos e verifica se deve continuar
            rodando = self.tratar_eventos()
            
            # Atualiza a renderização
            self.desenhar_labirinto()
            pygame.display.flip()
            
            # Controla a taxa de atualização
            self.relogio.tick(60)
        
        # Encerra o pygame ao sair
        pygame.quit()

# =============================================
# INICIALIZAÇÃO DO PROGRAMA
# =============================================

if __name__ == "__main__":
    # Cria e executa o simulador
    simulador = SimuladorLabirinto()
    simulador.executar()