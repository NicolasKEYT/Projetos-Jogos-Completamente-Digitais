import pygame
from bullet import Bullet

class TankSol:
    def __init__(self, x, y):
        self.image = pygame.Surface((60, 40))
        self.image.fill((200, 200, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel = 3
        self.tiros = []

    def handle_input(self, keys):
        if keys[pygame.K_LEFT]: self.rect.x -= self.vel
        if keys[pygame.K_RIGHT]: self.rect.x += self.vel
        if keys[pygame.K_x]: self.shoot()

    def shoot(self):
        if len(self.tiros) < 3:
            bx = self.rect.right
            by = self.rect.centery
            self.tiros.append(Bullet(bx, by, 6, (255, 255, 0)))

    def update(self):
        for b in list(self.tiros):
            b.update()
            if b.rect.x > 2000:
                self.tiros.remove(b)

    def draw(self, surface, cam_off):
        surface.blit(self.image, self.rect.move(-cam_off, 0))
        for b in self.tiros:
            b.draw(surface, cam_off)