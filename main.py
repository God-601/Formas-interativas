import pygame
import pymunk
import sys
import tkinter as tk
from tkinter import colorchooser

# Inicialização do Pygame
pygame.init()

# Configurações da tela
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Construtor de Formas")

# Cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255) 
VERMELHO = (255, 0, 0)
AZUL = (0, 0, 255)
VERDE = (0, 255, 0)
CINZA = (128, 128, 128)

def escolher_cor():
    root = tk.Tk()
    root.withdraw()  # Esconde a janela principal do tkinter
    cor = colorchooser.askcolor(title="Escolha uma cor")[0]
    root.destroy()  # Fecha completamente a janela do tkinter
    if cor:  # Se uma cor foi escolhida
        return (int(cor[0]), int(cor[1]), int(cor[2]))
    return None

class Botao:
    def __init__(self, x, y, largura, altura, texto, cor=BRANCO, cor_hover=VERDE):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.texto = texto
        self.cor = cor
        self.cor_hover = cor_hover
        self.cor_atual = cor
        self.fonte = pygame.font.Font(None, 36)
        
    def desenhar(self, superficie):
        pygame.draw.rect(superficie, self.cor_atual, self.rect, border_radius=12)
        texto_surface = self.fonte.render(self.texto, True, PRETO)
        texto_rect = texto_surface.get_rect(center=self.rect.center)
        superficie.blit(texto_surface, texto_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.cor_atual = self.cor_hover
            else:
                self.cor_atual = self.cor
                
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

def menu_principal():
    botao_play = Botao(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 50, "Play")
    botao_como_jogar = Botao(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, "Como Jogar")
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if botao_play.handle_event(event):
                return "play"
            if botao_como_jogar.handle_event(event):
                return "como_jogar"
        
        screen.fill(PRETO)
        
        # Título
        fonte_titulo = pygame.font.Font(None, 74)
        titulo = fonte_titulo.render("Construtor de Formas", True, BRANCO)
        titulo_rect = titulo.get_rect(center=(WIDTH//2, HEIGHT//4))
        screen.blit(titulo, titulo_rect)
        
        botao_play.desenhar(screen)
        botao_como_jogar.desenhar(screen)
        
        pygame.display.flip()

def tela_como_jogar():
    botao_voltar = Botao(WIDTH//2 - 100, HEIGHT - 100, 200, 50, "Voltar")
    fonte = pygame.font.Font(None, 32)
    
    instrucoes = [
        "Como Jogar:",
        "",
        "1. Clique esquerdo para criar formas",
        "2. Pressione ESPAÇO ou E para trocar de forma",
        "3. Pressione S para entrar no modo de seleção",
        "4. No modo de seleção, clique nas formas para selecioná-las",
        "5. Pressione C para mudar a cor das formas selecionadas",
        "6. Pressione J para juntar formas selecionadas",
        "7. Clique direito e arraste para mover as formas"
    ]
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if botao_voltar.handle_event(event):
                return "menu"
        
        screen.fill(PRETO)
        
        # Renderizar instruções
        for i, linha in enumerate(instrucoes):
            texto = fonte.render(linha, True, BRANCO)
            screen.blit(texto, (50, 50 + i * 40))
        
        botao_voltar.desenhar(screen)
        
        pygame.display.flip()

def jogo_principal():
    # Inicialização do Pymunk
    space = pymunk.Space()
    space.gravity = (0, 900)

    # Lista de formas disponíveis
    formas = ["quadrado", "circulo", "triangulo"]
    forma_atual = 0
    cor_atual = VERMELHO

    # Variáveis para arrastar objetos
    objeto_arrastado = None
    mouse_joint = None
    mouse_body = None
    formas_selecionadas = []
    modo_selecao = False

    def criar_quadrado(pos):
        massa = 1
        tamanho = 40
        momento = pymunk.moment_for_box(massa, (tamanho, tamanho))
        body = pymunk.Body(massa, momento)
        body.position = pos
        shape = pymunk.Poly.create_box(body, (tamanho, tamanho))
        shape.elasticity = 0.8
        shape.friction = 0.5
        shape.color = cor_atual
        space.add(body, shape)
        return shape

    def criar_circulo(pos):
        massa = 1
        raio = 20
        momento = pymunk.moment_for_circle(massa, 0, raio)
        body = pymunk.Body(massa, momento)
        body.position = pos
        shape = pymunk.Circle(body, raio)
        shape.elasticity = 0.8
        shape.friction = 0.5
        shape.color = cor_atual
        space.add(body, shape)
        return shape

    def criar_triangulo(pos):
        massa = 1
        vertices = [(-20, 20), (20, 20), (0, -20)]
        momento = pymunk.moment_for_poly(massa, vertices)
        body = pymunk.Body(massa, momento)
        body.position = pos
        shape = pymunk.Poly(body, vertices)
        shape.elasticity = 0.8
        shape.friction = 0.5
        shape.color = cor_atual
        space.add(body, shape)
        return shape

    def unir_formas():
        if len(formas_selecionadas) < 2:
            return
        
        massa_total = sum(shape.body.mass for shape in formas_selecionadas)
        momento_total = sum(shape.body.moment for shape in formas_selecionadas)
        novo_corpo = pymunk.Body(massa_total, momento_total)
        
        pos_x = sum(shape.body.position.x for shape in formas_selecionadas) / len(formas_selecionadas)
        pos_y = sum(shape.body.position.y for shape in formas_selecionadas) / len(formas_selecionadas)
        novo_corpo.position = (pos_x, pos_y)
        
        for i in range(len(formas_selecionadas)):
            for j in range(i + 1, len(formas_selecionadas)):
                junta = pymunk.PinJoint(formas_selecionadas[i].body, formas_selecionadas[j].body)
                space.add(junta)
        
        formas_selecionadas.clear()

    # Criar paredes
    chao_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    chao_shape = pymunk.Segment(chao_body, (0, HEIGHT-10), (WIDTH, HEIGHT-10), 5)
    parede_esq = pymunk.Segment(chao_body, (0, 0), (0, HEIGHT), 5)
    parede_dir = pymunk.Segment(chao_body, (WIDTH, 0), (WIDTH, HEIGHT), 5)
    teto = pymunk.Segment(chao_body, (0, 0), (WIDTH, 0), 5)

    space.add(chao_body)
    for parede in [chao_shape, parede_esq, parede_dir, teto]:
        parede.elasticity = 0.8
        parede.friction = 0.5
        space.add(parede)

    # Loop do jogo
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Tecla ESC para voltar ao menu
                    return "menu"
                elif event.key == pygame.K_SPACE or event.key == pygame.K_e:
                    forma_atual = (forma_atual + 1) % len(formas)
                elif event.key == pygame.K_c:
                    nova_cor = escolher_cor()
                    if nova_cor:
                        cor_atual = nova_cor
                        if formas_selecionadas:
                            for shape in formas_selecionadas:
                                shape.color = nova_cor
                elif event.key == pygame.K_s:
                    modo_selecao = not modo_selecao
                    if not modo_selecao:
                        formas_selecionadas.clear()
                elif event.key == pygame.K_j and modo_selecao:
                    unir_formas()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if modo_selecao:
                        mouse_pos = event.pos
                        for shape in space.shapes:
                            if isinstance(shape, (pymunk.Circle, pymunk.Poly)):
                                info = shape.point_query(mouse_pos)
                                if info.distance < 0:
                                    if shape not in formas_selecionadas:
                                        formas_selecionadas.append(shape)
                                        break
                    else:
                        pos = event.pos
                        if formas[forma_atual] == "quadrado":
                            criar_quadrado(pos)
                        elif formas[forma_atual] == "circulo":
                            criar_circulo(pos)
                        elif formas[forma_atual] == "triangulo":
                            criar_triangulo(pos)
                elif event.button == 3:
                    mouse_pos = event.pos
                    for shape in space.shapes:
                        if isinstance(shape, (pymunk.Circle, pymunk.Poly)):
                            info = shape.point_query(mouse_pos)
                            if info.distance < 0:
                                objeto_arrastado = shape.body
                                mouse_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
                                mouse_body.position = mouse_pos
                                mouse_joint = pymunk.PivotJoint(mouse_body, objeto_arrastado, (0, 0), (0, 0))
                                mouse_joint.max_force = 50000
                                space.add(mouse_body, mouse_joint)
                                break
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3 and mouse_joint is not None:
                    space.remove(mouse_joint)
                    space.remove(mouse_body)
                    mouse_joint = None
                    mouse_body = None
                    objeto_arrastado = None
            elif event.type == pygame.MOUSEMOTION:
                if mouse_body is not None:
                    mouse_body.position = event.pos

        # Atualizar física
        space.step(1/60.0)
        
        # Desenhar
        screen.fill(PRETO)
        
        # Desenhar todas as formas
        for shape in space.shapes:
            if isinstance(shape, pymunk.Circle):
                pos = shape.body.position
                cor = shape.color if hasattr(shape, 'color') else AZUL
                pygame.draw.circle(screen, cor, (int(pos.x), int(pos.y)), int(shape.radius))
            elif isinstance(shape, pymunk.Segment):
                pygame.draw.line(screen, BRANCO, shape.a, shape.b, 5)
            elif isinstance(shape, pymunk.Poly):
                vertices = [(shape.body.position.x + v.rotated(shape.body.angle).x, 
                           shape.body.position.y + v.rotated(shape.body.angle).y) 
                          for v in shape.get_vertices()]
                cor = shape.color if hasattr(shape, 'color') else VERMELHO
                pygame.draw.polygon(screen, cor, vertices)

        # Destacar formas selecionadas
        for shape in formas_selecionadas:
            if isinstance(shape, pymunk.Circle):
                pos = shape.body.position
                pygame.draw.circle(screen, VERDE, (int(pos.x), int(pos.y)), int(shape.radius) + 2, 2)
            elif isinstance(shape, pymunk.Poly):
                vertices = [(shape.body.position.x + v.rotated(shape.body.angle).x, 
                           shape.body.position.y + v.rotated(shape.body.angle).y) 
                          for v in shape.get_vertices()]
                pygame.draw.polygon(screen, VERDE, vertices, 2)

        # Interface
        fonte = pygame.font.Font(None, 36)
        texto = fonte.render(f"Forma atual: {formas[forma_atual]}", True, VERDE)
        screen.blit(texto, (10, 10))
        
        modo_texto = "Modo: Seleção" if modo_selecao else "Modo: Criação"
        texto_modo = fonte.render(modo_texto, True, VERDE)
        screen.blit(texto_modo, (10, 50))
        
        pygame.display.flip()
        clock.tick(60)

    return "menu"

# Loop principal do programa
estado_atual = "menu"

while True:
    if estado_atual == "menu":
        estado_atual = menu_principal()
    elif estado_atual == "play":
        estado_atual = jogo_principal()
    elif estado_atual == "como_jogar":
        estado_atual = tela_como_jogar()
