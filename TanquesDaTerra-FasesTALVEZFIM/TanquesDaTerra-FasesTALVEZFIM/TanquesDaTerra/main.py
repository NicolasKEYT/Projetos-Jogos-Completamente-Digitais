import pygame
import os
from ui_menu import mostrar_menu, mostrar_pagina_inicial

# Diretório base e perfil
BASE_DIR     = os.path.dirname(__file__)
PROFILE_FILE = os.path.join(BASE_DIR, 'player_profile.txt')

def inputar_nome(screen):
    """Mostra a tela de entrada de nome e permite digitar o nome."""
    pygame.font.init()
    clock = pygame.time.Clock()
    sw, sh = screen.get_size()
    ui_img = pygame.image.load(os.path.join(BASE_DIR, 'assets', 'ui', 'nomeui.png')).convert_alpha()
    ui_img = pygame.transform.scale(ui_img, (sw, sh))
    font = pygame.font.SysFont('arial', 32, bold=True)
    name = ''
    active = True
    while active:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN and name:
                    active = False
                elif e.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                # Limite de 10 caracteres
                elif len(name) < 10 and e.unicode.isprintable():
                    name += e.unicode
        screen.fill((0, 0, 0))
        screen.blit(ui_img, (0, 0))
        txt_surf = font.render(name, True, (255, 255, 255))
        box_rect = pygame.Rect(100, sh//2 - 20, sw - 200, 40)
        screen.blit(txt_surf, (box_rect.x + 10, box_rect.y + 5))
        pygame.display.flip()
        clock.tick(30)
    return name


def salvar_perfil(name, score):
    """Salva ou atualiza o perfil somando a pontuação."""
    profiles = {}
    # Lê perfis existentes
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or ',' not in line:
                    continue
                nm, sc = line.split(',', 1)
                try:
                    profiles[nm] = int(sc)
                except ValueError:
                    profiles[nm] = 0
    # Soma a pontuação
    profiles[name] = profiles.get(name, 0) + score
    # Grava de volta
    with open(PROFILE_FILE, 'w') as f:
        for nm, sc in profiles.items():
            f.write(f"{nm},{sc}\n")


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Tanques da Terra")

    # Tela inicial e entrada de nome
    mostrar_pagina_inicial(screen)
    player_name = inputar_nome(screen)
    # Cria arquivo se não existir
    if not os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, 'w') as f:
            f.write(f"{player_name},0\n")

    # Loop de fases
    while True:
        fase_fun = mostrar_menu(screen)
        if fase_fun is None:
            break
        pontos = fase_fun(screen) or 0
        salvar_perfil(player_name, pontos)

    pygame.quit()

if __name__ == '__main__':
    main()
