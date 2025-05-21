#Diego Estevão Lopes de Queiroz - 10419038
#Nicolas Gonçalves Santos - 10418047
#Kauã Paixão - 10418548
import pygame
from tank_sol import TankSol
from obstacles import Obstacle
from camera import Camera

def iniciar_fase_sol(screen):
    clock = pygame.time.Clock()
    tank = TankSol(100, 500)  # Cria o tanque na posição inicial (100, 500)
    inimigos = [Obstacle(400,500,40,40,'inimigo'), Obstacle(700,500,40,40,'inimigo')]  # Lista de inimigos
    cam = Camera(1600, 600)  # Inicializa a câmera com largura e altura do nível
    running = True
    while running:
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit(); exit()  # Fecha o jogo se clicar no X da janela
        keys = pygame.key.get_pressed()
        tank.handle_input(keys)  # Atualiza controles do tanque
        tank.update()            # Atualiza posição do tanque

        cam.update(tank.rect)    # Atualiza a câmera para seguir o tanque
        screen.fill((135,206,235))  # Preenche o fundo com cor de céu
        for obs in inimigos:
            obs.draw(screen, cam.offset)  # Desenha cada inimigo ajustando pela câmera
        tank.draw(screen, cam.offset)     # Desenha o tanque ajustando pela câmera

        pygame.display.flip()  # Atualiza a tela
        clock.tick(60)         # Limita o FPS para 60
