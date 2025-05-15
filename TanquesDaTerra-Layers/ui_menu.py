import pygame
from fase_sol import iniciar_fase_sol
from fase_semente import iniciar_fase_semente
from fase_agua import iniciar_fase_agua

def mostrar_menu(screen):
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None,48)
    txt1 = font.render("1 - Tank Sol", True, (200,200,0))
    txt2 = font.render("2 - Tank Semente", True, (100,200,100))
    txt3 = font.render("3 - Tank Água", True, (100,100,200))

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1: return iniciar_fase_sol
                if e.key == pygame.K_2: return iniciar_fase_semente
                if e.key == pygame.K_3: return iniciar_fase_agua

        screen.fill((30,30,30))
        screen.blit(txt1,(100,150))
        screen.blit(txt2,(100,250))
        screen.blit(txt3,(100,350))
        pygame.display.flip()
        clock.tick(60)
