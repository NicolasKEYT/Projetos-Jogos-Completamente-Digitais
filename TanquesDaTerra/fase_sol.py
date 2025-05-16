# fase_sol.py

import pygame
import os
import random
from tank_sol import TankSol
from obstacles import Obstacle
from camera import Camera

def iniciar_fase_sol(screen):
    pygame.init()
    clock = pygame.time.Clock()
    sw, sh = screen.get_size()

    # —————— Deslocamentos verticais independentes ——————
    BG_VERTICAL_SHIFT     = 260   # só move o background
    TANK_VERTICAL_SHIFT   = 250   # só move o tanque
    ENEMY_VERTICAL_SHIFT  = 250   # só move os inimigos

    # 1) Ordem fixa das 6 camadas (Fundo → Primeiro plano)
    layer_files = [
        'Hills Layer 01.png',
        'Hills Layer 02.png',
        'Hills Layer 03.png',
        'Hills Layer 04.png',
        'Hills Layer 05.png',  # chão visual
        'Hills Layer 06.png'   # primeiro plano
    ]
    parallax_factors = [0.2, 0.35, 0.5, 0.7, 0.9, 1.1]

    # 2) Carrega cada layer em memória
    base   = os.path.dirname(__file__)
    bg_dir = os.path.join(base, 'assets', 'sol_bg')
    bg_layers = []
    for fname, fac in zip(layer_files, parallax_factors):
        surf = pygame.image.load(os.path.join(bg_dir, fname)).convert_alpha()
        bg_layers.append((surf, fac))

    # 3) Calcula o piso “puro” (sem deslocamentos) usando a layer 05
    ground_idx  = layer_files.index('Hills Layer 05.png')
    ground_surf = bg_layers[ground_idx][0]
    floor_base  = sh - ground_surf.get_height()

    # 4) Aplica cada deslocamento vertical
    floor_bg    = floor_base + BG_VERTICAL_SHIFT
    floor_tank  = floor_base + TANK_VERTICAL_SHIFT
    floor_enemy = floor_base + ENEMY_VERTICAL_SHIFT

    # 5) Instancia o TankSol posicionado em floor_tank
    tmp     = TankSol(0, 0)
    tank_y  = floor_tank - tmp.image.get_height()
    tank    = TankSol(100, tank_y)

    # — Parâmetros de gameplay —
    spawn_margin     = 50    # px fora da tela para spawn
    enemy_speed      = 1     # velocidade lenta
    FLAME_RANGE      = 100
    FLAME_DAMAGE     = 20
    FLAME_INTERVAL   = 1.0
    kill_count       = 0
    death_since_spawn= 0

    cam = Camera(level_width=1600, level_height=sh)

    # — Função para spawnar 3 inimigos fora da visão —
    def spawn_enemies(n=3):
        enemies = []
        for _ in range(n):
            side = random.choice(['left','right'])
            if side == 'left':
                ex = -spawn_margin - random.randint(0, spawn_margin)
                dir_mult = 1
            else:
                ex = 1600 + spawn_margin + random.randint(0, spawn_margin)
                dir_mult = -1

            o = Obstacle(ex, floor_enemy, 40, 60, 'inimigo', sprite_name='inimigo_sol1')
            o.speed       = enemy_speed
            o.dir         = dir_mult
            o.touch_timer = 0.0
            # Ajuste: alinhar base do inimigo ao chão
            o.rect.y = floor_enemy - o.rect.height
            enemies.append(o)
        return enemies

    obstacles = spawn_enemies()

    # — Loop principal —
    while True:
        dt = clock.tick(60) / 1000.0

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return

        # 6) Atualiza jogador
        keys = pygame.key.get_pressed()
        tank.handle_input(keys)
        tank.update()
        # **sem limite** de movimento do tanque

        # 7) Atualiza inimigos rumo ao jogador
        for o in obstacles:
            o.dir = 1 if o.rect.centerx < tank.rect.centerx else -1
            o.rect.x += o.dir * o.speed

        # 8) Colisão projétil → inimigo
        for b in list(tank.bullets):
            for o in list(obstacles):
                if b.rect.colliderect(o.rect):
                    o.take_damage(TankSol.DAMAGE)
                    tank.bullets.remove(b)
                    if o.health <= 0:
                        obstacles.remove(o)
                        kill_count += 1
                        death_since_spawn += 1
                    break

        # 9) Dano de chama quando próximo
        for o in obstacles:
            if abs(o.rect.centerx - tank.rect.centerx) <= FLAME_RANGE:
                fx = o.rect.left - 20 if o.dir < 0 else o.rect.right
                flame = pygame.Rect(fx, o.rect.y, 20, o.rect.height)
                pygame.draw.rect(screen, (255,100,0), flame.move(-cam.offset, 0))
                o.touch_timer += dt
                if o.touch_timer >= FLAME_INTERVAL:
                    tank.health -= FLAME_DAMAGE
                    o.touch_timer -= FLAME_INTERVAL
            else:
                o.touch_timer = 0.0

        # 10) Respawn de 3 inimigos a cada 2 mortes
        if death_since_spawn >= 2:
            obstacles.extend(spawn_enemies())
            death_since_spawn = 0

        # 11) Fim de jogo: 15 kills ou vida do jogador zero
        if tank.health <= 0:
            return

        cam.update(tank.rect)

        # — Desenha cena —

        # 12) Céu
        sky_color = bg_layers[0][0].get_at((0, 0))
        screen.fill(sky_color)

        # 13) Parallax em loop (dois blits)
        for surf, fac in bg_layers:
            w      = surf.get_width()
            offset = int(cam.offset * fac) % w
            y_pos  = floor_bg - surf.get_height()
            screen.blit(surf, (-offset, y_pos))
            screen.blit(surf, (w - offset, y_pos))

        # 14) Desenha inimigos e tanque alinhados em floor_enemy/floor_tank
        for o in obstacles:
            o.rect.y = floor_enemy - o.rect.height
            o.draw(screen, cam.offset)
        tank.draw(screen, cam.offset)

        pygame.display.flip()
