#Diego Estevão Lopes de Queiroz - 10419038
#Nicolas Gonçalves Santos - 10418047
#Kauã Paixão - 10418548
# tank_agua.py

import pygame
import os
from bullet import Bullet

class TankAgua:
    # Escala do sprite
    SCALE = 1.5

    def __init__(self, x, y):
        # 1) Carrega o PNG original do tanque de água
        base = os.path.dirname(__file__)
        sprite_path = os.path.join(base, 'assets', 'tanque_agua.png')
        original = pygame.image.load(sprite_path).convert_alpha()

        # 2) Calcula o novo tamanho e escala o sprite
        w, h = original.get_size()
        new_size = (int(w * self.SCALE), int(h * self.SCALE))
        scaled = pygame.transform.scale(original, new_size)

        # 3) Gera as duas orientações já escaladas (esquerda/direita)
        self.image_left  = scaled
        self.image_right = pygame.transform.flip(scaled, True, False)
        self.image = self.image_left

        # 4) Cria o rect já com o tamanho novo e define atributos iniciais
        self.rect    = self.image.get_rect(topleft=(x, y))
        self.vel     = 4           # Velocidade de movimento
        self.bullets = []          # Lista de projéteis disparados
        self.health  = 5           # Vida do tanque
        self.facing  = 'left'      # Direção inicial

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

        # X = disparar jato d'água na direção atual (limite de 3 projéteis)
        if keys[pygame.K_x] and len(self.bullets) < 3:
            if self.facing == 'left':
                bx, dx = self.rect.left, -6
            else:
                bx, dx = self.rect.right,  6
            by = self.rect.centery
            self.bullets.append(Bullet(bx, by, dx, (0,150,255)))

    def update(self):
        # Atualiza cada projétil e remove os que saem da tela
        for b in self.bullets[:]:
            b.update()
            if b.rect.x < 0 or b.rect.x > 2000:
                self.bullets.remove(b)

    def draw(self, surf, cam_off):
        # Desenha o tanque na tela, ajustando pela câmera
        surf.blit(self.image, self.rect.move(-cam_off, 0))
        # Barra de vida acima do tanque
        bw, ratio = self.rect.width, max(0, self.health / 5)
        pygame.draw.rect(surf, (255,0,0),
                         (self.rect.x - cam_off, self.rect.y - 8, bw, 5))
        pygame.draw.rect(surf, (0,255,0),
                         (self.rect.x - cam_off, self.rect.y - 8, bw * ratio, 5))
        # Desenha os tiros (projéteis de água)
        for b in self.bullets:
            b.draw(surf, cam_off)
