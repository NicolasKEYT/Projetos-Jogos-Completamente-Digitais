import pygame
from fase_sol import iniciar_fase_sol
from fase_semente import iniciar_fase_semente
from fase_agua import iniciar_fase_agua
from ranking import mostrar_ranking

def mostrar_menu(screen):
    clock = pygame.time.Clock()
    sw, sh = screen.get_size()
    menu_img = pygame.image.load("TanquesDaTerra/assets/ui/ui_menu.png").convert_alpha()
    menu_img = pygame.transform.scale(menu_img, (sw, sh))

    # Defina as áreas dos botões (ajuste conforme o layout da imagem)
    btn_sol = pygame.Rect(40, 90, 700, 110)      # x, y, largura, altura
    btn_agua = pygame.Rect(40, 230, 700, 110)
    btn_semente = pygame.Rect(40, 370, 700, 110)

    pygame.draw.rect(screen, (255,255,0), btn_sol, 2)
    pygame.draw.rect(screen, (0,255,255), btn_agua, 2)
    pygame.draw.rect(screen, (0,255,0), btn_semente, 2)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if btn_sol.collidepoint(e.pos):
                    return iniciar_fase_sol
                if btn_agua.collidepoint(e.pos):
                    return iniciar_fase_agua
                if btn_semente.collidepoint(e.pos):
                    return iniciar_fase_semente

        screen.fill((30,30,30))
        screen.blit(menu_img, (0, 0))
        # Opcional: desenhe retângulos dos botões para depuração
        # pygame.draw.rect(screen, (255,255,0), btn_sol, 2)
        # pygame.draw.rect(screen, (0,255,255), btn_agua, 2)
        # pygame.draw.rect(screen, (0,255,0), btn_semente, 2)
        pygame.display.flip()
        clock.tick(60)

def mostrar_pagina_inicial(screen):
    clock = pygame.time.Clock()
    sw, sh = screen.get_size() 
    pagina_img = pygame.image.load("TanquesDaTerra/assets/ui/ui_page.png").convert_alpha()
    pagina_img = pygame.transform.scale(pagina_img, (sw, sh))

    pygame.font.init()
    fonte = pygame.font.SysFont("Arial", 20, bold=True)
    legenda = fonte.render("APERTE QUALQUER TECLA PARA INICIAR", True, (255, 255, 255))
    legenda_rect = legenda.get_rect(center=(400, 550))

    mostrar_legenda = True
    tempo_legenda = 0
    intervalo = 800  # milissegundos (1 segundo para piscar, 1 segundos = 1000 milissegundos)

    while True:
        dt = clock.tick(60)
        tempo_legenda += dt
        if tempo_legenda >= 800:
            mostrar_legenda = not mostrar_legenda
            tempo_legenda = 0

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); exit()
            if e.type == pygame.KEYDOWN or (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1):
                mostrar_pagina_init(screen)
                return
        screen.fill((0,0,0))
        screen.blit(pagina_img, (0, 0))
        if mostrar_legenda:
            screen.blit(legenda, legenda_rect)
        pygame.display.flip()

def mostrar_pagina_init(screen):
    clock = pygame.time.Clock()

    # Carregue as imagens dos botões
    img_escolher = pygame.image.load("TanquesDaTerra/assets/ui/escolher_tanque.png").convert_alpha()
    img_ranking = pygame.image.load("TanquesDaTerra/assets/ui/ranking.png").convert_alpha()
    img_sair = pygame.image.load("TanquesDaTerra/assets/ui/sair.png").convert_alpha()

    # Redimensione se necessário (ajuste conforme o tamanho desejado)
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