# fase_agua.py

import pygame
import os
from tank_agua import TankAgua
from obstacles import Obstacle
from camera import Camera

def iniciar_fase_agua(screen):
    clock = pygame.time.Clock()
    sw, sh = screen.get_size()

    # ——— Ajuste este valor para mover TODO o cenário verticalmente ———
    # valores NEGATIVOS movem o cenário para CIMA; positivos para BAIXO
    VERTICAL_SHIFT = 250

    # 1) Carrega e ordena os PNGs em assets/agua_bg
    base   = os.path.dirname(__file__)
    bg_dir = os.path.join(base, 'assets', 'agua_bg')
    filenames = sorted(
        [f for f in os.listdir(bg_dir) if f.lower().endswith('.png')],
        key=lambda x: int(os.path.splitext(x)[0]) 
                      if os.path.splitext(x)[0].isdigit() else float('inf')
    )

    # 2) Gera fatores de parallax de 0.2 a 1.1
    num = len(filenames)
    parallax_factors = [0.2 + 0.9 * i/(num-1) for i in range(num)]

    # 3) Carrega cada layer SEM escalar
    bg_layers = []
    for fname, fac in zip(filenames, parallax_factors):
        surf = pygame.image.load(os.path.join(bg_dir, fname)).convert_alpha()
        bg_layers.append((surf, fac))

    # 4) Usa o índice 13 (14ª camada) como solo
    ground_surf = bg_layers[13][0]
    # floor_y original é sh - altura_do_solo; com shift:
    floor_y = (sh - ground_surf.get_height()) + VERTICAL_SHIFT

    # 5) Instancia obstáculos apoiados no novo floor_y
    obstacles = [
        Obstacle(400,  floor_y, 40, 40, 'lixo'),
        Obstacle(700,  floor_y, 40, 40, 'fogo'),
        Obstacle(1000, floor_y, 40, 40, 'lixo'),
        Obstacle(1300, floor_y, 40, 40, 'fogo'),
    ]

    # 6) Cria o tanque colado ao new floor_y
    tmp    = TankAgua(0, 0)
    tank_y = floor_y - tmp.image.get_height()
    tank   = TankAgua(100, tank_y)

    cam = Camera(level_width=1600, level_height=sh)

    # --- Loop principal ---
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return

        # Atualiza lógica
        keys = pygame.key.get_pressed()
        tank.handle_input(keys)
        tank.update()
        cam.update(tank.rect)

        # 7) Desenha sky de fundo
        sky_color = bg_layers[0][0].get_at((0, 0))
        screen.fill(sky_color)

        # 8) Desenha cada layer com parallax, base alinhada ao shifted floor_y
        for surf, fac in bg_layers:
            w      = surf.get_width()
            offset = int(cam.offset * fac) % w
            # y_pos agora usa floor_y que já inclui VERTICAL_SHIFT
            y_pos = floor_y - surf.get_height()
            screen.blit(surf, (-offset, y_pos))
            screen.blit(surf, (w - offset, y_pos))

        # 9) Desenha obstáculos e tanque em cima desse mesmo floor_y
        for obs in obstacles:
            obs.draw(screen, cam.offset)
        tank.draw(screen, cam.offset)

        pygame.display.flip()
        clock.tick(60)
