import pygame

class Obstacle(pygame.sprite.Sprite):
    """
    Obstáculo genérico para: 'inimigo', 'buraco', 'lixo' ou 'fogo'.
    """
    def __init__(self, x, y, w, h, type):
        super().__init__()
        self.rect = pygame.Rect(x, y, w, h)
        self.type = type
        if self.type == 'inimigo':
            self.dir = 1
            self.speed = 2

    def update(self):
        if self.type == 'inimigo':
            self.rect.x += self.dir * self.speed
            if self.rect.x < 200 or self.rect.x > self.rect.width * 2:
                self.dir *= -1

    def draw(self, surface, cam_off):
        colors = {
            'inimigo': (200, 0, 0),
            'buraco' : (50, 50, 50),
            'lixo'   : (100, 100, 100),
            'fogo'   : (255, 100, 0)
        }
        color = colors.get(self.type, (255,255,255))
        pygame.draw.rect(surface, color, self.rect.move(-cam_off, 0))