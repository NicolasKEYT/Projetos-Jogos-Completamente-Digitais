import pygame
from tank_semente import TankSemente
from obstacles import Obstacle
from camera import Camera


def iniciar_fase_semente(screen):
    clock = pygame.time.Clock()
    tank = TankSemente(100, 500)
    buracos = [Obstacle(350, 530, 80, 30, 'buraco'), Obstacle(750, 530, 80, 30, 'buraco')]
    cam = Camera(width=1600, height=600)
    running = True

    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); exit()

        keys = pygame.key.get_pressed()
        tank.handle_input(keys)
        tank.update()

        cam.update(tank.rect)
        screen.fill((135, 206, 235))
        for b in buracos:
            b.draw(screen, cam.offset)
        tank.draw(screen, cam.offset)

        pygame.display.flip()
        clock.tick(60)