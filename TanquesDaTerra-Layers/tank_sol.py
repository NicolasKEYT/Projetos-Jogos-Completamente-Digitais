import pygame
import os
from bullet import Bullet

class TankSol:
    def __init__(self, x, y):
        base = os.path.dirname(__file__)
        sprite_path = os.path.join(base, 'assets', 'tanque_sol.png')
        original = pygame.image.load(sprite_path).convert_alpha()

        # Renderizações viradas para esquerda e direita
        self.image_left  = original
        self.image_right = pygame.transform.flip(original, True, False)
        self.image = self.image_left

        self.rect    = self.image.get_rect(topleft=(x, y))
        self.vel     = 4
        self.bullets = []
        self.health  = 5
        self.facing  = 'left'

    def handle_input(self, keys):
        # A = virar/esquerda e mover
        if keys[pygame.K_a]:
            self.facing = 'left'
            self.image  = self.image_left
            self.rect.x -= self.vel
        # D = virar/direita e mover
        if keys[pygame.K_d]:
            self.facing = 'right'
            self.image  = self.image_right
            self.rect.x += self.vel

        # X = disparar raio solar na direção atual
        if keys[pygame.K_x] and len(self.bullets) < 3:
            if self.facing == 'left':
                bx = self.rect.left
                dx = -8
            else:
                bx = self.rect.right
                dx = 8
            by = self.rect.centery
            self.bullets.append(Bullet(bx, by, dx, (255,255,0)))

    def update(self):
        for b in list(self.bullets):
            b.update()
            if b.rect.x < 0 or b.rect.x > 2000:
                self.bullets.remove(b)

    def draw(self, surface, cam_off):
        surface.blit(self.image, self.rect.move(-cam_off, 0))
        # Barra de vida
        bw, ratio = self.rect.width, max(0, self.health/5)
        pygame.draw.rect(surface, (255,0,0), (self.rect.x-cam_off, self.rect.y-8, bw, 5))
        pygame.draw.rect(surface, (0,255,0), (self.rect.x-cam_off, self.rect.y-8, bw*ratio, 5))
        # Desenha os tiros
        for b in self.bullets:
            b.draw(surface, cam_off)
