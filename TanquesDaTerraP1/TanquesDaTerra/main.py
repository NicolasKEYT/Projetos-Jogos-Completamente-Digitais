import pygame
from ui_menu import mostrar_menu

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Tanques da Terra")

    fase_func = mostrar_menu(screen)
    fase_func(screen)

    pygame.quit()

if __name__ == "__main__":
    main()