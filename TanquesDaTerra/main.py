import pygame
from ui_menu import mostrar_menu

def main():
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_caption("Tanques da Terra")
    clock = pygame.time.Clock()

    while True:
        fase = mostrar_menu(screen)
        fase(screen)
        pygame.time.delay(200)
        clock.tick(60)

if __name__ == "__main__":
    main()
