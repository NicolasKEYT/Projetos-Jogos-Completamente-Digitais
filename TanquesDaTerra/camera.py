#Diego Estevão Lopes de Queiroz - 10419038
#Nicolas Gonçalves Santos - 10418047
#Kauã Paixão - 10418548
class Camera:
    def __init__(self, level_width, level_height):
        # Offset da câmera 
        self.offset = 0
        # Largura total do nível 
        self.level_width = level_width
        # Altura total do nível 
        self.level_height = level_height

    def update(self, target_rect):
        # Centraliza o alvo horizontalmente em uma janela de 800px de largura
        x = target_rect.centerx - 800 // 2
        # Limita o deslocamento entre 0 e o máximo possível 
        self.offset = max(0, min(x, self.level_width - 800))
