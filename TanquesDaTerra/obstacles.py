# obstacles.py

import pygame
import os

class Obstacle:
    """
    Obstáculo genérico para: 'inimigo', 'buraco', 'lixo' ou 'fogo'.
    - Se kind=='buraco', carrega rombo.png em vez de desenhar um retângulo.
    """
    def __init__(self, x, y, w, h, kind, sprite_name=None):
        self.kind = kind
        base = os.path.dirname(__file__)

        if kind == 'inimigo':
            self.rect   = pygame.Rect(x, y, w, h)
            self.dir    = 1
            self.speed  = 2
            self.health = 3
            # Carrega a imagem do inimigo se sprite_name for fornecido
            if sprite_name:
                img_path = os.path.join(base, 'assets', 'enemies', 'sol', f'{sprite_name}.png')
                self.image = pygame.image.load(img_path).convert_alpha()
                # Ajusta o tamanho do rect para o tamanho da imagem
                self.rect.size = self.image.get_size()
            else:
                self.image = None

        elif kind == 'buraco':
            # carrega o PNG do rombo
            img_path = os.path.join(
                base, 'assets', 'enemies', 'semente', 'rombo.png'
            )
            self.image = pygame.image.load(img_path).convert_alpha()
            # Ajuste: rect menor que a imagem, centralizado
            img_rect = self.image.get_rect(topleft=(x, y))
            # Por exemplo, 60% da largura e altura, centralizado
            w, h = int(img_rect.width * 0.6), int(img_rect.height * 0.6)
            offset_x = (img_rect.width - w) // 2
            offset_y = (img_rect.height - h) // 2
            self.rect = pygame.Rect(x + offset_x, y + offset_y, w, h)
            self.img_rect = img_rect  # para desenhar a imagem no lugar certo

        else:
            # lixo, fogo etc.
            self.rect = pygame.Rect(x, y, w, h)

    def update(self):
        if self.kind == 'inimigo':
            self.rect.x += self.dir * self.speed
            if self.rect.x < 200 or self.rect.x > 1400:
                self.dir *= -1

    def take_damage(self, dmg=1):
        if self.kind == 'inimigo':
            self.health -= dmg

    def draw(self, surface, cam_off):
        if self.kind == 'buraco':
            # desenha o rombo.png na posição original
            surface.blit(self.image, self.img_rect.move(-cam_off, 0))
        elif self.kind == 'inimigo':
            if self.image:
                surface.blit(self.image, self.rect.move(-cam_off, 0))
            else:
                pygame.draw.rect(surface, (200,0,0), self.rect.move(-cam_off, 0))
            # barra de vida
            bw    = self.rect.width
            ratio = max(0, self.health / 3)
            bg_bar = pygame.Rect(self.rect.x-cam_off, self.rect.y-7, bw, 4)
            fg_bar = pygame.Rect(self.rect.x-cam_off, self.rect.y-7, bw*ratio, 4)
            pygame.draw.rect(surface, (50,50,50), bg_bar)
            pygame.draw.rect(surface, (0,255,0),   fg_bar)
        else:
            # outros tipos
            colors = {'lixo':(100,100,100), 'fogo':(255,100,0)}
            col = colors.get(self.kind, (255,255,255))
            pygame.draw.rect(surface, col, self.rect.move(-cam_off, 0))
