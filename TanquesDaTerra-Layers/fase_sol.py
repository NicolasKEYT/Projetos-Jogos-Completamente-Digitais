import pygame
import os
from tank_sol import TankSol
from obstacles import Obstacle
from camera import Camera

def iniciar_fase_sol(screen):
    clock = pygame.time.Clock()
    sw, sh = screen.get_size()

    # Carrega e ordena os PNGs do sol_bg
    base   = os.path.dirname(__file__)
    bg_dir = os.path.join(base, 'assets', 'sol_bg')
    fnames = sorted(
        [f for f in os.listdir(bg_dir) if f.lower().endswith('.png')],
        key=lambda x: x  # já estão nomeados em ordem numérica ("01.png", etc.)
    )

    # Fatores de parallax de 0.2 a 1.1
    n = len(fnames)
    parallax = [0.2 + 0.9 * i/(n-1) for i in range(n)]

    # Carrega layers
    bg_layers = []
    for fname, fac in zip(fnames, parallax):
        surf = pygame.image.load(os.path.join(bg_dir, fname)).convert_alpha()
        bg_layers.append((surf, fac))

    # Usa o índice 4 (5ª camada) como chão
    ground_layer_index = 4
    ground = bg_layers[ground_layer_index][0]
    floor_y = sh - ground.get_height()

    # Obstáculos sobre o chão
    obstacles = [
        Obstacle(400, floor_y,  40, 40, 'inimigo'),
        Obstacle(700, floor_y,  40, 40, 'inimigo'),
        Obstacle(1100,floor_y,  40, 40, 'inimigo'),
    ]

    # Tanque posicionado no chão
    tmp    = TankSol(0,0)
    tank_y = floor_y - tmp.image.get_height()
    tank   = TankSol(100, tank_y)

    cam = Camera(level_width=1600, level_height=sh)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return

        keys = pygame.key.get_pressed()
        tank.handle_input(keys); tank.update(); cam.update(tank.rect)

        # Fundo (sky)
        sky = bg_layers[0][0].get_at((0,0))
        screen.fill(sky)

        # Desenha parallax
        for surf, fac in bg_layers:
            w   = surf.get_width()
            off = int(cam.offset * fac) % w
            y0  = sh - surf.get_height()
            screen.blit(surf, (-off, y0))
            screen.blit(surf, (w-off, y0))

        # Desenha obstáculos e tanque
        for o in obstacles: o.draw(screen, cam.offset)
        tank.draw(screen, cam.offset)

        pygame.display.flip()
        clock.tick(60)
