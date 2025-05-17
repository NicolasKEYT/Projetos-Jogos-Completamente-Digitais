import pygame, os
from bullet import Bullet

class TankSol:
    # ESCALA do sprite: 1.0 = 100%, 1.5 = 150%, 2.0 = 200%
    SCALE = 1.5
    # Cooldown de tiro em milissegundos
    SHOOT_COOLDOWN = 1000
    MAX_HEALTH     = 100
    DAMAGE         = 50

    def __init__(self, x, y):
        base        = os.path.dirname(__file__)
        sprite_path = os.path.join(base, 'assets', 'tanque_sol.png')
        original    = pygame.image.load(sprite_path).convert_alpha()

        # escala
        w, h     = original.get_size()
        new_size = (int(w * self.SCALE), int(h * self.SCALE))
        scaled   = pygame.transform.scale(original, new_size)

        # orientações
        self.image_left  = scaled
        self.image_right = pygame.transform.flip(scaled, True, False)
        self.image       = self.image_left

        self.rect           = self.image.get_rect(topleft=(x, y))
        self.vel            = 4
        self.bullets        = []
        self.health         = self.MAX_HEALTH
        self.last_shot_time = 0
        self.facing         = 'left'

    def handle_input(self, keys):
        # movimento e flip
        if keys[pygame.K_a]:
            self.facing = 'left'
            self.image  = self.image_left
            self.rect.x -= self.vel
        if keys[pygame.K_d]:
            self.facing = 'right'
            self.image  = self.image_right
            self.rect.x += self.vel

        # tiro com cooldown
        if keys[pygame.K_x]:
            now = pygame.time.get_ticks()
            if now - self.last_shot_time >= self.SHOOT_COOLDOWN and len(self.bullets) < 3:
                bx, dx = (self.rect.left, -8) if self.facing=='left' else (self.rect.right, 8)
                by = self.rect.centery
                self.bullets.append(Bullet(bx, by, dx, (255,255,0)))
                self.last_shot_time = now

    def update(self):
        for b in self.bullets[:]:
            b.update()
            if b.rect.x < 0 or b.rect.x > 2000:
                self.bullets.remove(b)

    def draw(self, surf, cam_off):
        surf.blit(self.image, self.rect.move(-cam_off, 0))
        # barra de vida
        bw, ratio = self.rect.width, max(0, self.health/self.MAX_HEALTH)
        pygame.draw.rect(surf, (255,0,0),
                         (self.rect.x-cam_off, self.rect.y-8, bw, 5))
        pygame.draw.rect(surf, (0,255,0),
                         (self.rect.x-cam_off, self.rect.y-8, bw*ratio, 5))
        # projéteis
        for b in self.bullets:
            b.draw(surf, cam_off)
