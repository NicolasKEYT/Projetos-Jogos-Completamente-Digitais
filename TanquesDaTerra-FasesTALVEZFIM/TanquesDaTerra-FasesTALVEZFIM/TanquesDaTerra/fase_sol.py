import pygame
import os
import random
from tank_sol import TankSol
from obstacles import Obstacle
from camera import Camera

# Diretório base e de UI
BASE_DIR = os.path.dirname(__file__)
UI_DIR   = os.path.join(BASE_DIR, 'assets', 'ui')


def iniciar_fase_sol(screen):
    pygame.init()
    clock = pygame.time.Clock()
    sw, sh = screen.get_size()

    # — Carrega telas de vitória/derrota —
    img_vitoria = pygame.image.load(os.path.join(UI_DIR, 'vitoriaSol.png')).convert_alpha()
    img_derrota = pygame.image.load(os.path.join(UI_DIR, 'derrotaSol.png')).convert_alpha()
    img_vitoria = pygame.transform.scale(img_vitoria, (sw, sh))
    img_derrota = pygame.transform.scale(img_derrota, (sw, sh))

    # — Parâmetros de layout e jogo —
    BG_VERTICAL_SHIFT    = 260
    TANK_VERTICAL_SHIFT  = 250
    ENEMY_VERTICAL_SHIFT = 250
    SPAWN_MARGIN         = 20
    ENEMY_SPEED          = 1
    ENEMY_SCALE          = 1.5
    FLAME_RANGE          = 100
    FLAME_DAMAGE         = 20
    FLAME_INTERVAL       = 0.5
    KILL_TARGET          = 20
    POINTS_PER_5         = 100  # pontos a cada 5 inimigos mortos
    WAVE_KILL            = 1

    kill_count = 0
    death_since_spawn = 0

    # — HUD e efeitos —
    hud_dir      = os.path.join(BASE_DIR, 'assets', 'hud')
    hud_tank_100 = pygame.image.load(os.path.join(hud_dir, 'vida100.png')).convert_alpha()
    hud_tank_60  = pygame.image.load(os.path.join(hud_dir, 'vida60.png')).convert_alpha()
    hud_tank_20  = pygame.image.load(os.path.join(hud_dir, 'vida20.png')).convert_alpha()
    hud_enemy    = pygame.image.load(os.path.join(hud_dir, 'vidaenemy.png')).convert_alpha()
    bullet_base  = pygame.image.load(os.path.join(hud_dir, 'balatanque.png')).convert_alpha()
    bullet_left  = pygame.transform.flip(bullet_base, True, False)
    bullet_right = bullet_base
    flame_base   = pygame.image.load(os.path.join(hud_dir, 'chamas.png')).convert_alpha()
    fw, fh       = flame_base.get_size()
    flame_img    = pygame.transform.scale(flame_base, (int(fw*2.5), int(fh*2.5)))
    flame_left   = pygame.transform.flip(flame_img, True, False)
    flame_right  = flame_img

    # — Câmera e fundo —
    cam = Camera(level_width=1600, level_height=sh)
    sol_bg_dir = os.path.join(BASE_DIR, 'assets', 'sol_bg')
    layer_files = [
        'Hills Layer 01.png','Hills Layer 02.png','Hills Layer 03.png',
        'Hills Layer 04.png','Hills Layer 05.png','Hills Layer 06.png'
    ]
    parallax_factors = [0.2, 0.35, 0.5, 0.7, 0.9, 1.1]
    bg_layers = [
        (pygame.image.load(os.path.join(sol_bg_dir, f)).convert_alpha(), fac)
        for f, fac in zip(layer_files, parallax_factors)
    ]
    ground_surf = bg_layers[4][0]
    floor_base  = sh - ground_surf.get_height()
    floor_bg    = floor_base + BG_VERTICAL_SHIFT
    floor_tank  = floor_base + TANK_VERTICAL_SHIFT
    floor_enemy = floor_base + ENEMY_VERTICAL_SHIFT

    # — Carrega sprites de tanque —
    tmp     = TankSol(0, 0)
    tank_y  = floor_tank - tmp.image.get_height()
    tank    = TankSol(100, tank_y)

    # — Função interna para spawn de inimigos —
    def spawn_enemies(n=2):
        enemies = []
        for _ in range(n):
            side = random.choice(['left', 'right'])
            if side == 'left':
                ex, dir_mult = -SPAWN_MARGIN - random.randint(0, SPAWN_MARGIN), 1
            else:
                ex, dir_mult = 1600 + SPAWN_MARGIN + random.randint(0, SPAWN_MARGIN), -1
            o = Obstacle(ex, floor_enemy, 40, 60, 'inimigo', sprite_name='inimigo_sol1')
            if hasattr(o, 'image') and o.image:
                iw, ih = o.image.get_size()
                scaled = pygame.transform.scale(o.image, (int(iw*ENEMY_SCALE), int(ih*ENEMY_SCALE)))
                o.image_left  = scaled
                o.image_right = pygame.transform.flip(scaled, True, False)
            o.dir = dir_mult
            o.speed = ENEMY_SPEED
            o.touch_timer = 0.0
            img = o.image_left if o.dir < 0 else o.image_right
            o.rect = img.get_rect(topleft=(ex, floor_enemy - img.get_height()))
            enemies.append(o)
        return enemies

    obstacles = spawn_enemies()

    # — Tela de fim —
    def mostrar_tela_fim(screen, imagem, tipo="vitoria"):
        sw, sh = screen.get_size()
        screen.blit(imagem, imagem.get_rect(center=(sw//2, sh//2)))
        pygame.display.flip()
        largura, altura, esp = 320, 80, 40  # aumente largura e altura
        yb = sh//2 + 160  # desça um pouco mais
        btn_r = pygame.Rect(sw//2 - largura - esp//2, yb, largura, altura)
        btn_m = pygame.Rect(sw//2 + esp//2,         yb, largura, altura)
        acao = None
        while acao is None:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); exit()
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    mx, my = e.pos
                    if btn_r.collidepoint(mx, my): acao = 'reiniciar'
                    elif btn_m.collidepoint(mx, my): acao = 'menu'
            pygame.time.wait(10)
        return acao

    # — Loop principal —
    while True:
        # Derrota por morte
        if tank.health <= 0:
            acao = mostrar_tela_fim(screen, img_derrota, tipo="derrota")
            if acao == "reiniciar":
                return iniciar_fase_sol(screen)
            else:
                return 0

        # Vitória por kill count
        if kill_count >= KILL_TARGET:
            acao = mostrar_tela_fim(screen, img_vitoria, tipo="vitoria")
            if acao == "reiniciar":
                return iniciar_fase_sol(screen)
            else:
                # retorna pontos acumulados
                return (kill_count // 5) * POINTS_PER_5

        dt = clock.tick(60) / 1000.0
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return 0

        # Atualiza tanque
        keys = pygame.key.get_pressed()
        tank.handle_input(keys)
        tank.update()

        # Atualiza inimigos e chama
        for o in obstacles:
            dir_mult = 1 if o.rect.centerx < tank.rect.centerx else -1
            o.rect.x += dir_mult * o.speed
            if abs(o.rect.centerx - tank.rect.centerx) <= FLAME_RANGE:
                o.touch_timer += dt
                if o.touch_timer >= FLAME_INTERVAL:
                    tank.health -= FLAME_DAMAGE
                    o.touch_timer -= FLAME_INTERVAL
            else:
                o.touch_timer = 0.0

        # Colisões projétil → inimigo
        for b in list(tank.bullets):
            b.update()
            for o in list(obstacles):
                if b.rect.colliderect(o.rect):
                    o.take_damage(TankSol.DAMAGE)
                    tank.bullets.remove(b)
                    if o.health <= 0:
                        obstacles.remove(o)
                        kill_count += 1
                        death_since_spawn += 1
                    break

        # Respawn em ondas
        if death_since_spawn >= WAVE_KILL:
            obstacles.extend(spawn_enemies())
            death_since_spawn = 0

        cam.update(tank.rect)

        # Desenha background
        sky = bg_layers[0][0].get_at((0,0))
        screen.fill(sky)
        for surf, fac in bg_layers:
            w   = surf.get_width()
            off = int(cam.offset * fac) % w
            screen.blit(surf, (-off, floor_bg - surf.get_height()))
            screen.blit(surf, (w - off, floor_bg - surf.get_height()))

        # HUD: faltam e pontuação
        remaining = max(0, KILL_TARGET - kill_count)
        score     = (kill_count // 5) * POINTS_PER_5
        font      = pygame.font.SysFont("arialblack", 30, bold=True)
        text_f    = f"Faltam: {remaining}"
        text_s    = f"Pontos: {score}"
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            outline_f = font.render(text_f, True, (0,0,0)); screen.blit(outline_f, (10+dx,10+dy))
            outline_s = font.render(text_s, True, (0,0,0)); screen.blit(outline_s, (10+dx,50+dy))
        screen.blit(font.render(text_f, True, (255,255,255)), (10,10))
        screen.blit(font.render(text_s, True, (255,255,255)), (10,50))

        # Desenha inimigos, projéteis, chama e HUD de inimigo
        for o in obstacles:
            img = o.image_left if o.dir < 0 else o.image_right
            screen.blit(img, o.rect.move(-cam.offset, 0))
            if abs(o.rect.centerx - tank.rect.centerx) <= FLAME_RANGE:
                flame = flame_left if o.dir < 0 else flame_right
                fx    = o.rect.left - flame.get_width() if o.dir < 0 else o.rect.right
                fy    = o.rect.y + o.rect.height // 4
                screen.blit(flame, (fx - cam.offset, fy))
            hud_x = o.rect.centerx - hud_enemy.get_width() // 2 - cam.offset
            hud_y = o.rect.y - hud_enemy.get_height() - 5
            screen.blit(hud_enemy, (hud_x, hud_y))

        for b in tank.bullets:
            bi = bullet_right if b.dx > 0 else bullet_left
            screen.blit(bi, (b.rect.x - cam.offset, b.rect.y))

        # Desenha tanque e barra de vida
        screen.blit(tank.image, tank.rect.move(-cam.offset, 0))
        th = hud_tank_100 if tank.health > 60 else hud_tank_60 if tank.health > 20 else hud_tank_20
        if th:
            tx = tank.rect.centerx - th.get_width() // 2 - cam.offset
            ty = tank.rect.y - th.get_height() - 5
            screen.blit(th, (tx, ty))

        pygame.display.flip()
