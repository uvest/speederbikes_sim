import pygame
import numpy as np

from speederbikes_sim.objects.level import Level

# inherit from sprite class?
class Agent(pygame.sprite.Sprite):
    def __init__(self, x:int, y:int, level:Level, size:int=15, speed:float=200, color:tuple=(50, 55, 220)) -> None:
        """_summary_
        Args:
            x (_type_): _description_
            y (_type_): _description_
            size (int, optional): radius of circle. Defaults to 15.
            speed (float, optional): _description_. Defaults to 200.
            color (tuple, optional): _description_. Defaults to (155, 20, 220).
        """
        super().__init__()
        self.size = size
        self.speed = speed
        self.color = color
        self.level = level

        self.x = x
        self.y = y

        # =====
        self.image = pygame.Surface([self.size*2, self.size*2])
        self.image.fill((0, 155, 155))
        self.body = pygame.draw.circle(
            self.image,
            self.color,
            (self.size, self.size),
            self.size
        )
        self.rect = self.image.get_rect()

        # put own sprite in a group
        self.group = pygame.sprite.GroupSingle(self)

        # ====
        self.rect.x = self.x - self.size
        self.rect.y = self.y - self.size

    def collided(self):
        """Checks if this agent collides with one of the level's obstacles using custom collision logic.
        Returns:
            _type_: _description_
        """
        colliders = pygame.sprite.spritecollide(self, self.level.obstacles_sprite_group, dokill=False, collided=self.level._checkCollision)

        return len(colliders) > 0

        # if len(colliders) > 0:
        #     print(f"# of detected collisions: {len(colliders)}")
        #     for collider in colliders:
        #         print(collider.map)
        #     return True	
        
        # return False


    def update(self, action:int, dt):
        assert( action in [-1, 0, 1] )
        self.x = self.x + action * self.speed * dt

        # limit movement to stay on the road, may even stay inside road lines:
        _left = (self.level.left_border + self.size) #+ self.level.road.line_width
        _right = (self.level.right_border - self.size) #- self.level.road.line_width
        self.x = np.clip(self.x, _left, _right, dtype=float)

        self.rect.x = self.x - self.size

    def render(self, canvas:pygame.Surface):
        canvas.blit(self.image, self.rect)


# class Agent2():
#     # conatins the agent sprite, its position and update logic.
#     def __init__(self, canvas:Surface|None, x:int=None, size:int=30, speed:float=400., window_size:int|None=512, window:Surface|None=None) -> None:
#         self.canvas = canvas

#         self.size = size
#         self.speed = speed

#         # need either window size or window to get size
#         assert (window_size is not None) or (window is not None)
#         self.window = window
#         self.window_size = window_size if self.window is None else self.window.get_width()

#         self.x = x if x is not None else self.window_size // 2
#         self.x = np.clip(self.x, 0, self.window_size - 1) # limit x position to given window size

#         # ============
#         self.y = int(self.window_size * 0.8)

#         self.body = pygame.draw.circle(
#             self.canvas,
#             (0, 55, 255),
#             (self.x, self.y), # reference point in middle of circel / # + 0.5 * self.size # would set reference point to left side of circle
#             self.size
#         )

#     def update(self, action:int, dt):
#         assert action in [-1, 1]
#         self.x += action * self.speed * dt
#         self.body.x = int(self.x)

#     def render(self):
#         if self.window is not None:
#             self.window.blit(self.canvas, self.canvas.get_rect())

