#Diego Estevão Lopes de Queiroz - 10419038
#Nicolas Gonçalves Santos - 10418047
#Kauã Paixão - 10418548
import pygame
import os
from ui_menu import mostrar_menu, mostrar_pagina_inicial, tocar_musica_menu, mostrar_pagina_init

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
    pixel_font_path = os.path.join(BASE_DIR, 'assets', 'fonts', 'pixel.ttf')
    font = pygame.font.Font(pixel_font_path, 32)
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
                # Voltar para a tela anterior ao apertar ESC
                elif e.key == pygame.K_ESCAPE:
                    mostrar_pagina_init(screen)
                    return None
                # Limite de 10 caracteres
                elif len(name) < 10 and e.unicode.isprintable():
                    name += e.unicode
        screen.fill((0, 0, 0))
        screen.blit(ui_img, (0, 0))
        txt_surf = font.render(name, True, (255, 255, 255))
        box_rect = pygame.Rect(225, sh//2 - 10, sw - 200, 40)
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

def mostrar_tela_dificuldade(screen):
    """Exibe a tela para o jogador escolher a dificuldade."""
    tocar_musica_menu()
    telaDificuldade = pygame.image.load(
        os.path.join(BASE_DIR, 'assets', 'ui', 'telaDificuldade.png')
    ).convert_alpha()
    telaDificuldade = pygame.transform.scale(telaDificuldade, screen.get_size())
    screen.blit(telaDificuldade, (0, 0))

    deslocamento = 50
    largura_botao = 570
    altura_botao = 90
    x_centro = (screen.get_width() - largura_botao) // 2
    y_facil = 55 + deslocamento
    y_medio = 220 + deslocamento
    y_dificil = 375 + deslocamento

    botoes = {
        "facil": pygame.Rect(x_centro, y_facil, largura_botao, altura_botao),
        "medio": pygame.Rect(x_centro, y_medio, largura_botao, altura_botao),
        "dificil": pygame.Rect(x_centro, y_dificil, largura_botao, altura_botao)
    }

    pygame.display.update()

    escolhendo = True
    dificuldade_escolhida = None
    while escolhendo:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None  # Volta para o menu
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for nome, rect in botoes.items():
                    if rect.collidepoint(pos):
                        dificuldade_escolhida = nome
                        escolhendo = False
    return dificuldade_escolhida

def mostrar_tela_fim(screen, tipo, pontuacao=0):
    """Exibe a tela de vitória ou derrota e toca o som correspondente."""
    base = os.path.dirname(__file__)
    sons_dir = os.path.join(base, 'assets', 'sons')
    pygame.mixer.music.stop()  # Pare a música de fundo antes de tocar o som de fim
    if tipo == "vitoria":
        som_vitoria = pygame.mixer.Sound(os.path.join(sons_dir, 'vitoria.wav'))
        som_vitoria.set_volume(0.4)  # ajuste o volume aqui (exemplo: 40%)
        som_vitoria.play()
    elif tipo == "derrota":
        som_derrota = pygame.mixer.Sound(os.path.join(sons_dir, 'derrota.wav'))
        som_derrota.set_volume(0.4)  # ajuste o volume aqui (exemplo: 40%)
        som_derrota.play()
    # Resto da função para mostrar a tela de fim...

def main():
    """Função principal do jogo: gerencia fluxo de telas, nome, perfil e fases."""
    pygame.init()
    pygame.mixer.init()  # Inicializa o mixer de áudio
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Tanques da Terra")

    # Tela inicial e entrada de nome
    mostrar_pagina_inicial(screen)
    player_name = None
    while not player_name:
        player_name = inputar_nome(screen)
        if player_name is None:
            mostrar_pagina_init(screen)
    if not os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, 'w') as f:
            f.write(f"{player_name},0\n")

    while True:
        fase_fun = mostrar_menu(screen)
        if fase_fun is None:
            break

        dificuldade = mostrar_tela_dificuldade(screen)
        if dificuldade is None:
            continue  # Volta para o menu

        # Chama a função da fase escolhida, passando a dificuldade se necessário
        if fase_fun.__name__ in ("iniciar_fase_sol", "iniciar_fase_agua","iniciar_fase_semente"):
            pontos = fase_fun(screen, dificuldade) or 0
        else:
            pontos = fase_fun(screen) or 0
        salvar_perfil(player_name, pontos)

    pygame.quit()

if __name__ == '__main__':
    main()
