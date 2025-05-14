import pygame
from fase_sol import iniciar_fase_sol
from fase_semente import iniciar_fase_semente
from fase_agua import iniciar_fase_agua

def mostrar_menu(screen):
    clock = pygame.time.Clock()
    fonte = pygame.font.SysFont(None, 48)
    escolhido = None

    while escolhido is None:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1:
                    escolhido = iniciar_fase_sol
                elif e.key == pygame.K_2:
                    escolhido = iniciar_fase_semente
                elif e.key == pygame.K_3:
                    escolhido = iniciar_fase_agua
        screen.fill((30, 30, 30))
        screen.blit(fonte.render("1. Tank Sol", True, (200,200,0)), (100,150))
        screen.blit(fonte.render("2. Tank Semente", True, (100,200,100)), (100,250))
        screen.blit(fonte.render("3. Tank Água", True, (100,100,200)), (100,350))
        pygame.display.flip()
        clock.tick(60)

    return escolhido