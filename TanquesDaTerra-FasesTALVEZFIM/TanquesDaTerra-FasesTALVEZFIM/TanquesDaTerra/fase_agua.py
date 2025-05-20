import pygame
import os
import time
import random
from tank_agua import TankAgua
from obstacles import Obstacle
from camera import Camera
from PIL import Image

# Constantes de fase
TIME_LIMIT      = 20.0       # segundos
EXTINGUISH_HOLD = 1.0        # segundos para extinguir
VICTORY_TARGET  = 15         # picos para vitória
POINTS_PER_5    = 100        # pontos a cada 5 picos

# Deslocamentos verticais
BG_VERTICAL_SHIFT    = 260
TANK_VERTICAL_SHIFT  = -15
SPIKE_VERTICAL_SHIFT = -45

# Spawn de spikes
INITIAL_SPIKES  = 5
MAX_SPIKES      = 10
SPIKE_SPAWN_GAP = (200, 400)


def load_gif_frames(path):
    frames = []
    pil_img = Image.open(path)
    try:
        while True:
            frame = pil_img.convert('RGBA')
            surf  = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
            frames.append(surf)
            pil_img.seek(pil_img.tell() + 1)
    except EOFError:
        pass
    return frames


def iniciar_fase_agua(screen):
    pygame.init()
    clock = pygame.time.Clock()
    sw, sh = screen.get_size()

    # Carrega backgrounds
    base   = os.path.dirname(__file__)
    bg_dir = os.path.join(base, 'assets', 'agua_bg')
    files  = [f for f in os.listdir(bg_dir) if f.endswith('.png') and not f.lower().endswith('christmas tree.png')]
    files  = sorted(files, key=lambda x: int(os.path.splitext(x)[0]) if x.split('.')[0].isdigit() else float('inf'))
    factors = [0.2 + 0.8 * i/(len(files)-1) for i in range(len(files))]
    layers  = [(pygame.image.load(os.path.join(bg_dir, f)).convert_alpha(), fac) for f, fac in zip(files, factors)]
    back_layers  = layers[:-3]
    front_layers = layers[-3:]
    floor_y = sh - front_layers[0][0].get_height() + BG_VERTICAL_SHIFT

    # Carrega sprite de árvore opcional
    tree_path = os.path.join(bg_dir, 'christmas tree.png')
    if os.path.exists(tree_path):
        tree_img = pygame.image.load(tree_path).convert_alpha()
        tree_rect = tree_img.get_rect(midbottom=(sw//2, floor_y))
    else:
        tree_img, tree_rect = None, None

    # Carrega UI final
    ui_dir  = os.path.join(base, 'assets', 'ui')
    img_vit = pygame.image.load(os.path.join(ui_dir, 'vitoriaAgua.png')).convert_alpha()
    img_der = pygame.image.load(os.path.join(ui_dir, 'derrotaAgua.png')).convert_alpha()
    img_vit = pygame.transform.scale(img_vit, (sw, sh))
    img_der = pygame.transform.scale(img_der, (sw, sh))

    # Inicializa spikes
    fire_spikes = []
    x = 400
    for _ in range(INITIAL_SPIKES):
        s = Obstacle(x, floor_y - 40 + SPIKE_VERTICAL_SHIFT, 40, 40, 'fogo')
        fire_spikes.append(s)
        x += random.randint(*SPIKE_SPAWN_GAP)
    timers = {s: 0.0 for s in fire_spikes}
    extinguished = 0

    # Instancia tanque
    tmp  = TankAgua(0, 0)
    tank = TankAgua(100, floor_y - tmp.image.get_height() + TANK_VERTICAL_SHIFT)
    cam  = Camera(level_width=10**9, level_height=sh)

    # Animações de fogo e água
    fire_frames  = load_gif_frames(os.path.join(base, 'assets', 'effects', 'fogo.gif'))
    water_frames = load_gif_frames(os.path.join(base, 'assets', 'effects', 'agua.gif'))
    f_idx, f_tm = 0, 0.0
    w_idx, w_tm = 0, 0.0

    # Marca início da fase
    start_time = time.time()

    def mostrar_fim(imagem, tipo='vitoria'):
        screen.blit(imagem, imagem.get_rect(center=(sw//2, sh//2)))
        pygame.display.flip()
        lw, lh, sp = 320, 80, 40  # aumente largura e altura
        yb = sh//2 + 160  # desça um pouco mais
        btn_r = pygame.Rect(sw//2 - lw - sp//2, yb, lw, lh)
        btn_m = pygame.Rect(sw//2 + sp//2,       yb, lw, lh)
        act = None
        while act is None:
            for e in pygame.event.get():
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    mx, my = e.pos
                    if btn_r.collidepoint(mx, my): act = 'reiniciar'
                    elif btn_m.collidepoint(mx, my): act = 'menu'
            pygame.time.wait(10)
        return act

    # Loop principal
    while True:
        dt      = clock.tick(60) / 1000.0
        elapsed = time.time() - start_time

        # Verifica fim por tempo
        if elapsed >= TIME_LIMIT:
            score = (extinguished // 5) * POINTS_PER_5
            if extinguished >= VICTORY_TARGET:
                action = mostrar_fim(img_vit)
            else:
                action = mostrar_fim(img_der, tipo='derrota')
            if action == 'reiniciar':
                return iniciar_fase_agua(screen)
            else:
                return score

        # Eventos gerais
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return 0

        # Atualiza tanque
        keys = pygame.key.get_pressed()
        tank.handle_input(keys)
        tank.update()
        cam.update(tank.rect)

        # Lógica de extinção
        if keys[pygame.K_x]:
            W, H = 60, 40
            if tank.facing == 'left':
                cannon = pygame.Rect(tank.rect.left - W, tank.rect.y, W, H)
            else:
                cannon = pygame.Rect(tank.rect.right, tank.rect.y, W, H)
            for s in list(fire_spikes):
                if cannon.colliderect(s.rect):
                    timers[s] += dt
                    if timers[s] >= EXTINGUISH_HOLD:
                        fire_spikes.remove(s)
                        extinguished += 1
                        timers.pop(s, None)
                else:
                    timers[s] = 0.0

        # Respawn spikes
        for s in list(fire_spikes):
            if s.rect.x < cam.offset - 100:
                fire_spikes.remove(s)
                timers.pop(s, None)
        if len(fire_spikes) < MAX_SPIKES:
            nx = int(cam.offset + sw + random.randint(*SPIKE_SPAWN_GAP))
            new_s = Obstacle(nx, floor_y - 40 + SPIKE_VERTICAL_SHIFT, 40, 40, 'fogo')
            fire_spikes.append(new_s)
            timers[new_s] = 0.0

        # Atualiza animações
        f_tm += dt
        if fire_frames and f_tm > 0.08:
            f_idx = (f_idx + 1) % len(fire_frames)
            f_tm = 0.0
        w_tm += dt
        if water_frames and w_tm > 0.08:
            w_idx = (w_idx + 1) % len(water_frames)
            w_tm = 0.0

        # Desenha back layers
        sky = back_layers[0][0].get_at((0,0))
        screen.fill(sky)
        for surf, fac in back_layers:
            w = surf.get_width()
            off = int(cam.offset * fac) % w
            y = floor_y - surf.get_height()
            screen.blit(surf, (-off, y))
            screen.blit(surf, (w-off, y))

        # Desenha árvore opcional
        if tree_img:
            screen.blit(tree_img, (tree_rect.x - cam.offset, tree_rect.y))

        # Desenha spikes animados
        for s in fire_spikes:
            if fire_frames:
                img = fire_frames[f_idx]
                new_w = int(s.rect.width * 2)
                new_h = int(s.rect.height * 2.5)
                anim = pygame.transform.scale(img, (new_w, new_h))
                dx = s.rect.x - cam.offset - (new_w - s.rect.width)//2
                dy = s.rect.y - (new_h - s.rect.height)//2
                screen.blit(anim, (dx, dy))
            else:
                s.draw(screen, cam.offset)

        # Desenha tanque
        screen.blit(tank.image, tank.rect.move(-cam.offset, 0))

        # Desenha jato de água (fallback ou animado)
        if keys[pygame.K_x]:
            if water_frames:
                img = pygame.transform.scale(water_frames[w_idx],
                    (int(60*1.4), int(40*1.4)))
                cr = pygame.Rect(
                    tank.rect.left-60 if tank.facing=='left' else tank.rect.right,
                    tank.rect.y, 60, 40)
                dr = cr.move(-cam.offset,0)
                dr.x -= (img.get_width()-cr.width)//2
                dr.y -= (img.get_height()-cr.height)//2
                screen.blit(img, dr)

        # Desenha front layers
        for surf, fac in front_layers:
            w = surf.get_width()
            off = int(cam.offset * fac) % w
            y = floor_y - surf.get_height()
            screen.blit(surf, (-off, y))
            screen.blit(surf, (w-off, y))

        # HUD: tempo, apagados e pontos
        score = (extinguished // 5) * POINTS_PER_5
        font = pygame.font.SysFont('arialblack', 20, bold=True)
        # Sombra
        t_s = font.render(f"Tempo: {max(0, TIME_LIMIT-elapsed):.1f}", True, (0,0,0))
        a_s = font.render(f"Apagados: {extinguished}", True, (0,0,0))
        p_s = font.render(f"Pontos: {score}", True, (0,0,0))
        screen.blit(t_s, (13,13)); screen.blit(a_s, (13,53)); screen.blit(p_s, (13,93))
        # Texto principal
        t_m = font.render(f"Tempo: {max(0, TIME_LIMIT-elapsed):.1f}", True, (0,200,255))
        a_m = font.render(f"Apagados: {extinguished}", True, (255,220,0))
        p_m = font.render(f"Pontos: {score}", True, (255,220,0))
        screen.blit(t_m, (10,10)); screen.blit(a_m, (10,50)); screen.blit(p_m, (10,90))

        pygame.display.flip()
