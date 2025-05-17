# fase_semente.py

import pygame
import os
from tank_semente import TankSemente
from obstacles      import Obstacle
from camera         import Camera

def iniciar_fase_semente(screen):
    pygame.init()
    clock = pygame.time.Clock()
    sw, sh = screen.get_size()

    # — Ajuste fino da altura dos rombos —
    HOLE_VERTICAL_SHIFT = -50  # positivo desce; negativo sobe

    # — Carrega camadas de background —
    base            = os.path.dirname(__file__)
    seed_bg_dir     = os.path.join(base, 'assets', 'seed_bg')
    layer_files     = [
        'Layer_0011_0.png','Layer_0010_1.png','Layer_0009_2.png',
        'Layer_0008_3.png','Layer_0007_Lights.png','Layer_0006_4.png',
        'Layer_0005_5.png','Layer_0004_Lights.png','Layer_0003_6.png',
        'Layer_0002_7.png','Layer_0001_8.png','Layer_0000_9.png'
    ]
    parallax_factors = [0.1,0.15,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1]

    bg_layers = []
    for fname, fac in zip(layer_files, parallax_factors):
        surf = pygame.image.load(os.path.join(seed_bg_dir, fname)).convert_alpha()
        bg_layers.append((surf, fac))
    # — Fim do carregamento —

    # — Cria e posiciona o Tanque —
    tmp     = TankSemente(0, 0)
    tank_y  = 500
    tank    = TankSemente(100, tank_y)

    # — Calcula o Y dos buracos —
    hole_base_y = 530 + HOLE_VERTICAL_SHIFT

    # — Instancia obstáculos “rombo” (buraco) —
    obstacles = [
        Obstacle(x, hole_base_y, 96, 142, 'buraco')
        for x in (350, 750, 1150)
    ]

    cam = Camera(level_width=1600, level_height=600)

    # — Carrega sprite da plataforma (arbusto) —
    bush_surf = pygame.image.load(
        os.path.join(base, 'assets','enemies','semente','bush_seed.png')
    ).convert_alpha()

    # — Parâmetro de alcance para plantar —
    PLANT_RANGE = 50  # o tanque deve estar a ≤50px do centro do rombo

    # — Lista de plataformas geradas —
    platforms = []

    # — Loop principal —
    while True:
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN and e.key == pygame.K_x:
                for obs in list(obstacles):
                    if obs.kind == 'buraco' and tank.rect.colliderect(obs.rect):
                        # Aumenta o tamanho da plataforma para cobrir bem o buraco
                        largura = int(obs.rect.width * 1.5)   # 50% maior que o buraco
                        altura  = int(obs.rect.height * 1.2)  # um pouco mais alto
                        x = obs.rect.centerx - largura // 2
                        y = obs.rect.centery - altura // 2
                        plat = pygame.Rect(x, y, largura, altura)
                        platforms.append(plat)
                        obstacles.remove(obs)

        # — Atualiza tanque e câmera —
        keys = pygame.key.get_pressed()
        tank.handle_input(keys)
        tank.update()
        cam.update(tank.rect)

        # — Queda: se bater no rombo sem plataforma, morre —
        caiu_no_buraco = False
        for obs in obstacles:
            if obs.kind == 'buraco' and tank.rect.colliderect(obs.rect):
                caiu_no_buraco = True
        for plat in platforms:
            if tank.rect.colliderect(plat):
                caiu_no_buraco = False
        if caiu_no_buraco:
            return  # game over

        # — Desenha parallax em loop infinito —
        screen.fill((0,0,0))
        for surf, fac in bg_layers:
            w      = surf.get_width()
            offset = int(cam.offset * fac) % w
            y_pos  = sh - surf.get_height()
            screen.blit(surf, (-offset,    y_pos))
            screen.blit(surf, ( w-offset,  y_pos))

        # — Desenha rombos (buracos) —
        for obs in obstacles:
            obs.draw(screen, cam.offset)

        # — Desenha as plataformas plantadas —
        for plat in platforms:
            screen.blit(bush_surf, (plat.x - cam.offset, plat.y))

        # — Desenha o tanque por último —
        tank.draw(screen, cam.offset)

        pygame.display.flip()
        clock.tick(60)
