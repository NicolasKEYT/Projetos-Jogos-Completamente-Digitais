import pygame
import os

class TankSemente:
    def __init__(self, x, y):
        base = os.path.dirname(__file__)
        sprite_path = os.path.join(base, 'assets', 'tanque_semente.png')
        original = pygame.image.load(sprite_path).convert_alpha()

        # two orientations
        self.image_left  = original
        self.image_right = pygame.transform.flip(original, True, False)
        self.image = self.image_left

        self.rect       = self.image.get_rect(topleft=(x, y))
        self.vel        = 4
        self.plants     = []
        self.health     = 5
        self.facing     = 'left'
        self.max_plants = 5

    def handle_input(self, keys):
        if keys[pygame.K_a]:
            self.facing = 'left'
            self.image  = self.image_left
            self.rect.x -= self.vel
        if keys[pygame.K_d]:
            self.facing = 'right'
            self.image  = self.image_right
            self.rect.x += self.vel

        if keys[pygame.K_x] and len(self.plants) < self.max_plants:
            if self.facing == 'left':
                px = self.rect.left - 40
            else:
                px = self.rect.right
            py = self.rect.bottom
            self.plants.append(pygame.Rect(px, py, 40, 10))

    def update(self):
        pass

    def draw(self, surf, cam_off):
        surf.blit(self.image, self.rect.move(-cam_off, 0))
        bw, ratio = self.rect.width, max(0, self.health/5)
        pygame.draw.rect(surf, (255,0,0),
                         (self.rect.x-cam_off, self.rect.y-8, bw, 5))
        pygame.draw.rect(surf, (0,255,0),
                         (self.rect.x-cam_off, self.rect.y-8, bw*ratio, 5))
        for p in self.plants:
            pygame.draw.rect(surf, (0,150,0), p.move(-cam_off, 0))
