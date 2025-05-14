import pygame
from bullet import Bullet

class TankAgua:
    def __init__(self, x, y):
        self.image = pygame.Surface((60, 40))
        self.image.fill((100, 100, 200))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel = 3
        self.jatos = []

    def handle_input(self, keys):
        if keys[pygame.K_LEFT]: self.rect.x -= self.vel
        if keys[pygame.K_RIGHT]: self.rect.x += self.vel
        if keys[pygame.K_x]: self.shoot()

    def shoot(self):
        if len(self.jatos) < 3:
            bx = self.rect.right
            by = self.rect.centery
            self.jatos.append(Bullet(bx, by, 6, (0, 150, 255)))

    def update(self):
        for j in list(self.jatos):
            j.update()
            if j.rect.x > 2000:
                self.jatos.remove(j)

    def draw(self, surface, cam_off):
        surface.blit(self.image, self.rect.move(-cam_off, 0))
        for j in self.jatos:
            j.draw(surface, cam_off)