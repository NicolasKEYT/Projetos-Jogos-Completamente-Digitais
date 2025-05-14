class Camera:
    def __init__(self, width, height):
        self.offset = 0
        self.width = width
        self.height = height

    def update(self, target_rect):
        # Centraliza a câmera no alvo, limitando ao cenário
        self.offset = target_rect.x - 800 // 2
        if self.offset < 0:
            self.offset = 0
        max_offset = self.width - 800
        if self.offset > max_offset:
            self.offset = max_offset