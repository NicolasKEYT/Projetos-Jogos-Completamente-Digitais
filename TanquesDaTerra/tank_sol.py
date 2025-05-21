#Diego Estevão Lopes de Queiroz - 10419038
#Nicolas Gonçalves Santos - 10418047
#Kauã Paixão - 10418548
import pygame, os
from bullet import Bullet

class TankSol:
    # ESCALA do sprite
    SCALE = 1.5
    # Cooldown de tiro em milissegundos
    SHOOT_COOLDOWN = 1000
    MAX_HEALTH     = 100
    DAMAGE         = 50

    BULLET_VERTICAL_SHIFT = -10  # ajuste para subir/descer o tiro
    BULLET_SCALE = 2           # ajuste para aumentar/diminuir o tamanho da bala

    def __init__(self, x, y):
        base        = os.path.dirname(__file__)
        sprite_path = os.path.join(base, 'assets', 'tanque_sol.png')
        original    = pygame.image.load(sprite_path).convert_alpha()

        # Carrega o som do tiro
        som_tiro_path = os.path.join(base, 'assets', 'sons', 'tiro_sol.wav')
        self.som_tiro = pygame.mixer.Sound(som_tiro_path)
        self.som_tiro.set_volume(0.2)  # volume de 0.0 (mudo) até 1.0 (máximo)

        # Escala o sprite do tanque
        w, h     = original.get_size()
        new_size = (int(w * self.SCALE), int(h * self.SCALE))
        scaled   = pygame.transform.scale(original, new_size)

        # Gera as duas orientações (esquerda/direita)
        self.image_left  = scaled
        self.image_right = pygame.transform.flip(scaled, True, False)
        self.image       = self.image_left

        # Inicializa o retângulo de colisão e atributos do tanque
        self.rect           = self.image.get_rect(topleft=(x, y))
        self.vel            = 4
        self.bullets        = []
        self.health         = self.MAX_HEALTH
        self.last_shot_time = 0
        self.facing         = 'left'

    def handle_input(self, keys):
        # Movimento para a esquerda
        if keys[pygame.K_a]:
            self.facing = 'left'
            self.image  = self.image_left
            self.rect.x -= self.vel
        # Movimento para a direita
        if keys[pygame.K_d]:
            self.facing = 'right'
            self.image  = self.image_right
            self.rect.x += self.vel

        # Tiro com cooldown (X) e limite de 3 projéteis
        if keys[pygame.K_x]:
            now = pygame.time.get_ticks()
            if now - self.last_shot_time >= self.SHOOT_COOLDOWN and len(self.bullets) < 3:
                bx, dx = (self.rect.left, -8) if self.facing=='left' else (self.rect.right, 8)
                by = self.rect.centery + self.BULLET_VERTICAL_SHIFT
                bullet_height = int(4 * self.BULLET_SCALE)
                bullet_width = int(10 * self.BULLET_SCALE)
                self.bullets.append(Bullet(bx, by, dx, (255,255,0), bullet_width, bullet_height))
                self.last_shot_time = now
                self.som_tiro.play()  # toca o som do tiro

    def update(self):
        # Atualiza cada projétil e remove os que saem da tela
        for b in self.bullets[:]:
            b.update()
            if b.rect.x < 0 or b.rect.x > 2000:
                self.bullets.remove(b)

    def draw(self, surf, cam_off):
        # Desenha o tanque ajustando pela câmera
        surf.blit(self.image, self.rect.move(-cam_off, 0))
        # Barra de vida acima do tanque
        bw, ratio = self.rect.width, max(0, self.health/self.MAX_HEALTH)
        pygame.draw.rect(surf, (255,0,0),
                         (self.rect.x-cam_off, self.rect.y-8, bw, 5))
        pygame.draw.rect(surf, (0,255,0),
                         (self.rect.x-cam_off, self.rect.y-8, bw*ratio, 5))
        # Desenha os projéteis
        for b in self.bullets:
            b.draw(surf, cam_off)
