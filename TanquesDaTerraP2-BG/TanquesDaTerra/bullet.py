import pygame

class Bullet:
    def __init__(self, x, y, dx, color=(255,255,0)):
        self.rect = pygame.Rect(x, y, 8, 4)
        self.dx = dx
        self.color = color

    def update(self):
        self.rect.x += self.dx

    def draw(self, surface, cam_off):
        pygame.draw.rect(surface, self.color, self.rect.move(-cam_off, 0))