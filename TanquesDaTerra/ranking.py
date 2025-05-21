#Diego Estevão Lopes de Queiroz - 10419038
#Nicolas Gonçalves Santos - 10418047
#Kauã Paixão - 10418548
import pygame
import os

BASE_DIR     = os.path.dirname(__file__)
PROFILE_FILE = os.path.join(BASE_DIR, 'player_profile.txt')

def mostrar_ranking(screen):
    pygame.font.init()
    clock = pygame.time.Clock()
    sw, sh = screen.get_size()
    # Carrega imagem de fundo
    bg_path = os.path.join(BASE_DIR, 'assets', 'ui', 'raw.png')
    if os.path.exists(bg_path):
        bg_img = pygame.image.load(bg_path).convert_alpha()
        bg_img = pygame.transform.scale(bg_img, (sw, sh))
    else:
        bg_img = None

    pixel_font_path = os.path.join(BASE_DIR, 'assets', 'fonts', 'pixel.ttf')
    font = pygame.font.Font(pixel_font_path, 20)
    font_small = pygame.font.Font(pixel_font_path, 22)

    # Área clicável do botão voltar 
    area_voltar = pygame.Rect(30, 30, 180, 90)

    # Carrega ranking do arquivo de perfil
    ranking = []
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line or ',' not in line:
                    continue
                nm, sc = line.split(',', 1)
                try:
                    sc = int(sc)
                except ValueError:
                    sc = 0
                ranking.append((nm, sc))
    # Ordena do maior para o menor pontuação
    ranking.sort(key=lambda x: x[1], reverse=True)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if area_voltar.collidepoint(e.pos):
                    return

        # Desenha fundo
        if bg_img:
            screen.blit(bg_img, (0, 0))
        else:
            screen.fill((30, 30, 40))

        # Exibe top 8, alinhando posição, nome e pontos em colunas fixas
        y = 170  # posição inicial
        pos_x = 80
        name_x = 190
        pts_x = sw - 220

        for idx, (nm, sc) in enumerate(ranking[:7], 1):
            # Limita o nome a 10 caracteres
            nome_exibido = nm[:10]
            pos_txt = font.render(f"{idx:2d}.", True, (255,255,255))
            name_txt = font.render(nome_exibido, True, (255,255,255))
            pts = font_small.render(f"{sc} pts", True, (255,220,0))

            # Alinha posição, nome e pontos em colunas
            screen.blit(pos_txt, (pos_x, y))
            screen.blit(name_txt, (name_x, y))
            screen.blit(pts, (pts_x, y))
            y += 54  # espaçamento maior

        pygame.display.flip()
        clock.tick(60)