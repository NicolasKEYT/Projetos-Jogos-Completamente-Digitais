import pygame
from tank_agua import TankAgua
from obstacles import Obstacle
from camera import Camera


def iniciar_fase_agua(screen):
    clock = pygame.time.Clock()
    tank = TankAgua(100, 500)
    obstaculos = [Obstacle(400, 520, 40, 40, 'lixo'), Obstacle(600, 520, 40, 40, 'fogo')]
    cam = Camera(width=1600, height=600)
    running = True

    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); exit()

        keys = pygame.key.get_pressed()
        tank.handle_input(keys)
        tank.update()
        for o in obstaculos:
            o.update()

        cam.update(tank.rect)
        screen.fill((135, 206, 235))
        for o in obstaculos:
            o.draw(screen, cam.offset)
        tank.draw(screen, cam.offset)

        pygame.display.flip()
        clock.tick(60)