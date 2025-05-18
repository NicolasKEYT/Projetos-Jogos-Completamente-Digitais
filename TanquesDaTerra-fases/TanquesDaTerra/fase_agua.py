import pygame
import os
import time
import random
from tank_agua import TankAgua
from obstacles import Obstacle
from camera import Camera
from PIL import Image  # Adicione este import no topo

# Constants
TIME_LIMIT = 20.0         # seconds
EXTINGUISH_HOLD = 1.0     # seconds to hold water on a fire
FIRE_KIND = 'fogo'        # obstacle kind for fire spikes

# Vertical shifts (pixels)
BG_VERTICAL_SHIFT = 260     # shift entire background vertically
TANK_VERTICAL_SHIFT = -15   # shift tank vertical position
SPIKE_VERTICAL_SHIFT = -45  # shift fire spikes vertical position

# Spike spawn settings
INITIAL_SPIKES = 5        # initial number of spikes
MAX_SPIKES = 10           # max spikes at a time
SPIKE_SPAWN_GAP = (200, 400)  # horizontal gap range when spawning

def load_gif_frames(path):
    """Carrega todos os frames de um GIF animado como surfaces do pygame."""
    pil_img = Image.open(path)
    frames = []
    try:
        while True:
            frame = pil_img.convert('RGBA')
            mode = frame.mode
            size = frame.size
            data = frame.tobytes()
            py_image = pygame.image.fromstring(data, size, mode)
            frames.append(py_image)
            pil_img.seek(pil_img.tell() + 1)
    except EOFError:
        pass
    return frames

