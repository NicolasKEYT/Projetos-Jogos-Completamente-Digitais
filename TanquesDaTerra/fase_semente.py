#Diego Estevão Lopes de Queiroz - 10419038
#Nicolas Gonçalves Santos - 10418047
#Kauã Paixão - 10418548
import pygame
import os
import time
import random
from tank_semente import TankSemente
from obstacles import Obstacle
from camera import Camera


class Enemy:
    def __init__(self, x, y, min_y, max_y, img_fly, img_down, vertical_shift=0):
        # Inicializa o inimigo com imagens, posição e limites de movimento vertical
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
        # Movimento vertical do inimigo
        self.rect.y += int(self.direction * self.speed * dt)
        # Impede que o inimigo suba além do limite superior
        if self.rect.top < self.min_y:
            self.rect.top = self.min_y
            self.direction = 1
        # Impede que o inimigo desça além do limite inferior
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
        # Desenha o inimigo na tela, escolhendo a imagem conforme está no chão ou voando
        img = self.img_down if self.on_ground else self.img_fly
        screen.blit(img, self.rect.move(-cam_offset, 0))


def iniciar_fase_semente(screen, dificuldade='facil'):
    pygame.mixer.music.stop()
    pygame.init()
    clock = pygame.time.Clock()
    sw, sh = screen.get_size()

    # Parâmetros de dificuldade
    if dificuldade == 'facil':
        TIME_LIMIT = 30.0
        ENEMY_SPEED = 100
    elif dificuldade == 'medio':
        TIME_LIMIT = 30.0
        ENEMY_SPEED = 130
    elif dificuldade == 'dificil':
        TIME_LIMIT = 20.0
        ENEMY_SPEED = 200

    # Ajuste da altura dos buracos
    HOLE_VERTICAL_SHIFT = -50  # positivo desce; negativo sobe

    # Carrega camadas de background (parallax)
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

    # Cria e posiciona o Tanque
    tmp = TankSemente(0, 0)
    tank_y = 500
    tank   = TankSemente(100, tank_y)

    # Calcula o Y dos buracos
    hole_base_y = 530 + HOLE_VERTICAL_SHIFT

    # Gera buracos infinitos em distâncias aleatórias
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

    # Carrega imagens do inimigo do caminho correto
    base = os.path.dirname(__file__)
    enemy_dir = os.path.join(base, 'assets', 'enemies', 'semente')
    img_fly = pygame.image.load(os.path.join(enemy_dir, 'fly_enemy.png')).convert_alpha()
    img_down = pygame.image.load(os.path.join(enemy_dir, 'down_enemy.png')).convert_alpha()

    # Cria inimigos que andam de cima para baixo entre os buracos
    ENEMY_VERTICAL_SHIFT = -40  
    enemies = []
    for i in range(len(buracos_x) - 1):
        x1 = buracos_x[i]
        x2 = buracos_x[i + 1]
        enemy_x = (x1 + x2) // 2
        min_y = hole_base_y - 120
        max_y = hole_base_y + 120
        enemy_y = min_y
        enemies.append(Enemy(enemy_x, enemy_y, min_y, max_y, img_fly, img_down, vertical_shift=ENEMY_VERTICAL_SHIFT))

    # Ajusta a velocidade de todos os inimigos conforme a dificuldade
    for enemy in enemies:
        enemy.speed = ENEMY_SPEED

    # Lista de plataformas geradas (árvores plantadas)
    platforms = []

    # Câmera para fase infinita
    cam = Camera(level_width=10**9, level_height=600)

    # Carrega sprite da plataforma (arbusto)
    bush_surf = pygame.image.load(
        os.path.join(base, 'assets','enemies','semente','bush_seed.png')
    ).convert_alpha()

    # Carrega sprite da árvore para plantar
    tree_img = pygame.image.load(
        os.path.join(base, 'assets', 'effects', 'tree.png')
    ).convert_alpha()

    # Alcance de plantio
    PLANT_RANGE = 30  # px de distância do centro do buraco

    # Carrega telas de vitória/derrota
    base = os.path.dirname(__file__)
    ui_dir = os.path.join(base, 'assets', 'ui')
    img_vitoria = pygame.image.load(os.path.join(ui_dir, 'vitoriaSemente.png')).convert_alpha()
    img_derrota = pygame.image.load(os.path.join(ui_dir, 'derrotaSemente.png')).convert_alpha()
    img_vitoria = pygame.transform.scale(img_vitoria, (sw, sh))
    img_derrota = pygame.transform.scale(img_derrota, (sw, sh))

    # Função interna para mostrar tela de fim de fase
    def mostrar_fim(imagem, tipo='vitoria'):
        sw, sh = screen.get_size()
        # Toca o som de vitória ou derrota
        base = os.path.dirname(__file__)
        sons_dir = os.path.join(base, 'assets', 'sons')
        som_vitoria = som_derrota = None
        pygame.mixer.music.stop()
        som_asas.stop()  # <-- ADICIONE ESTA LINHA PARA PARAR O SOM DAS ASAS
        if tipo == "vitoria":
            som_vitoria = pygame.mixer.Sound(os.path.join(sons_dir, 'vitoria.wav'))
            som_vitoria.play()
        elif tipo == "derrota":
            som_derrota = pygame.mixer.Sound(os.path.join(sons_dir, 'derrota.wav'))
            som_derrota.play()

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

    # Carrega o som das asas dos inimigos
    som_asas_path = os.path.join(base, 'assets', 'sons', 'asas.wav')
    som_asas = pygame.mixer.Sound(som_asas_path)
    som_asas.set_volume(0.3)  

    # Carrega o som de plantar semente
    som_plantar_path = os.path.join(base, 'assets', 'sons', 'plantando.wav')
    som_plantar = pygame.mixer.Sound(som_plantar_path)
    som_plantar.set_volume(0.5)  

    # Loop principal da fase
    start_time = time.time()
    while True:
        # Verifica fim por vitória (plantou 10 sementes)
        if len(platforms) >= 10:
            acertou = mostrar_quiz_semente(screen)
            if acertou:
                action = mostrar_fim(img_vitoria, tipo='vitoria')
            else:
                action = mostrar_fim(img_derrota, tipo='derrota')
            if action == 'reiniciar':
                return iniciar_fase_semente(screen, dificuldade)
            else:
                return len(platforms) * 100 if acertou else 0

        # Verifica fim por tempo
        elapsed = time.time() - start_time
        if elapsed >= TIME_LIMIT:
            action = mostrar_fim(img_derrota, tipo='derrota')
            if action == 'reiniciar':
                return iniciar_fase_semente(screen, dificuldade)
            else:
                return len(platforms) * 100  # exemplo de pontuação

        # Controla FPS e obtém dt
        dt = clock.tick(60) / 1000.0

        # Eventos do pygame
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

        # Controle do som das asas dos inimigos
        asas_proximo = any(
            abs(tank.rect.centerx - enemy.rect.centerx) < 120 and abs(tank.rect.centery - enemy.rect.centery) < 80
            for enemy in enemies
        )
        if asas_proximo:
            if not hasattr(tank, 'asas_som_playing') or not tank.asas_som_playing:
                som_asas.play(-1)  # loop enquanto perto
                tank.asas_som_playing = True
        else:
            if hasattr(tank, 'asas_som_playing') and tank.asas_som_playing:
                som_asas.stop()
                tank.asas_som_playing = False

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
                    som_plantar.play()  # Toca o som ao plantar

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
            # Ajuste que reduz hitbox do inimigo em 30% nas bordas 
            shrink = 0.3  # quanto maior, menor a área de colisão
            reduced_rect = enemy.rect.inflate(-enemy.rect.width*shrink, -enemy.rect.height*shrink)
            if tank.rect.colliderect(reduced_rect):
                action = mostrar_fim(img_derrota, tipo='derrota')
                if action == 'reiniciar':
                    return iniciar_fase_semente(screen)
                else:
                    return len(platforms) * 100

        # Desenha parallax de fundo
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
        pixel_font_path = os.path.join(base, 'assets', 'fonts', 'pixel.ttf')
        font = pygame.font.Font(pixel_font_path, 20)
        elapsed = time.time() - start_time
        text_time = f"Tempo: {elapsed:.1f}s"
        text_seed = f"Sementes: {len(platforms)}"
        screen.blit(font.render(text_time, True, (255,255,255)), (10, 10))
        screen.blit(font.render(text_seed, True, (255,255,255)), (10, 40))

        pygame.display.flip()


def mostrar_quiz_semente(screen):
    # Exibe o quiz final da fase da semente e retorna True se acertou, False se errou
    base = os.path.dirname(__file__)
    quiz_img = pygame.image.load(os.path.join(base, 'assets', 'quiz', 'semente_quiz.png')).convert_alpha()
    sw, sh = screen.get_size()
    quiz_img = pygame.transform.scale(quiz_img, (sw, sh))

    # Ajuste as áreas dos botões conforme a imagem do quiz da semente
    btns = [
        pygame.Rect(55, 300, 700, 70),   # Alternativa 1 (correta)
        pygame.Rect(55, 380, 700, 65),   # Alternativa 2 
        pygame.Rect(55, 455, 700, 65),   # Alternativa 3
        pygame.Rect(55, 530, 700, 65),   # Alternativa 4  
    ]
    resposta_correta = 0  # índice da alternativa correta 

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
