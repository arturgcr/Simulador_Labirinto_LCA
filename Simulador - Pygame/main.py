import pygame
from include.labirinto import Labirinto
from include.robo import Robo
import os

# =============================================
# CONFIGURAÇÕES DO JOGO
# =============================================

# Dimensões da janela principal e do painel lateral
LARGURA, ALTURA = 700, 700
LARGURA_INFO = 210

# Tamanho do labirinto (em células)
LINHAS, COLUNAS = 5, 5

# Tamanho de cada célula (ajustado para caber na janela)
TAMANHO_CELULA = min(LARGURA // COLUNAS, ALTURA // LINHAS)

# Paleta de cores
BRANCO = (255, 255, 255)                    # Fundo
PRETO = (0, 0, 0)                           # Paredes
AZUL = (50, 100, 255)                       # Ponto de início
VERMELHO = (255, 0, 0)                      # Ponto final
VERDE = (50, 255, 100)                      # Robô
CINZA = (200, 200, 200)                     # Painel lateral
ROXO = (150, 50, 255)                       # Caminho da solução
AZUL_CLARO = (100, 150, 255)                # Botão ativo
VERMELHO_TRANSPARENTE = (255, 0, 0, 150)    # Caminho transparente

# =============================================
# CLASE PRINCIPAL DO SIMULADOR
# =============================================

class SimuladorLabirinto:
    def __init__(self):
        """Inicializa o simulador com configurações padrão"""
        pygame.init()
        self.labirinto = Labirinto(LINHAS, COLUNAS, 'prim')
        # Passe tanto a posição inicial quanto o labirinto completo
        self.robo = Robo(self.labirinto.inicio, self.labirinto)
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
        # self.labirinto = Labirinto(LINHAS, COLUNAS, 'prim')
        # self.robo = Robo(self.labirinto.inicio, self.labirinto)  # Passe o labirinto como parâmetro
        self.caminho_solucao = self.labirinto.resolver()      # Solução do labirinto
        
        # Estados do simulador
        self.mostrar_caminho = False   # Se deve mostrar o caminho da solução
        self.algoritmo = 'prim'        # Algoritmo atual de geração
        self.ultimo_evento = None      # Último evento processado
        self.algoritmo_solucao = 'dfs'  # Algoritmo de busca inicial
        self.botoes_laterais = {}
        self.labirinto.simulador = self


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
        """Renderiza todas as paredes de forma precisa"""
        # Desenha paredes internas
        for x, y, direcao in self.labirinto.paredes:
            if direcao == 'R':
                pygame.draw.line(self.tela, PRETO,
                            ((x + 1) * TAMANHO_CELULA, y * TAMANHO_CELULA),
                            ((x + 1) * TAMANHO_CELULA, (y + 1) * TAMANHO_CELULA), 3)
            else:
                pygame.draw.line(self.tela, PRETO,
                            (x * TAMANHO_CELULA, (y + 1) * TAMANHO_CELULA),
                            ((x + 1) * TAMANHO_CELULA, (y + 1) * TAMANHO_CELULA), 3)

        # Desenha paredes externas mais espessas
        pygame.draw.rect(self.tela, PRETO, (0, 0, LARGURA, 5))  # Topo
        pygame.draw.rect(self.tela, PRETO, (0, ALTURA-5, LARGURA, 5))  # Base
        pygame.draw.rect(self.tela, PRETO, (0, 0, 5, ALTURA))  # Esquerda
        pygame.draw.rect(self.tela, PRETO, (LARGURA-5, 0, 5, ALTURA))  # Direita

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
        """Renderiza o caminho da solução (se existir) com transparência"""
        for x, y in self.caminho_solucao:
            # Cria uma superfície temporária com transparência
            transparent_surface = pygame.Surface((TAMANHO_CELULA - 4, TAMANHO_CELULA - 4), pygame.SRCALPHA)
            # Desenha o retângulo na superfície temporária
            pygame.draw.rect(transparent_surface, VERMELHO_TRANSPARENTE, (0, 0, TAMANHO_CELULA - 4, TAMANHO_CELULA -4))
            # Posiciona a superfície na tela principal
            self.tela.blit(transparent_surface, (x * TAMANHO_CELULA + 2, y * TAMANHO_CELULA + 2))
            
    def desenhar_painel_lateral(self):
        """Renderiza o painel lateral com informações organizadas"""
        # Fundo do painel
        pygame.draw.rect(self.tela, (230, 230, 230), (LARGURA, 0, LARGURA_INFO, ALTURA))
        
        # Título
        titulo = self.fonte_titulo.render("Informações", True, PRETO)
        self.tela.blit(titulo, (LARGURA + 20, 20))

        # Estado do robô
        estado = self.fonte.render("Estado do Robô:", True, PRETO)
        self.tela.blit(estado, (LARGURA + 20, 60))
        
        direcoes = ['Cima', 'Direita', 'Baixo', 'Esquerda']
        texto_dir = self.fonte.render(f"Direção: {direcoes[self.robo.direcao]}", True, (50, 50, 200))
        self.tela.blit(texto_dir, (LARGURA + 30, 90))
        
        pos_text = self.fonte.render(f"Posição: {self.robo.posicao}", True, (50, 50, 200))
        self.tela.blit(pos_text, (LARGURA + 30, 120))

        # Sensores
        sensores = self.fonte.render("Sensores:", True, PRETO)
        self.tela.blit(sensores, (LARGURA + 20, 160))
        
        # Atualiza as detecções
        self.robo.detectar_paredes()  # Agora usa a referência interna ao labirinto
        deteccoes = self.robo.get_deteccoes()
        
        # Frente
        frente_color = (255, 0, 0) if deteccoes['frente'] else (0, 150, 0)
        frente_text = self.fonte.render("Fre:", True, PRETO)
        self.tela.blit(frente_text, (LARGURA + 30, 190))
        frente_status = self.fonte.render("DETECTADO" if deteccoes['frente'] else "LIVRE", True, frente_color)
        self.tela.blit(frente_status, (LARGURA + 70, 190))
        
        # Esquerda
        esq_color = (255, 0, 0) if deteccoes['esquerda'] else (0, 150, 0)
        esq_text = self.fonte.render("Esq:", True, PRETO)
        self.tela.blit(esq_text, (LARGURA + 30, 220))
        esq_status = self.fonte.render("DETECTADO" if deteccoes['esquerda'] else "LIVRE", True, esq_color)
        self.tela.blit(esq_status, (LARGURA + 75, 220))
        
        # Direita
        dir_color = (255, 0, 0) if deteccoes['direita'] else (0, 150, 0)
        dir_text = self.fonte.render("Dir:", True, PRETO)
        self.tela.blit(dir_text, (LARGURA + 30, 250))
        dir_status = self.fonte.render("DETECTADO" if deteccoes['direita'] else "LIVRE", True, dir_color)
        self.tela.blit(dir_status, (LARGURA + 70, 250))

        # Controles
        controles = self.fonte.render("Controles:", True, PRETO)
        self.tela.blit(controles, (LARGURA + 20, 300))
        
        ctrl1 = self.fonte.render("Setas: Mover", True, (100, 100, 100))
        self.tela.blit(ctrl1, (LARGURA + 30, 330))
        
        ctrl2 = self.fonte.render("ESQ/DIR: Girar", True, (100, 100, 100))
        self.tela.blit(ctrl2, (LARGURA + 30, 360))
        
        ctrl3 = self.fonte.render("Espaço: Caminho", True, (100, 100, 100))
        self.tela.blit(ctrl3, (LARGURA + 30, 390))

        botao_caminho = self.criar_botao(420, "Mostrar Caminho", AZUL_CLARO if self.mostrar_caminho else AZUL)
        botao_novo = self.criar_botao(470, "Novo Labirinto", AZUL)
        botao_algoritmo = self.criar_botao(520, f"Algoritmo: {self.algoritmo}", AZUL)
        botao_salvar = self.criar_botao(570, "Salvar Labirinto", AZUL)
        botao_carregar = self.criar_botao(620, "Carregar Labirinto", AZUL)
        botao_metodos_de_resolucao = self.criar_botao(670, f"Resolver: {self.algoritmo_solucao}", AZUL)

        return botao_caminho, botao_novo, botao_algoritmo, botao_salvar, botao_carregar, botao_metodos_de_resolucao

    def criar_botao(self, y, texto, cor):
        """Cria um botão retangular na posição vertical y com o texto especificado"""
        botao = pygame.draw.rect(self.tela, cor, (LARGURA + 10, y, LARGURA_INFO - 20, 40))
        texto_render = self.fonte.render(texto, True, BRANCO)
        self.tela.blit(texto_render, (LARGURA + 20, y + 10))
        return botao

    def trocar_algoritmo_solucao(self):
        opcoes = ['dfs', 'bfs', 'aestrela']
        idx = opcoes.index(self.algoritmo_solucao)
        self.algoritmo_solucao = opcoes[(idx + 1) % len(opcoes)]


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
        """Processa comandos do teclado e imprime o estado do robô"""
        if evento.key == pygame.K_LEFT:
            self.robo.girar_esquerda()
            print(self.robo.get_estado())
        elif evento.key == pygame.K_RIGHT:
            self.robo.girar_direita()
            print(self.robo.get_estado())
        elif evento.key == pygame.K_UP:
            self.robo.mover('F')  # Ou pode usar pygame.K_UP para manter compatibilidade
        elif evento.key == pygame.K_DOWN:
            self.robo.mover('B')  # Ou pode usar pygame.K_DOWN para manter compatibilidade
        elif evento.key == pygame.K_SPACE:
            self.mostrar_caminho = not self.mostrar_caminho

    def processar_mouse(self):
        """Processa cliques no painel lateral"""
        pos = pygame.mouse.get_pos()
        if pos[0] > LARGURA:  # Verifica se clique foi no painel
            botoes = self.desenhar_painel_lateral()
            botao_caminho, botao_novo, botao_algoritmo, botao_salvar, botao_carregar, botao_metodos_de_resolucao = botoes

            
            # if pos[0] > LARGURA and self.botoes_laterais:
            #     if self.botoes_laterais['resolver'].collidepoint(pos):
            #         self.robo.resolver_com_movimento(self.algoritmo_solucao)
            #     elif self.botoes_laterais['modo'].collidepoint(pos):
            #         self.trocar_algoritmo_solucao()
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
            elif botao_metodos_de_resolucao.collidepoint(pos):
                self.trocar_algoritmo_solucao()
                self.robo.resolver_com_movimento(self.algoritmo_solucao)  # Resolve o labirinto com o novo algoritmo
            
                    
    def criar_novo_labirinto(self):
        """Gera um novo labirinto com o algoritmo atual"""
        self.labirinto = Labirinto(LINHAS, COLUNAS, self.algoritmo)
        self.labirinto.simulador = self
        self.robo = Robo(self.labirinto.inicio, self.labirinto)  # Adicionei o segundo parâmetro
        self.caminho_solucao = self.labirinto.resolver()

    def alternar_algoritmo(self):
        """Alterna entre os algoritmos de geração de labirinto"""
        if self.algoritmo == 'prim':
            self.algoritmo = 'kruskal'
        elif self.algoritmo == 'kruskal':
            self.algoritmo = 'growingtree'
        else:
            self.algoritmo = 'prim'
        self.criar_novo_labirinto()

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
                self.robo = Robo(self.labirinto.inicio, self.labirinto)  # Adicionei o segundo parâmetro
                self.caminho_solucao = self.labirinto.resolver()
                self.labirinto.simulador = self
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