import pygame
from tank_sol import TankSol
from obstacles import Obstacle
from camera import Camera


def iniciar_fase_sol(screen):
    clock = pygame.time.Clock()
    tank = TankSol(100, 500)
    inimigos = [Obstacle(400, 500, 40, 40, 'inimigo'), Obstacle(700, 500, 40, 40, 'inimigo')]
    cam = Camera(width=1600, height=600)
    running = True

    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); exit()

        keys = pygame.key.get_pressed()
        tank.handle_input(keys)
        tank.update()
        for obs in inimigos:
            obs.update()

        cam.update(tank.rect)
        screen.fill((135, 206, 235))
        for obs in inimigos:
            obs.draw(screen, cam.offset)
        tank.draw(screen, cam.offset)

        pygame.display.flip()
        clock.tick(60)