import pygame
from bullet import Bullet

class TankSemente:
    def __init__(self, x, y):
        self.image = pygame.Surface((60, 40))
        self.image.fill((100, 200, 100))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel = 3
        self.plantas = []

    def handle_input(self, keys):
        if keys[pygame.K_LEFT]: self.rect.x -= self.vel
        if keys[pygame.K_RIGHT]: self.rect.x += self.vel
        if keys[pygame.K_x]: self.plantar()

    def plantar(self):
        x = self.rect.centerx
        y = self.rect.bottom
        self.plantas.append(pygame.Rect(x-20, y, 40, 10))

    def update(self): pass

    def draw(self, surface, cam_off):
        surface.blit(self.image, self.rect.move(-cam_off, 0))
        for p in self.plantas:
            pygame.draw.rect(surface, (0, 150, 0), p.move(-cam_off, 0))