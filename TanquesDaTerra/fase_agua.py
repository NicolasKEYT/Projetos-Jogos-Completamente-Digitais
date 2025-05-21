#Diego Estevão Lopes de Queiroz - 10419038
#Nicolas Gonçalves Santos - 10418047
#Kauã Paixão - 10418548

import pygame
import os
import time
import random
from tank_agua import TankAgua
from obstacles import Obstacle
from camera import Camera
from PIL import Image

# Constantes de fase
VICTORY_TARGET  = 15         # Quantidade de picos de fogo para vitória
POINTS_PER_5    = 100        # Pontos a cada 5 picos apagados

# Deslocamentos verticais para ajuste de sprites no cenário
BG_VERTICAL_SHIFT    = 260
TANK_VERTICAL_SHIFT  = -15
SPIKE_VERTICAL_SHIFT = -45

# Parâmetros de spawn dos picos de fogo
INITIAL_SPIKES  = 5
MAX_SPIKES      = 10
SPIKE_SPAWN_GAP = (200, 400)  # Distância mínima e máxima entre spikes

def load_gif_frames(path):
    # Carrega todos os frames de um GIF animado e converte para superfícies do pygame
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

def iniciar_fase_agua(screen, dificuldade='facil'):
    pygame.mixer.music.stop()
    pygame.init()
    clock = pygame.time.Clock()
    sw, sh = screen.get_size()

    # Carrega sons de fogo e água
    base = os.path.dirname(__file__)
    som_fogo_path = os.path.join(base, 'assets', 'sons', 'fogo_som.wav')
    som_fogo = pygame.mixer.Sound(som_fogo_path)
    som_fogo.set_volume(0.05)  # Volume do som de fogo

    som_agua_path = os.path.join(base, 'assets', 'sons', 'agua_spray.wav')
    som_agua = pygame.mixer.Sound(som_agua_path)
    som_agua.set_volume(0.3)  # Volume do som de água

    # Define parâmetros de dificuldade
    if dificuldade == 'facil':
        TIME_LIMIT = 30.0
        EXTINGUISH_HOLD = 1.0
    elif dificuldade == 'medio':
        TIME_LIMIT = 20.0
        EXTINGUISH_HOLD = 1.0
    elif dificuldade == 'dificil':
        TIME_LIMIT = 20.0
        EXTINGUISH_HOLD = 1.5

    # Carrega camadas de fundo (parallax)
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

    # Carrega telas de vitória e derrota
    ui_dir  = os.path.join(base, 'assets', 'ui')
    img_vit = pygame.image.load(os.path.join(ui_dir, 'vitoriaAgua.png')).convert_alpha()
    img_der = pygame.image.load(os.path.join(ui_dir, 'derrotaAgua.png')).convert_alpha()
    img_vit = pygame.transform.scale(img_vit, (sw, sh))
    img_der = pygame.transform.scale(img_der, (sw, sh))

    # Inicializa picos de fogo (spikes)
    fire_spikes = []
    x = 400
    for _ in range(INITIAL_SPIKES):
        s = Obstacle(x, floor_y - 40 + SPIKE_VERTICAL_SHIFT, 40, 40, 'fogo')
        fire_spikes.append(s)
        x += random.randint(*SPIKE_SPAWN_GAP)
    timers = {s: 0.0 for s in fire_spikes}  # Timer para cada spike
    extinguished = 0  # Contador de picos apagados

    # Instancia o tanque de água
    tmp  = TankAgua(0, 0)
    tank = TankAgua(100, floor_y - tmp.image.get_height() + TANK_VERTICAL_SHIFT)
    cam  = Camera(level_width=10**9, level_height=sh)

    # Carrega animações de fogo e água
    fire_frames  = load_gif_frames(os.path.join(base, 'assets', 'effects', 'fogo.gif'))
    water_frames = load_gif_frames(os.path.join(base, 'assets', 'effects', 'agua.gif'))
    f_idx, f_tm = 0, 0.0
    w_idx, w_tm = 0, 0.0

    # Marca o início da fase
    start_time = time.time()

    def mostrar_fim(imagem, tipo='vitoria'):
        # Exibe tela de vitória ou derrota e trata botões de reinício/menu
        sw, sh = screen.get_size()
        base = os.path.dirname(__file__)
        sons_dir = os.path.join(base, 'assets', 'sons')
        som_vitoria = som_derrota = None
        pygame.mixer.music.stop()
        if tipo == "vitoria":
            som_vitoria = pygame.mixer.Sound(os.path.join(sons_dir, 'vitoria.wav'))
            som_vitoria.play()
        elif tipo == "derrota":
            som_derrota = pygame.mixer.Sound(os.path.join(sons_dir, 'derrota.wav'))
            som_derrota.play()

        screen.blit(imagem, imagem.get_rect(center=(sw//2, sh//2)))
        pygame.display.flip()
        lw, lh, sp = 320, 80, 40
        yb = sh//2 + 160
        btn_r = pygame.Rect(sw//2 - lw - sp//2, yb, lw, lh)
        btn_m = pygame.Rect(sw//2 + sp//2,       yb, lw, lh)
        act = None
        while act is None:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    if som_vitoria: som_vitoria.stop()
                    if som_derrota: som_derrota.stop()
                    pygame.quit(); exit()
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    mx, my = e.pos
                    if btn_r.collidepoint(mx, my): act = 'reiniciar'
                    elif btn_m.collidepoint(mx, my): act = 'menu'
            pygame.time.wait(10)
        # Para o som ao sair da tela
        if som_vitoria: som_vitoria.stop()
        if som_derrota: som_derrota.stop()
        return act

    # Loop principal da fase
    while True:
        dt      = clock.tick(60) / 1000.0
        elapsed = time.time() - start_time

        # Verifica se o tempo acabou
        if elapsed >= TIME_LIMIT:
            score = (extinguished // 5) * POINTS_PER_5
            som_fogo.stop()
            som_agua.stop()
            if extinguished >= VICTORY_TARGET:
                acertou = mostrar_quiz_agua(screen)
                if acertou:
                    action = mostrar_fim(img_vit)
                else:
                    action = mostrar_fim(img_der, tipo='derrota')
            else:
                action = mostrar_fim(img_der, tipo='derrota')
            if action == 'reiniciar':
                return iniciar_fase_agua(screen, dificuldade)
            else:
                return score if extinguished >= VICTORY_TARGET and acertou else 0

        # Eventos do pygame (fechar janela, ESC)
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

        # Toca o som se o tanque estiver próximo de algum pico de fogo
        fogo_proximo = any(
            abs(tank.rect.centerx - s.rect.centerx) < 120 and abs(tank.rect.centery - s.rect.centery) < 80
            for s in fire_spikes
        )
        if fogo_proximo:
            if not hasattr(tank, 'fogo_som_playing') or not tank.fogo_som_playing:
                som_fogo.play(-1)  # Loop enquanto perto
                tank.fogo_som_playing = True
        else:
            if hasattr(tank, 'fogo_som_playing') and tank.fogo_som_playing:
                som_fogo.stop()
                tank.fogo_som_playing = False

        # Lógica de extinção dos picos de fogo
        if keys[pygame.K_x]:
            # Toca o som do spray de água enquanto X estiver pressionado
            if not hasattr(tank, 'agua_som_playing') or not tank.agua_som_playing:
                som_agua.play(-1)
                tank.agua_som_playing = True

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
        else:
            if hasattr(tank, 'agua_som_playing') and tank.agua_som_playing:
                som_agua.stop()
                tank.agua_som_playing = False

        # Remove spikes que saíram da tela
        for s in list(fire_spikes):
            if s.rect.x < cam.offset - 100:
                fire_spikes.remove(s)
                timers.pop(s, None)
        # Respawn de spikes até o máximo permitido
        if len(fire_spikes) < MAX_SPIKES:
            nx = int(cam.offset + sw + random.randint(*SPIKE_SPAWN_GAP))
            new_s = Obstacle(nx, floor_y - 40 + SPIKE_VERTICAL_SHIFT, 40, 40, 'fogo')
            fire_spikes.append(new_s)
            timers[new_s] = 0.0

        # Atualiza animações de fogo e água
        f_tm += dt
        if fire_frames and f_tm > 0.08:
            f_idx = (f_idx + 1) % len(fire_frames)
            f_tm = 0.0
        w_tm += dt
        if water_frames and w_tm > 0.08:
            w_idx = (w_idx + 1) % len(water_frames)
            w_tm = 0.0

        # Desenha camadas de fundo (parallax)
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

        # Desenha jato de água 
        if keys[pygame.K_x]:
            if water_frames:
                img = pygame.transform.scale(water_frames[w_idx], (int(60*1.4), int(40*1.4)))
                img = pygame.transform.flip(img, True, False)  # Sempre inverte o PNG do jato
                if tank.facing == 'left':
                    img = pygame.transform.flip(img, True, False)  # Inverte de novo se virado para a esquerda
                cr = pygame.Rect(
                    tank.rect.left-60 if tank.facing=='left' else tank.rect.right,
                    tank.rect.y, 60, 40)
                dr = cr.move(-cam.offset,0)
                dr.x -= (img.get_width()-cr.width)//2
                dr.y -= (img.get_height()-cr.height)//2
                screen.blit(img, dr)

        # Desenha camadas frontais
        for surf, fac in front_layers:
            w = surf.get_width()
            off = int(cam.offset * fac) % w
            y = floor_y - surf.get_height()
            screen.blit(surf, (-off, y))
            screen.blit(surf, (w-off, y))

        # HUD: tempo, apagados e pontos
        score = (extinguished // 5) * POINTS_PER_5
        pixel_font_path = os.path.join(base, 'assets', 'fonts', 'pixel.ttf')
        font = pygame.font.Font(pixel_font_path, 20)
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

def mostrar_quiz_agua(screen):
    # Exibe o quiz final da fase da água e retorna True se acertou, False se errou
    base = os.path.dirname(__file__)
    quiz_img = pygame.image.load(os.path.join(base, 'assets', 'quiz', 'agua_quiz.png')).convert_alpha()
    sw, sh = screen.get_size()
    quiz_img = pygame.transform.scale(quiz_img, (sw, sh))

    # Define as áreas dos botões conforme a imagem do quiz
    btns = [
        pygame.Rect(55, 340, 700, 65),   # Alternativa 1
        pygame.Rect(55, 415, 700, 65),   # Alternativa 2 (correta)
        pygame.Rect(55, 490, 700, 65),   # Alternativa 3
        pygame.Rect(55, 565, 700, 35),   # Alternativa 4
    ]
    resposta_correta = 1  # índice da alternativa correta

    clock = pygame.time.Clock()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                for idx, btn in enumerate(btns):
                    if btn.collidepoint(e.pos):
                        return idx == resposta_correta  # True se acertou, False se errou

        screen.blit(quiz_img, (0, 0))
        pygame.display.flip()
        clock.tick(60)