def iniciar_fase_agua(screen):
    pygame.init()
    clock = pygame.time.Clock()
    sw, sh = screen.get_size()

    # — Load background layers in numeric order —
    base = os.path.dirname(__file__)
    bg_dir = os.path.join(base, 'assets', 'agua_bg')
    files = [f for f in os.listdir(bg_dir)
             if f.lower().endswith('.png') and f.lower() != 'christmas tree.png']
    layer_files = sorted(
        files,
        key=lambda x: int(os.path.splitext(x)[0])
                   if os.path.splitext(x)[0].isdigit() else float('inf')
    )
    num_layers = len(layer_files)
    parallax_factors = [0.2 + 0.8 * i / (num_layers - 1) for i in range(num_layers)]
    bg_layers = []
    for fname, fac in zip(layer_files, parallax_factors):
        surf = pygame.image.load(os.path.join(bg_dir, fname)).convert_alpha()
        bg_layers.append((surf, fac))

    # — Split back and front layers —
    back_layers = bg_layers[:-3]
    front_layers = bg_layers[-3:]

    # — Calculate floor Y —
    floor_y = sh - front_layers[0][0].get_height() + BG_VERTICAL_SHIFT

    # — Load Christmas tree sprite —
    tree_path = os.path.join(bg_dir, 'christmas tree.png')
    if os.path.exists(tree_path):
        tree_img = pygame.image.load(tree_path).convert_alpha()
        tree_rect = tree_img.get_rect()
        tree_rect.bottom = floor_y
        tree_rect.x = sw // 2  # adjust horizontal as needed
    else:
        tree_img, tree_rect = None, None

    # — Initialize fire spikes —
    fire_spikes = []
    x_pos = 400
    for _ in range(INITIAL_SPIKES):
        spike = Obstacle(x_pos, floor_y - 40 + SPIKE_VERTICAL_SHIFT,
                         40, 40, FIRE_KIND)
        fire_spikes.append(spike)
        x_pos += random.randint(*SPIKE_SPAWN_GAP)

    # — Instantiate water tank —
    tmp = TankAgua(0, 0)
    tank_y = floor_y - tmp.image.get_height() + TANK_VERTICAL_SHIFT
    tank = TankAgua(100, tank_y)

    cam = Camera(level_width=10**9, level_height=sh)
    extinguish_timers = {spike: 0.0 for spike in fire_spikes}
    extinguished_count = 0
    start_time = time.time()

    # Carregue todos os frames do fogo animado
    fire_img_path = os.path.join(base, 'assets', 'efects', 'fogo.gif')
    fire_frames = load_gif_frames(fire_img_path) if os.path.exists(fire_img_path) else []
    fire_frame_count = len(fire_frames)
    fire_anim_index = 0
    fire_anim_timer = 0

    # Carregue todos os frames do jato de água animado
    water_img_path = os.path.join(base, 'assets', 'efects', 'agua.gif')
    water_frames = load_gif_frames(water_img_path) if os.path.exists(water_img_path) else []
    water_frame_count = len(water_frames)
    water_anim_index = 0
    water_anim_timer = 0

    # — Main loop —
    while True:
        dt = clock.tick(60) / 1000.0
        elapsed = time.time() - start_time
        if elapsed >= TIME_LIMIT:
            break

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return

        # — Update tank & camera —
        keys = pygame.key.get_pressed()
        tank.handle_input(keys)
        tank.bullets.clear()
        tank.update()
        cam.update(tank.rect)

        # — Extinguish logic using water cannon —
        if keys[pygame.K_x]:
            # define cannon area rectangle
            CANNON_W, CANNON_H = 60, 40
            if tank.facing == 'left':
                cannon_rect = pygame.Rect(
                    tank.rect.left - CANNON_W,
                    tank.rect.y,
                    CANNON_W, CANNON_H
                )
            else:
                cannon_rect = pygame.Rect(
                    tank.rect.right,
                    tank.rect.y,
                    CANNON_W, CANNON_H
                )
            # apply extinguish hold on spikes
            for spike in list(fire_spikes):
                if cannon_rect.colliderect(spike.rect):
                    extinguish_timers[spike] += dt
                    if extinguish_timers[spike] >= EXTINGUISH_HOLD:
                        fire_spikes.remove(spike)
                        extinguished_count += 1
                        extinguish_timers.pop(spike, None)
                        start_time += 0.7  # Adiciona 1.5s ao timer
                        print("Tempo aumentado! Novo start_time:", start_time)
                else:
                    extinguish_timers[spike] = 0.0

        # — Spawn new spikes infinitely —
        for spike in list(fire_spikes):
            if spike.rect.x < cam.offset - 100:
                fire_spikes.remove(spike)
                extinguish_timers.pop(spike, None)
        if len(fire_spikes) < MAX_SPIKES:
            new_x = int(cam.offset + sw + random.randint(*SPIKE_SPAWN_GAP))
            spike = Obstacle(new_x, floor_y - 40 + SPIKE_VERTICAL_SHIFT,
                             40, 40, FIRE_KIND)
            fire_spikes.append(spike)
            extinguish_timers[spike] = 0.0

        fire_anim_timer += dt
        if fire_frames and fire_anim_timer > 0.08:
            fire_anim_index = (fire_anim_index + 1) % fire_frame_count
            fire_anim_timer = 0

        # Atualize o frame do jato de água
        water_anim_timer += dt
        if water_frames and water_anim_timer > 0.08:
            water_anim_index = (water_anim_index + 1) % water_frame_count
            water_anim_timer = 0

        # — Draw back layers —
        sky = back_layers[0][0].get_at((0, 0))
        screen.fill(sky)
        for surf, fac in back_layers:
            w = surf.get_width()
            off = int(cam.offset * fac) % w
            y_pos = floor_y - surf.get_height()
            screen.blit(surf, (-off, y_pos))
            screen.blit(surf, (w - off, y_pos))

        # — Draw Christmas tree —
        if tree_img and tree_rect:
            screen.blit(tree_img, (tree_rect.x - cam.offset, tree_rect.y))

        # — Draw spikes and tank behind front layers —
        for spike in fire_spikes:
            if fire_frames:
                # Aumenta o fogo: 30% mais alto e 10% mais largo
                new_w = int(spike.rect.width * 2)
                new_h = int(spike.rect.height * 2.5)
                img = pygame.transform.scale(fire_frames[fire_anim_index], (new_w, new_h))
                # Centraliza o fogo aumentado no spike
                draw_x = spike.rect.x - cam.offset - (new_w - spike.rect.width) // 2
                draw_y = spike.rect.y - (new_h - spike.rect.height) // 2
                screen.blit(img, (draw_x, draw_y))
            else:
                spike.draw(screen, cam.offset)
        screen.blit(tank.image, tank.rect.move(-cam.offset, 0))

        # — Draw water cannon visual —
        if keys[pygame.K_x]:
            if water_frames:
                # Aumenta o tamanho do jato de água em 40%
                scale_w = int(cannon_rect.width * 1.4)
                scale_h = int(cannon_rect.height * 1.4)
                water_img = water_frames[water_anim_index]
                water_img = pygame.transform.scale(water_img, (scale_w, scale_h))
                # Centraliza o jato aumentado no canhão
                draw_rect = cannon_rect.move(-cam.offset, 0)
                draw_rect.x -= (scale_w - cannon_rect.width) // 2
                draw_rect.y -= (scale_h - cannon_rect.height) // 2
                screen.blit(water_img, draw_rect)
            else:
                # Spray effect: apenas gotas circulares (fallback)
                spray_color = (80, 180, 255, 120)  # azul claro semi-transparente
                surf = pygame.Surface((int(cannon_rect.width*1.4), int(cannon_rect.height*1.4)), pygame.SRCALPHA)
                for i in range(12):
                    gx = random.randint(0, surf.get_width())
                    gy = random.randint(surf.get_height()//2, int(surf.get_height() * 1.3))
                    gy = min(gy, surf.get_height() - 1)
                    pygame.draw.circle(surf, spray_color, (gx, gy), random.randint(5, 10))
                draw_rect = cannon_rect.move(-cam.offset, 0)
                draw_rect.x -= (surf.get_width() - cannon_rect.width) // 2
                draw_rect.y -= (surf.get_height() - cannon_rect.height) // 2
                screen.blit(surf, draw_rect)

        # — Draw front layers —
        for surf, fac in front_layers:
            w = surf.get_width()
            off = int(cam.offset * fac) % w
            y_pos = floor_y - surf.get_height()
            screen.blit(surf, (-off, y_pos))
            screen.blit(surf, (w - off, y_pos))

        # — Draw HUD: timer/score —
        font = pygame.font.SysFont("arialblack", 20, bold=True)
        shadow_font = pygame.font.SysFont("arialblack", 20, bold=True)
        # Sombra
        ttxt = font.render(f"Tempo: {max(0, TIME_LIMIT-elapsed):.1f}", True, (0,0,0))
        ctxt = font.render(f"Apagados: {extinguished_count}", True, (0,0,0))
        screen.blit(ttxt, (13,13))
        screen.blit(ctxt, (13,53))
        # Texto principal
        ttxt = font.render(f"Tempo: {max(0, TIME_LIMIT-elapsed):.1f}", True, (0,200,255))
        ctxt = font.render(f"Apagados: {extinguished_count}", True, (255,220,0))
        screen.blit(ttxt, (10,10))
        screen.blit(ctxt, (10,50))

        pygame.display.flip()

    return extinguished_count
