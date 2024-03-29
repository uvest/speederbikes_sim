import pygame

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x:int, y:int, width:int, map:tuple, speed:float=300., color:tuple=(222, 222, 222), background_color:tuple=(0,0,0)) -> None:
        # contains the obstacle parts arranges such that there is at least one hole.
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.map = map

        self.speed = speed
        self.color = color
        self.background_color = background_color

        # ======
        self.n_parts = len(map)
        self.part_width = int(round(self.width / self.n_parts))
        self.part_limits = [[(self.part_width) * i, (self.part_width) * (i+1) - 1] for i in range(self.n_parts)]

        # because of rounding errors the most right limit may not coincide with the right border of image.
        self.part_limits[-1][1] = self.width

        # # manually add one to the last part's right border (because of pixel-perfect matching road width)
        # self.part_limits[-1][1] += 1

        # ======
        self.obstacle_height = 5

        # # DEBUG
        # if self.y > 0:
        #     self.background_color = (200, 0, 0)

        self.image = pygame.Surface([self.width, self.obstacle_height])
        self.image.fill(self.background_color)
        
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.parts = []
        for i, entry in enumerate(self.map):
            if entry:
                # print(f"DEBUG: self.part_limits[{i}]: {self.part_limits[i]}" )
                part = pygame.draw.line(
                    self.image, 
                    self.color,
                    (self.part_limits[i][0], self.y),
                    (self.part_limits[i][1], self.y),
                    width=self.obstacle_height # self.width
                )
                self.parts.append(part)
    
    def update(self, dt) -> None:
        self.y = self.y + self.speed * dt
        self.rect.y = self.y

    def render(self, canvas:pygame.Surface) -> None:
        canvas.blit(self.image, self.rect)
