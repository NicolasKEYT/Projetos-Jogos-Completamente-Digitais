class Camera:
    def __init__(self, level_width, level_height):
        self.offset = 0
        self.level_width = level_width
        self.level_height = level_height

    def update(self, target_rect):
        x = target_rect.centerx - 800//2
        self.offset = max(0, min(x, self.level_width - 800))
