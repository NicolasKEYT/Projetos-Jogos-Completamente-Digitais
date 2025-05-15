import pygame

class Obstacle:
    def __init__(self, x, y, w, h, kind):
        self.rect = pygame.Rect(x, y, w, h)
        self.kind = kind
        if kind == 'inimigo':
            self.health = 3
            self.dir = 1
            self.speed = 2

    def update(self):
        if self.kind == 'inimigo':
            self.rect.x += self.dir * self.speed
            if self.rect.x < 200 or self.rect.x > 1400:
                self.dir *= -1

    def take_damage(self, dmg=1):
        if self.kind == 'inimigo':
            self.health -= dmg

    def draw(self, surf, cam_off):
        cols = {
            'inimigo': (200,0,0),
            'buraco':  (50,50,50),
            'lixo':    (100,100,100),
            'fogo':    (255,100,0)
        }
        pygame.draw.rect(surf, cols[self.kind], self.rect.move(-cam_off,0))
        if self.kind == 'inimigo':
            bw = self.rect.width
            ratio = max(0, self.health/3)
            # back bar
            pygame.draw.rect(surf,(50,50,50),(self.rect.x-cam_off,self.rect.y-7,bw,4))
            # life bar
            pygame.draw.rect(surf,(0,255,0),(self.rect.x-cam_off,self.rect.y-7,bw*ratio,4))
