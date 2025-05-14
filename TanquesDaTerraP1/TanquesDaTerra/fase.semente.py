import pygame
from tank_agua import TankAgua
from obstacles import Obstacle
from camera import Camera

def iniciar_fase_agua(screen):
    clock = pygame.time.Clock()
    tank = TankAgua(100, 500)
    # Lixo e fogo que bloqueiam o caminho
    obstaculos = [
        Obstacle(400, 520, 40, 40, 'lixo'),
        Obstacle(600, 520, 40, 40, 'fogo'),
        Obstacle(900, 520, 40, 40, 'lixo'),
        Obstacle(1200, 520, 40, 40, 'fogo')
    ]
    cam = Camera(width=1600, height=600)

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                exit()

        keys = pygame.key.get_pressed()
        tank.handle_input(keys)
        tank.update()

        cam.update(tank.rect)
        screen.fill((135, 206, 235))  # céu azul

        # Desenha lixo e fogo
        for o in obstaculos:
            o.draw(screen, cam.offset)

        # Desenha o tanque e seus jatos
        tank.draw(screen, cam.offset)

        pygame.display.flip()
        clock.tick(60)
