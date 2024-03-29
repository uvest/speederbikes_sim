import pygame

class Road(pygame.sprite.Sprite):
    def __init__(self, width, height, color:tuple=(22, 22, 22)) -> None:
        # contains the background and its width
        self.width = width
        self.height = height
        self.color = color

        # =======
        self.line_width = 3
        self.lane_width = self.width - self.line_width * 2

        self.image = pygame.Surface([self.width, self.height])
        self.rect = self.image.get_rect()

        # fill with background color and add left and right lines
        self.update()

    def _addBorderLines(self):
        self.left_line = pygame.draw.line(
            self.image,
            (222, 222, 222),
            (1, 0), (1, self.height),
            width=self.line_width
        )
        self.right_line = pygame.draw.line(
            self.image,
            (222, 222, 222),
            (self.width - self.line_width + 1, 0), (self.width - self.line_width + 1, self.height),
            width=self.line_width
        )

    def set_color(self, color:tuple):
        self.color = color
        
    def update(self):
        self.image.fill(self.color)
        self._addBorderLines()

    def render(self, canvas:pygame.Surface):
        canvas.blit(self.image, self.rect)