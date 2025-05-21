#Diego Estevão Lopes de Queiroz - 10419038
#Nicolas Gonçalves Santos - 10418047
#Kauã Paixão - 10418548
import pygame
import os
import random
from tank_sol import TankSol
from obstacles import Obstacle
from camera import Camera

# Diretório base e de UI
BASE_DIR = os.path.dirname(__file__)
UI_DIR   = os.path.join(BASE_DIR, 'assets', 'ui')

def iniciar_fase_sol(screen, dificuldade='facil'):
    pygame.mixer.music.stop()
    pygame.init()
    clock = pygame.time.Clock()
    sw, sh = screen.get_size()

    # — Parâmetros de layout e jogo —
    BG_VERTICAL_SHIFT    = 260
    TANK_VERTICAL_SHIFT  = 250
    ENEMY_VERTICAL_SHIFT = 250
    SPAWN_MARGIN         = 1  
    ENEMY_SCALE          = 1.5
    FLAME_RANGE          = 100
    FLAME_DAMAGE         = 20
    FLAME_INTERVAL       = 0.5
    POINTS_PER_5         = 100  # pontos a cada 5 inimigos mortos

    # Parâmetros de dificuldade
    if dificuldade == 'facil':
        ENEMY_SPEED   = 1.0
        KILL_TARGET   = 10
        WAVE_KILL     = 1
        ENEMIES_PER_WAVE = 15
    elif dificuldade == 'medio':
        ENEMY_SPEED   = 1.5
        KILL_TARGET   = 20
        WAVE_KILL     = 2
        ENEMIES_PER_WAVE = 10
    elif dificuldade == 'dificil':
        ENEMY_SPEED   = 2.0
        KILL_TARGET   = 20
        WAVE_KILL     = 3
        ENEMIES_PER_WAVE = 10

    kills = 0
    wave = 1

    # — Carrega telas de vitória/derrota 
    img_vitoria = pygame.image.load(os.path.join(UI_DIR, 'vitoriaSol.png')).convert_alpha()
    img_derrota = pygame.image.load(os.path.join(UI_DIR, 'derrotaSol.png')).convert_alpha()
    img_vitoria = pygame.transform.scale(img_vitoria, (sw, sh))
    img_derrota = pygame.transform.scale(img_derrota, (sw, sh))

    kill_count = 0
    death_since_spawn = 0
    
    # — HUD e efeitos 
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

    # Carregue o som do lança-chamas
    som_chamas_path = os.path.join(BASE_DIR, 'assets', 'sons', 'chamas.wav')
    som_chamas = pygame.mixer.Sound(som_chamas_path)
    som_chamas.set_volume(0.10)  

    # — Câmera e fundo 
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

    # — Carrega sprites de tanque 
    tmp     = TankSol(0, 0)
    tank_y  = floor_tank - tmp.image.get_height()
    tank    = TankSol(100, tank_y)

    # — Função interna para spawn de inimigos 
    def spawn_enemies(n=4):
        # Gera uma lista de inimigos em posições variadas, evitando sobreposição
        enemies = []
        used_positions = set()
        min_dist = 80  # Distância mínima entre inimigos 
        for _ in range(n):
            side = random.choice(['left', 'right'])
            # Gera uma posição única para cada inimigo
            while True:
                extra_dist = random.randint(0, 700)  
                if side == 'left':
                    ex = -SPAWN_MARGIN - extra_dist
                else:
                    ex = 1600 + SPAWN_MARGIN + extra_dist
                # Garante que não nasça muito perto de outro inimigo
                if all(abs(ex - pos) > min_dist for pos in used_positions):
                    used_positions.add(ex)
                    break
            dir_mult = 1 if side == 'left' else -1
            o = Obstacle(ex, floor_enemy, 40, 60, 'inimigo', sprite_name='inimigo_sol1')

            if hasattr(o, 'image') and o.image:
                iw, ih = o.image.get_size()
                scaled = pygame.transform.scale(o.image, (int(iw*ENEMY_SCALE), int(ih*ENEMY_SCALE)))
                o.image_left  = scaled
                o.image_right = pygame.transform.flip(scaled, True, False)
            o.dir = dir_mult
            o.speed = ENEMY_SPEED  
            o.touch_timer = 0.0
            img = o.image_right if o.dir > 0 else o.image_left
            o.rect = img.get_rect(topleft=(ex, floor_enemy - img.get_height()))
            enemies.append(o)
        return enemies

    # Spawn inicial de inimigos
    obstacles = spawn_enemies(4)

    # — Tela de fim —
    def mostrar_tela_fim(screen, imagem, tipo="vitoria"):
        # Exibe tela de vitória ou derrota e trata botões de reinício/menu
        sw, sh = screen.get_size()
        base = os.path.dirname(__file__)
        sons_dir = os.path.join(base, 'assets', 'sons')
        som_vitoria = som_derrota = None
        if tipo == "vitoria":
            som_vitoria = pygame.mixer.Sound(os.path.join(sons_dir, 'vitoria.wav'))
            som_vitoria.play()
        elif tipo == "derrota":
            som_derrota = pygame.mixer.Sound(os.path.join(sons_dir, 'derrota.wav'))
            som_derrota.play()

        screen.blit(imagem, imagem.get_rect(center=(sw//2, sh//2)))
        pygame.display.flip()
        largura, altura, esp = 320, 80, 40
        yb = sh//2 + 160
        btn_r = pygame.Rect(sw//2 - largura - esp//2, yb, largura, altura)
        btn_m = pygame.Rect(sw//2 + esp//2,         yb, largura, altura)
        acao = None
        while acao is None:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    if som_vitoria: som_vitoria.stop()
                    if som_derrota: som_derrota.stop()
                    pygame.quit(); exit()
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    mx, my = e.pos
                    if btn_r.collidepoint(mx, my): acao = 'reiniciar'
                    elif btn_m.collidepoint(mx, my): acao = 'menu'
            pygame.time.wait(10)
        # Pare o som ao sair da tela
        if som_vitoria: som_vitoria.stop()
        if som_derrota: som_derrota.stop()
        return acao

    wave_message_pending = False
    # — Loop principal 
    while True:
        # Derrota por morte
        if tank.health <= 0:
            pygame.mixer.Channel(5).stop()  # <-- ADICIONE ESTA LINHA
            acao = mostrar_tela_fim(screen, img_derrota, tipo="derrota")
            if acao == "reiniciar":
                return iniciar_fase_sol(screen, dificuldade)  
            else:
                return 0

        # Vitória por kill count
        if kill_count >= KILL_TARGET:
            pygame.mixer.Channel(5).stop()  # <-- ADICIONE ESTA LINHA
            # Mostra quiz antes da tela final
            acertou = mostrar_quiz_sol(screen)
            if acertou:
                acao = mostrar_tela_fim(screen, img_vitoria, tipo="vitoria")
            else:
                acao = mostrar_tela_fim(screen, img_derrota, tipo="derrota")
            if acao == "reiniciar":
                return iniciar_fase_sol(screen, dificuldade)
            else:
                # retorna pontos acumulados apenas se acertou o quiz
                return (kill_count // 5) * POINTS_PER_5 if acertou else 0

        dt = clock.tick(60) / 1000.0
        chama_ativa = False  # Flag para saber se algum lança-chamas está ativo nesta iteração

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
            # Atualiza direção do inimigo para olhar para o tanque
            if o.rect.centerx < tank.rect.centerx:
                o.dir = 1
                img = o.image_right  # imagem do inimigo olhando para a direita
                flame = flame_right  # lança-chamas para a direita
                fx = o.rect.right    # posição x do lança-chamas
            else:
                o.dir = -1
                img = o.image_left   # imagem do inimigo olhando para a esquerda
                flame = flame_left   # lança-chamas para a esquerda
                fx = o.rect.left - flame.get_width()  # posição x do lança-chamas

            # Movimento do inimigo
            o.rect.x += o.dir * o.speed

            # Desenhar inimigo
            screen.blit(img, o.rect.move(-cam.offset, 0))

            # Desenhar lança-chamas se estiver perto do tanque
            if abs(o.rect.centerx - tank.rect.centerx) <= FLAME_RANGE:
                fy = o.rect.y + o.rect.height // 4
                screen.blit(flame, (fx - cam.offset, fy))
                chama_ativa = True  # Algum lança-chamas está ativo

                # Dano do lança-chamas
                o.touch_timer += dt
                if o.touch_timer >= FLAME_INTERVAL:
                    tank.health -= FLAME_DAMAGE
                    o.touch_timer -= FLAME_INTERVAL
            else:
                o.touch_timer = 0.0

            # HUD de vida do inimigo
            hud_x = o.rect.centerx - hud_enemy.get_width() // 2 - cam.offset
            hud_y = o.rect.y - hud_enemy.get_height() - 5
            screen.blit(hud_enemy, (hud_x, hud_y))

        # Controle do som do lança-chamas
        if chama_ativa:
            if not pygame.mixer.Channel(5).get_busy():
                pygame.mixer.Channel(5).play(som_chamas, loops=-1)
        else:
            pygame.mixer.Channel(5).stop()

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
        if dificuldade in ('medio', 'dificil'):
            if death_since_spawn >= 2:
                obstacles.extend(spawn_enemies(3))
                death_since_spawn = 0
        else:
            if death_since_spawn >= WAVE_KILL:
                obstacles.extend(spawn_enemies())
                death_since_spawn = 0

        cam.update(tank.rect)

        # Desenha background (parallax)
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
        pixel_font_path = os.path.join(BASE_DIR, 'assets', 'fonts', 'pixel.ttf')
        font = pygame.font.Font(pixel_font_path, 30)
        text_f = f"Faltam: {remaining}"
        text_s = f"Pontos: {score}"
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

def mostrar_quiz_sol(screen):
    # Exibe o quiz final da fase do sol e retorna True se acertou, False se errou
    base = os.path.dirname(__file__)
    quiz_img = pygame.image.load(os.path.join(base, 'assets', 'quiz', 'sol_quiz.png')).convert_alpha()
    sw, sh = screen.get_size()
    quiz_img = pygame.transform.scale(quiz_img, (sw, sh))

    # Ajuste as áreas dos botões conforme a imagem
    btns = [
        pygame.Rect(60, 390, 680, 35),   # Alternativa 1
        pygame.Rect(60, 430, 680, 60),   # Alternativa 2 (correta)
        pygame.Rect(60, 500, 680, 35),   # Alternativa 3 
        pygame.Rect(60, 540, 680, 35),   # Alternativa 4
    ]
    resposta_correta = 1  # índice da alternativa correta (0, 1, 2, 3)

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
