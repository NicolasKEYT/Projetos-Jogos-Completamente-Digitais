#Diego Estevão Lopes de Queiroz - 10419038
#Nicolas Gonçalves Santos - 10418047
#Kauã Paixão - 10418548
import pygame
import os
from fase_sol import iniciar_fase_sol
from fase_semente import iniciar_fase_semente
from fase_agua import iniciar_fase_agua
from ranking import mostrar_ranking

BASE_DIR = os.path.dirname(__file__)

def tocar_musica_menu():
    # Toca a música de fundo do menu, se não estiver tocando
    musica_path = os.path.join(BASE_DIR, 'assets', 'sons', 'musica_bg.wav')
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.load(musica_path)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)

def mostrar_menu(screen):
    # Exibe o menu principal com botões para cada fase
    tocar_musica_menu()
    clock = pygame.time.Clock()
    sw, sh = screen.get_size()
    menu_img = pygame.image.load("TanquesDaTerra/assets/ui/ui_menu.png").convert_alpha()
    menu_img = pygame.transform.scale(menu_img, (sw, sh))

    # Defina as áreas dos botões 
    btn_sol = pygame.Rect(40, 90, 700, 110)
    btn_agua = pygame.Rect(40, 230, 700, 110)
    btn_semente = pygame.Rect(40, 370, 700, 110)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                from main import inputar_nome  # Importação tardia para evitar import circular
                inputar_nome(screen)
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if btn_sol.collidepoint(e.pos):
                    return iniciar_fase_sol
                if btn_agua.collidepoint(e.pos):
                    return iniciar_fase_agua
                if btn_semente.collidepoint(e.pos):
                    return iniciar_fase_semente

        screen.fill((30,30,30))
        screen.blit(menu_img, (0, 0))
        pygame.display.flip()
        clock.tick(60)

def mostrar_pagina_inicial(screen):
    # Exibe a página inicial com uma breve introdução
    tocar_musica_menu()
    clock = pygame.time.Clock()
    sw, sh = screen.get_size() 
    pagina_img = pygame.image.load("TanquesDaTerra/assets/ui/ui_page.png").convert_alpha()
    pagina_img = pygame.transform.scale(pagina_img, (sw, sh))

    pygame.font.init()
    pixel_font_path = os.path.join(BASE_DIR, 'assets', 'fonts', 'pixel.ttf')
    fonte = pygame.font.Font(pixel_font_path, 12)
    legenda_texto = [
        "O planeta está sendo tomado por poluição e destruição ambiental.",
        "Três tanques criados por cientistas foram ativados para restaurar",
        "o equilíbrio da Terra, cada um com uma missão específica."
    ]
    legendas = [fonte.render(linha, True, (255, 255, 255)) for linha in legenda_texto]
    legenda_rects = [legenda.get_rect(center=(sw//2, 520 + i*32)) for i, legenda in enumerate(legendas)]

    mostrar_legenda = True

    while True:
        dt = clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); exit()
            if (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1) or \
               (e.type == pygame.KEYDOWN and e.key != pygame.K_ESCAPE):
                mostrar_pagina_intermediaria(screen)
                return
        screen.fill((0,0,0))
        screen.blit(pagina_img, (0, 0))
        if mostrar_legenda:
            for legenda, rect in zip(legendas, legenda_rects):
                screen.blit(legenda, rect)
        pygame.display.flip()

def mostrar_pagina_init(screen):
    # Exibe a tela de seleção inicial: escolher tanque, ranking ou sair
    tocar_musica_menu()
    clock = pygame.time.Clock()

    # Carregue as imagens dos botões
    img_escolher = pygame.image.load("TanquesDaTerra/assets/ui/escolher_tanque.png").convert_alpha()
    img_ranking = pygame.image.load("TanquesDaTerra/assets/ui/ranking.png").convert_alpha()
    img_sair = pygame.image.load("TanquesDaTerra/assets/ui/sair.png").convert_alpha()

    # Redimensione se necessário 
    img_escolher = pygame.transform.scale(img_escolher, (640, 140))
    img_ranking = pygame.transform.scale(img_ranking, (640, 140))
    img_sair = pygame.transform.scale(img_sair, (640, 140))

    # Defina as posições dos botões
    pos_x = 80
    pos_y_escolher = 60
    pos_y_ranking = 230
    pos_y_sair = 400

    # Crie os retângulos para detecção de clique
    btn_escolher = pygame.Rect(pos_x, pos_y_escolher, 640, 140)
    btn_ranking  = pygame.Rect(pos_x, pos_y_ranking, 640, 140)
    btn_sair     = pygame.Rect(pos_x, pos_y_sair, 640, 140)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                mostrar_pagina_intermediaria(screen)
                return
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if btn_escolher.collidepoint(e.pos):
                    return
                if btn_ranking.collidepoint(e.pos):
                    mostrar_ranking(screen)
                if btn_sair.collidepoint(e.pos):
                    pygame.quit(); exit()

        screen.fill((20, 30, 30))  # Fundo escuro
        # Desenhe os botões
        screen.blit(img_escolher, (pos_x, pos_y_escolher))
        screen.blit(img_ranking, (pos_x, pos_y_ranking))
        screen.blit(img_sair, (pos_x, pos_y_sair))
        pygame.display.flip()
        clock.tick(60)

def mostrar_pagina_intermediaria(screen):
    # Exibe uma página intermediária antes da seleção de tanque
    tocar_musica_menu()
    clock = pygame.time.Clock()
    sw, sh = screen.get_size()
    bg_img = pygame.image.load(os.path.join("TanquesDaTerra", "assets", "ui", "ui_page2.png")).convert_alpha()
    bg_img = pygame.transform.scale(bg_img, (sw, sh))

    # Área de clique do botão "Iniciar" 
    btn_largura, btn_altura = 380, 80
    btn_x = (sw - btn_largura) // 2
    btn_y = sh - 130
    btn_iniciar = pygame.Rect(btn_x, btn_y, btn_largura, btn_altura)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                mostrar_pagina_inicial(screen)
                return
            if (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1):
                mostrar_pagina_init(screen)
                return

        screen.blit(bg_img, (0, 0))
        pygame.display.flip()
        clock.tick(60)