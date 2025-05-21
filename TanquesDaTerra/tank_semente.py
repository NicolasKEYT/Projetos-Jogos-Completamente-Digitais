#Diego Estevão Lopes de Queiroz - 10419038
#Nicolas Gonçalves Santos - 10418047
#Kauã Paixão - 10418548
import pygame
import os

class TankSemente:
    def __init__(self, x, y):
        # Carrega o sprite do tanque de semente
        base = os.path.dirname(__file__)
        sprite_path = os.path.join(base, 'assets', 'tanque_semente.png')
        original = pygame.image.load(sprite_path).convert_alpha()

        # Gera as duas orientações (esquerda/direita)
        self.image_left  = original
        self.image_right = pygame.transform.flip(original, True, False)
        self.image = self.image_left

        # Inicializa o retângulo de colisão e atributos do tanque
        self.rect       = self.image.get_rect(topleft=(x, y))
        self.vel        = 4
        self.plants     = []      # Lista de plantas (sementes plantadas)
        self.health     = 5
        self.facing     = 'left'
        self.max_plants = 5       # Limite de plantas que pode plantar

    def handle_input(self, keys):
        # Movimento para a esquerda
        if keys[pygame.K_a]:
            self.facing = 'left'
            self.image  = self.image_left
            self.rect.x -= self.vel
        # Movimento para a direita
        if keys[pygame.K_d]:
            self.facing = 'right'
            self.image  = self.image_right
            self.rect.x += self.vel

        # Planta uma semente se X pressionado e não atingiu o máximo
        if keys[pygame.K_x] and len(self.plants) < self.max_plants:
            if self.facing == 'left':
                px = self.rect.left - 40
            else:
                px = self.rect.right
            py = self.rect.bottom
            # Adiciona uma nova planta (como um retângulo simples)
            self.plants.append(pygame.Rect(px, py, 20, 20))

    def update(self):
        # Atualização do tanque (pode ser expandida)
        pass

    def draw(self, surf, cam_off):
        # Desenha o tanque ajustando pela câmera
        surf.blit(self.image, self.rect.move(-cam_off, 0))
        
