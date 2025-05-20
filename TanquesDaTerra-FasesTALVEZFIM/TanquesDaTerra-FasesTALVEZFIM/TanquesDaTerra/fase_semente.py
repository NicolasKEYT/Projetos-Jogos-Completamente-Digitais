import pygame
import os
import time
import random
from tank_semente import TankSemente
from obstacles import Obstacle
from camera import Camera


class Enemy:
    def __init__(self, x, y, min_y, max_y, img_fly, img_down, vertical_shift=0):
        # Usa o tamanho real da imagem para o rect
        self.img_fly = pygame.transform.scale(img_fly, img_fly.get_size())
        self.img_down = pygame.transform.scale(img_down, img_down.get_size())
        width, height = self.img_fly.get_size()
        self.rect = pygame.Rect(x, y + vertical_shift, width, height)
        self.speed = 120  # pixels por segundo
        self.direction = 1  # 1: baixo, -1: cima
        self.min_y = min_y + vertical_shift
        self.max_y = max_y + vertical_shift
        self.on_ground = False
        # Parâmetros para movimento aleatório
        self.change_time = random.uniform(0.5, 2.0)
        self.time_accum = 0

    def update(self, dt):
        # Movimento vertical
        self.rect.y += int(self.direction * self.speed * dt)
        # Garante que não suba demais
        if self.rect.top < self.min_y:
            self.rect.top = self.min_y
            self.direction = 1
        # Garante que não desça demais
        elif self.rect.bottom > self.max_y:
            self.rect.bottom = self.max_y
            self.direction = -1
        self.on_ground = (self.rect.bottom >= self.max_y)
        # Movimento aleatório: troca direção em intervalos aleatórios
        self.time_accum += dt
        if self.time_accum >= self.change_time:
            # Só troca para cima se não está no topo
            if self.rect.top <= self.min_y:
                self.direction = 1
            # Só troca para baixo se não está no fundo
            elif self.rect.bottom >= self.max_y:
                self.direction = -1
            else:
                self.direction = random.choice([-1, 1])
            self.change_time = random.uniform(0.5, 2.0)
            self.time_accum = 0

    def draw(self, screen, cam_offset):
        img = self.img_down if self.on_ground else self.img_fly
        screen.blit(img, self.rect.move(-cam_offset, 0))


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

    # — Gera buracos infinitos em distâncias aleatórias —
    min_x = 350
    max_x = 10000  # Limite "alto" para simular infinito
    min_dist = 300
    max_dist = 500

    buracos_x = []
    x = min_x
    while x < max_x:
        buracos_x.append(x)
        x += random.randint(min_dist, max_dist)

    obstacles = [
        Obstacle(x, hole_base_y, 80, 120, 'buraco')
        for x in buracos_x
    ]

    # — Carrega imagens do inimigo do caminho correto
    base = os.path.dirname(__file__)
    enemy_dir = os.path.join(base, 'assets', 'enemies', 'semente')
    img_fly = pygame.image.load(os.path.join(enemy_dir, 'fly_enemy.png')).convert_alpha()
    img_down = pygame.image.load(os.path.join(enemy_dir, 'down_enemy.png')).convert_alpha()

    # — Cria inimigos que andam de cima para baixo entre os buracos —
    ENEMY_VERTICAL_SHIFT = -40  # ajuste aqui para subir/descer todos os inimigos
    enemies = []
    for i in range(len(buracos_x) - 1):
        x1 = buracos_x[i]
        x2 = buracos_x[i + 1]
        enemy_x = (x1 + x2) // 2
        min_y = hole_base_y - 120
        max_y = hole_base_y + 120
        enemy_y = min_y
        enemies.append(Enemy(enemy_x, enemy_y, min_y, max_y, img_fly, img_down, vertical_shift=ENEMY_VERTICAL_SHIFT))

    # — Lista de plataformas geradas —
    platforms = []

    # — Câmera para fase infinita —
    cam = Camera(level_width=10**9, level_height=600)

    # — Carrega sprite da plataforma (arbusto) —
    bush_surf = pygame.image.load(
        os.path.join(base, 'assets','enemies','semente','bush_seed.png')
    ).convert_alpha()

    # Carrega sprite da árvore para plantar
    tree_img = pygame.image.load(
        os.path.join(base, 'assets', 'effects', 'tree.png')
    ).convert_alpha()

    # — Alcance de plantio —
    PLANT_RANGE = 30  # px de distância do centro do buraco

    # — Carrega telas de vitória/derrota
    base = os.path.dirname(__file__)
    ui_dir = os.path.join(base, 'assets', 'ui')
    img_vitoria = pygame.image.load(os.path.join(ui_dir, 'vitoriaSemente.png')).convert_alpha()
    img_derrota = pygame.image.load(os.path.join(ui_dir, 'derrotaSemente.png')).convert_alpha()
    img_vitoria = pygame.transform.scale(img_vitoria, (sw, sh))
    img_derrota = pygame.transform.scale(img_derrota, (sw, sh))

    # — Função interna para mostrar tela de fim de fase
    def mostrar_fim(imagem, tipo='vitoria'):
        screen.blit(imagem, imagem.get_rect(center=(sw//2, sh//2)))
        pygame.display.flip()
        lw, lh, sp = 320, 80, 40  # largura, altura, espaço
        yb = sh//2 + 160
        btn_r = pygame.Rect(sw//2 - lw - sp//2, yb, lw, lh)
        btn_m = pygame.Rect(sw//2 + sp//2,     yb, lw, lh)
        act = None
        while act is None:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); exit()
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    mx, my = e.pos
                    if btn_r.collidepoint(mx, my): act = 'reiniciar'
                    elif btn_m.collidepoint(mx, my): act = 'menu'
            pygame.time.wait(10)
        return act

    # — Loop principal —
    start_time = time.time()
    TIME_LIMIT = 30.0  # segundos para acabar a fase

    while True:
        # Verifica fim por vitória (plantou 10 sementes)
        if len(platforms) >= 10:
            action = mostrar_fim(img_vitoria, tipo='vitoria')
            if action == 'reiniciar':
                return iniciar_fase_semente(screen)
            else:
                return len(platforms) * 100  # exemplo de pontuação

        # Verifica fim por tempo
        elapsed = time.time() - start_time
        if elapsed >= TIME_LIMIT:
            action = mostrar_fim(img_derrota, tipo='derrota')
            if action == 'reiniciar':
                return iniciar_fase_semente(screen)
            else:
                return len(platforms) * 100  # exemplo de pontuação

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

        # Atualiza inimigos (movimento vertical)
        for enemy in enemies:
            enemy.update(dt)

        # Plantio contínuo (X pressionado)
        if keys[pygame.K_x]:
            for obs in list(obstacles):
                if obs.kind == 'buraco' and tank.rect.colliderect(obs.rect):
                    # Cria plataforma com imagem de árvore ao plantar
                    largura = int(obs.rect.width * 1.5)
                    altura  = int(obs.rect.height * 1.2)
                    px = obs.rect.centerx - largura // 2
                    py = obs.rect.centery - altura // 2
                    # Salva posição e tamanho para desenhar a árvore
                    platforms.append((px, py, largura, altura))
                    obstacles.remove(obs)

        # Colisão com buraco sem plataforma: impede passagem
        for obs in obstacles:
            if obs.kind == 'buraco' and tank.rect.colliderect(obs.rect):
                if tank.rect.centerx < obs.rect.centerx:
                    tank.rect.right = obs.rect.left
                else:
                    tank.rect.left = obs.rect.right
                break

        # Colisão com inimigo: derrota instantânea
        for enemy in enemies:
            # Ajuste fino: reduz hitbox do inimigo em 30% nas bordas (colisão só ocorre bem próximo)
            shrink = 0.3  # quanto maior, menor a área de colisão
            reduced_rect = enemy.rect.inflate(-enemy.rect.width*shrink, -enemy.rect.height*shrink)
            if tank.rect.colliderect(reduced_rect):
                action = mostrar_fim(img_derrota, tipo='derrota')
                if action == 'reiniciar':
                    return iniciar_fase_semente(screen)
                else:
                    return len(platforms) * 100

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

        # Desenha plataformas criadas (árvore)
        for plat in platforms:
            px, py, largura, altura = plat
            tree_scaled = pygame.transform.scale(tree_img, (largura, altura))
            screen.blit(tree_scaled, (px - cam.offset, py - 10))  # Suba 10 pixels

        # Desenha inimigos
        for enemy in enemies:
            enemy.draw(screen, cam.offset)

        # Desenha tanque por último (camada superior)
        tank.draw(screen, cam.offset)

        # Placar: tempo e sementes plantadas
        font = pygame.font.SysFont("arialblack", 20, bold=True)
        elapsed = time.time() - start_time
        text_time = f"Tempo: {elapsed:.1f}s"
        text_seed = f"Sementes: {len(platforms)}"
        screen.blit(font.render(text_time, True, (255,255,255)), (10, 10))
        screen.blit(font.render(text_seed, True, (255,255,255)), (10, 40))

        pygame.display.flip()
