#Diego Estevão Lopes de Queiroz - 10419038
#Nicolas Gonçalves Santos - 10418047
#Kauã Paixão - 10418548
import pygame
class Bullet:
    def __init__(self, x, y, dx, color=(255,255,0), width=10, height=4):
        self.rect = pygame.Rect(x, int(y - height // 2), width, height)
        self.dx = dx  # Velocidade horizontal da bala 
        self.color = color  # Cor da bala 

    def update(self):
        # Move a bala horizontalmente de acordo com dx
        self.rect.x += self.dx

    def draw(self, surface, cam_off):
        pygame.draw.rect(surface, self.color, self.rect.move(-cam_off, 0))
