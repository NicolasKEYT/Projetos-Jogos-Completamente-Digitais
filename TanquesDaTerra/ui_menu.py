import pygame
from fase_sol import iniciar_fase_sol
from fase_semente import iniciar_fase_semente
from fase_agua import iniciar_fase_agua

def mostrar_menu(screen):
    clock = pygame.time.Clock()
    menu_img = pygame.image.load("TanquesDaTerra/assets/ui/uiMenu.png").convert_alpha()
    menu_img = pygame.transform.scale(menu_img, (800, 600))

    # Defina as áreas dos botões (ajuste conforme o layout da imagem)
    btn_sol = pygame.Rect(40, 90, 700, 110)      # x, y, largura, altura
    btn_agua = pygame.Rect(40, 230, 700, 110)
    btn_semente = pygame.Rect(40, 370, 700, 110)

    pygame.draw.rect(screen, (255,255,0), btn_sol, 2)
    pygame.draw.rect(screen, (0,255,255), btn_agua, 2)
    pygame.draw.rect(screen, (0,255,0), btn_semente, 2)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if btn_sol.collidepoint(e.pos):
                    return iniciar_fase_sol
                if btn_agua.collidepoint(e.pos):
                    return iniciar_fase_agua
                if btn_semente.collidepoint(e.pos):
                    return iniciar_fase_semente

        screen.fill((30,30,30))
        screen.blit(menu_img, (0, 0))
        # Opcional: desenhe retângulos dos botões para depuração
        # pygame.draw.rect(screen, (255,255,0), btn_sol, 2)
        # pygame.draw.rect(screen, (0,255,255), btn_agua, 2)
        # pygame.draw.rect(screen, (0,255,0), btn_semente, 2)
        pygame.display.flip()
        clock.tick(60)