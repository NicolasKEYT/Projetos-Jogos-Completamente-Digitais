# fase_semente.py

import pygame
import os
from tank_semente import TankSemente
from obstacles import Obstacle
from camera import Camera

def iniciar_fase_semente(screen):
    clock = pygame.time.Clock()

    # --- Carregamento das camadas de background (dentro da função) ---
    base = os.path.dirname(__file__)
    layer_files = [
        'Layer_0011_0.png','Layer_0010_1.png','Layer_0009_2.png',
        'Layer_0008_3.png','Layer_0007_Lights.png','Layer_0006_4.png',
        'Layer_0005_5.png','Layer_0004_Lights.png','Layer_0003_6.png',
        'Layer_0002_7.png','Layer_0001_8.png','Layer_0000_9.png'
    ]
    parallax_factors = [0.1,0.15,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1]
    bg_layers = []
    for fname, fac in zip(layer_files, parallax_factors):
        path = os.path.join(base, 'assets', 'seed_bg', fname)
        surf = pygame.image.load(path).convert_alpha()
        bg_layers.append((surf, fac))
    # --- Fim do carregamento ---

    # --- Instâncias de jogo ---
    tank      = TankSemente(100, 500)
    obstacles = [Obstacle(x, 530, 80, 30, 'buraco') for x in (350, 750, 1150)]
    cam       = Camera(level_width=1600, level_height=600)

    # --- Loop principal ---
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return  # retorna ao menu

        # Atualizações
        keys = pygame.key.get_pressed()
        tank.handle_input(keys)
        tank.update()
        cam.update(tank.rect)

        # --- Desenha parallax em loop infinito ---
        screen.fill((0,0,0))
        screen_w = screen.get_width()
        screen_h = screen.get_height()
        for layer_surf, fac in bg_layers:
            layer_w = layer_surf.get_width()
            # calcula deslocamento com wrap
            offset = int(cam.offset * fac) % layer_w
            y_pos  = screen_h - layer_surf.get_height()
            # desenha duas vezes para cobrir toda a largura
            screen.blit(layer_surf, (-offset, y_pos))
            screen.blit(layer_surf, (layer_w - offset, y_pos))

        # --- Desenha obstáculos e tanque ---
        for obs in obstacles:
            obs.draw(screen, cam.offset)
        tank.draw(screen, cam.offset)

        # Flip e tick
        pygame.display.flip()
        clock.tick(60)
