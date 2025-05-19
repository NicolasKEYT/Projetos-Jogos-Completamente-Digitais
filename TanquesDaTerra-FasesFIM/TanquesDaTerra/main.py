import pygame
from ui_menu import mostrar_menu, mostrar_pagina_inicial

def main():
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_caption("Tanques da Terra")
    clock = pygame.time.Clock()

    # Exibe a página inicial e só segue após o usuário escolher "ESCOLHER TANQUE"
    mostrar_pagina_inicial(screen)

    while True:
        fase = mostrar_menu(screen)
        if fase is None:
            break  # Permite sair do loop se mostrar_menu retornar None
        fase(screen)
        pygame.time.delay(200)
        clock.tick(60)

if __name__ == "__main__":
    main()