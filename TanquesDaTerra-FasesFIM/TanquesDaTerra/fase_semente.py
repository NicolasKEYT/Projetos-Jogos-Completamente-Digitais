import pygame
import os
import time
from tank_semente import TankSemente
from obstacles import Obstacle
from camera import Camera


def iniciar_fase_semente(screen):
    pygame.init()
    clock = pygame.time.Clock()
    sw, sh = screen.get_size()

    # — Ajuste fino da altura dos rombos —
    HOLE_VERTICAL_SHIFT = -50  # positivo desce; negativo sobe

    # — Carrega camadas de background —
    base        = os.path.dirname(__file__)
    seed_bg_dir = os.path.join(base, 'assets', 'seed_bg')
    layer_files = [
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

    # — Cria e posiciona o Tanque —
    tmp = TankSemente(0, 0)
    tank_y = 500
    tank   = TankSemente(100, tank_y)

    # — Calcula o Y dos buracos —
    hole_base_y = 530 + HOLE_VERTICAL_SHIFT

    # — Instancia obstáculos “rombo” (buraco) —
    obstacles = [
        Obstacle(x, hole_base_y, 80, 120, 'buraco')
        for x in (350, 750, 1150)
    ]

    # — Lista de plataformas geradas —
    platforms = []

    # — Câmera para fase infinita —
    cam = Camera(level_width=10**9, level_height=600)

    # — Carrega sprite da plataforma (arbusto) —
    bush_surf = pygame.image.load(
        os.path.join(base, 'assets','enemies','semente','bush_seed.png')
    ).convert_alpha()

    # — Alcance de plantio —
    PLANT_RANGE = 30  # px de distância do centro do buraco

    # — Loop principal —
    start_time = time.time()
    TIME_LIMIT = 20.0  # segundos para acabar a fase

    while True:
        # Verifica fim por tempo
        elapsed = time.time() - start_time
        if elapsed >= TIME_LIMIT:
            return  # fim da fase por tempo

        # Controla FPS e obtém dt
        dt = clock.tick(60) / 1000.0

        # Eventos
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                exit()

        # Atualiza tanque e câmera
        keys = pygame.key.get_pressed()
        tank.handle_input(keys)
        tank.update()
        cam.update(tank.rect)

        # Plantio contínuo (X pressionado)
        if keys[pygame.K_x]:
            for obs in list(obstacles):
                if obs.kind == 'buraco' and tank.rect.colliderect(obs.rect):
                    # cria passagem: retângulo verde de teste
                    largura = int(obs.rect.width * 1.5)
                    altura  = int(obs.rect.height * 1.2)
                    px = obs.rect.centerx - largura // 2
                    py = obs.rect.centery - altura // 2
                    plat = pygame.Rect(px, py, largura, altura)
                    platforms.append(plat)
                    obstacles.remove(obs)

        # Colisão com buraco sem plataforma: impede passagem
        for obs in obstacles:
            if obs.kind == 'buraco' and tank.rect.colliderect(obs.rect):
                if tank.rect.centerx < obs.rect.centerx:
                    tank.rect.right = obs.rect.left
                else:
                    tank.rect.left = obs.rect.right
                break

        # Desenha parallax
        screen.fill((0,0,0))
        for surf, fac in bg_layers:
            w = surf.get_width()
            offset = int(cam.offset * fac) % w
            y_pos = sh - surf.get_height()
            screen.blit(surf, (-offset, y_pos))
            screen.blit(surf, (w - offset, y_pos))

        # Desenha buracos
        for obs in obstacles:
            obs.draw(screen, cam.offset)

        # Desenha plataformas criadas (verde)
        for plat in platforms:
            pygame.draw.rect(screen, (0,200,0), plat.move(-cam.offset, 0))

        # Desenha tanque por último (camada superior)
        tank.draw(screen, cam.offset)

        # Placar: tempo e sementes plantadas
        font = pygame.font.SysFont("arialblack", 20, bold=True)
        text_time = f"Tempo: {elapsed:.1f}s"
        text_seed = f"Sementes: {len(platforms)}"
        screen.blit(font.render(text_time, True, (255,255,255)), (10, 10))
        screen.blit(font.render(text_seed, True, (255,255,255)), (10, 40))

        pygame.display.flip()
