# fase_sol.py

import pygame
import os
from tank_sol import TankSol
from obstacles import Obstacle
from camera import Camera

def iniciar_fase_sol(screen):
    pygame.init()
    clock = pygame.time.Clock()
    sw, sh = screen.get_size()

    # —————— Configuração de deslocamentos verticais ——————
    BG_VERTICAL_SHIFT     = 250   # background
    TANK_VERTICAL_SHIFT   = 240     # tanque
    ENEMY_VERTICAL_SHIFT  = 200  # inimigos

    # 1) Ordem fixa das layers, do fundo para frente
    layer_files = [
        'Hills Layer 01.png',
        'Hills Layer 02.png',
        'Hills Layer 03.png',
        'Hills Layer 04.png',
        'Hills Layer 05.png',  # chão visual
        'Hills Layer 06.png'   # primeiro plano
    ]
    parallax_factors = [0.2, 0.35, 0.5, 0.7, 0.9, 1.1]

    # 2) Carrega as imagens de background
    base   = os.path.dirname(__file__)
    bg_dir = os.path.join(base, 'assets', 'sol_bg')
    bg_layers = []
    for fname, fac in zip(layer_files, parallax_factors):
        surf = pygame.image.load(os.path.join(bg_dir, fname)).convert_alpha()
        bg_layers.append((surf, fac))

    # 3) Calcula o floor_base (pé do chão sem deslocamentos)
    ground_idx  = layer_files.index('Hills Layer 05.png')
    ground_surf = bg_layers[ground_idx][0]
    floor_base  = sh - ground_surf.get_height()

    # 4) Aplica cada deslocamento
    floor_bg    = floor_base + BG_VERTICAL_SHIFT
    floor_tank  = floor_base + TANK_VERTICAL_SHIFT
    floor_enemy = floor_base + ENEMY_VERTICAL_SHIFT

    # 5) Cria obstáculos posicionados em floor_enemy
    obstacles = [
        Obstacle(400,  floor_enemy, 40, 40, 'inimigo'),
        Obstacle(700,  floor_enemy, 40, 40, 'inimigo'),
        Obstacle(1100, floor_enemy, 40, 40, 'inimigo'),
    ]

    # 6) Cria o tanque posicionado em floor_tank
    tmp    = TankSol(0, 0)
    tank_y = floor_tank - tmp.image.get_height()
    tank   = TankSol(100, tank_y)

    cam = Camera(level_width=1600, level_height=sh)

    # —————— Loop principal ——————
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return

        # 7) Atualiza input e lógica
        keys = pygame.key.get_pressed()
        tank.handle_input(keys)
        tank.update()
        for o in obstacles:
            o.update()
        cam.update(tank.rect)

        # 8) Desenha sky de fundo
        sky_color = bg_layers[0][0].get_at((0, 0))
        screen.fill(sky_color)

        # 9) Desenha cada layer alinhada a floor_bg
        for surf, fac in bg_layers:
            w      = surf.get_width()
            offset = int(cam.offset * fac) % w
            y_pos  = floor_bg - surf.get_height()
            screen.blit(surf, (-offset, y_pos))
            screen.blit(surf, (w - offset, y_pos))

        # 10) Desenha inimigos em floor_enemy
        for o in obstacles:
            o.rect.y = floor_enemy
            o.draw(screen, cam.offset)

        # 11) Desenha tanque em floor_tank
        tank.rect.y = floor_tank - tank.image.get_height()
        tank.draw(screen, cam.offset)

        pygame.display.flip()
        clock.tick(60)
