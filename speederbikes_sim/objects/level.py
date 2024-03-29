import pygame
from speederbikes_sim.objects.road import Road
from speederbikes_sim.objects.obstacle import Obstacle

import numpy as np

class Level(pygame.sprite.Sprite):
    def __init__(self, window_size:int, n_lanes:int=5, speed:float=200., road_width:int=350) -> None:
        super().__init__()
        self.n_lanes = n_lanes
        self.speed = speed
        self.width:int = road_width
        self.height = window_size

        # =======
        self.inter_obstacle_distance = 220
        self.obstacle_entry_y = 0 # values < 0 lead to obstacles not being rendered
        self.obstacle_exit_y = self.height

        # =======
        # create surface to draw level on
        self.image = pygame.Surface([road_width, self.height])

        # center surface
        self.rect = self.image.get_rect()
        window_width:int = window_size
        self.rect.x = (window_width - self.width) / 2

        # contains a road as background
        self.road = Road(road_width, self.height)

        # store left and right level limits
        self.left_border = (window_width - self.width) / 2 + self.road.line_width
        self.right_border = window_width - (window_width - self.width) / 2 - self.road.line_width



        # generates a pseudo-random, infinite number of obstacles
        # create sprite group to hold all the obstacles
        self.obstacles_sprite_group = pygame.sprite.Group()
        # a list for my own obstacle management
        self.obstacles:list = []

        # add initially two obstacles.
        # TODO figure out why this isn't working
        # self._addObstacle(self.inter_obstacle_distance)
        # self._addObstacle(5)
        # for obst in self.obstacles:
        #     print(f"obst: y={obst.y}, map: {obst.map}")
        self._addObstacle()
            

    def _createObstacle(self, map:np.array, y:int|None=None) -> Obstacle:
        """Create new obstacle in the level's road.
        Returns:
            Obstacle: new obstacle instance
        """
        y = self.obstacle_entry_y if y is None else y
        new_obstacle = Obstacle(x=self.road.line_width,
                                y=y, 
                                width=self.road.lane_width, 
                                map=map, 
                                speed=self.speed, 
                                background_color=self.road.color)
        return new_obstacle

    def _deleteObstacle(self, obstacle:Obstacle) -> None:
        """Delete obstacle: Remove sprite, free resources.
        Args:
            obstacle (Obstacle): obstacle instance to be deleted
        """
        obstacle.kill()
        # might instead do:
        # self.obstacles_sprite_group.remove(obstacle)
        del(obstacle)

    def _addObstacle(self, y:int|None=None) -> None:
        """Sample a random map and check if it fits the current rules.
        Create new obstacle according to the map.
        Add obstacle to self.obstalces.
        """
        assert (self.obstacles is not None)
        # get last map if available
        try:
            last_map = self.obstacles[-1].map
        except IndexError:
            # if there is no last obstacle then this is fine
            last_map = None

        # define rules the new map has to fulfill
        def _isViable(map:np.array, last_map:np.array) -> bool:
            if map.sum() == self.n_lanes:
                return False
            
            # We generally don't want to have a free lane.
            # only generally though.
            if map.sum() == 0:
                if np.random.random() < 0.15:
                    return True
                else:
                    return False
            
            if last_map is not None:
                n_twice_empty_slots = ((map == 0) & (last_map == 0)).sum()

                # if there are holes at the same spot in at least 40 % of the slots or (2 slots in 5 lane case) in at least 2 slots,
                # let it go through in 5 % of cases
                if n_twice_empty_slots >= max( int(round(0.4 * self.n_lanes, 0)), 2):
                    if np.random.random() < 0.05:
                        return True
                    else:
                        return False
                    
                # if there are holes at the same spot in at least 20 % of the slots (1 slot in 3 or 5 lane case),
                # let it go through in 20 % of cases
                if n_twice_empty_slots >= int(round(0.2 * self.n_lanes, 0)):
                    if np.random.random() < 0.2:
                        return True
                    else:
                        return False

            # seems fine so far!
            return True

        # sample random obstacles until one fulfills all the rules
        map = np.random.randint(0, 2, size=self.n_lanes)
        i = 0
        while not _isViable(map, last_map):
            # print(f"DEBUG: last inviable map: {map}")
            map = np.random.randint(0, 2, size=self.n_lanes)
            i += 1
        # print(f"DEBUG: # of resamples needed: {i}")

        # create and append new obstacle
        new_obstacle = self._createObstacle(map, y)
        self.obstacles.append(new_obstacle)
        self.obstacles_sprite_group.add(new_obstacle)


    def _checkCollision(self, agent:pygame.sprite.Sprite, obstacle:pygame.sprite.Sprite) -> bool:
        """Collision logic. Currently, the agent's rectangular surface is used as coolider box
        Args:
            agent (pygame.sprite.Sprite): game agent
            obstacle (pygame.sprite.Sprite): one obstacle
        Returns:
            bool: whether there was a collision or not.
        """
        # use simple logic for now. This could be done better by using sprites all the way.
        agent_center_x = agent.x - agent.level.left_border
        a_l = agent_center_x - agent.size # left
        a_r = agent_center_x + agent.size # right
        a_t = agent.y - agent.size # top
        a_b = agent.y + agent.size # bottom

        o_t = obstacle.y # obstacle top bound
        o_b = obstacle.y + obstacle.obstacle_height # obstacle bottom bound

        # print(f"agent: {(a_l, a_r, a_t, a_b)} | obstacle: {(o_t, o_b)}")
        # if they overlap in the y dimension:
        if (a_t <= o_b) and (a_b >= o_t):
            for i, pos in enumerate(obstacle.map):
                if pos:
                    o_l, o_r = obstacle.part_limits[i] # obstacle bounds left and right
                    # check for overlaps in x dimension and return True if overlapping
                    if (a_r >= o_l) and (a_l <= o_r):
                        return True
        return False


    def update(self, dt):
        # update road
        self.road.update()

        # check if new obstacle should be created
        if self.obstacles[-1].y >= self.inter_obstacle_distance:
            self._addObstacle()

        # check if old obstacle should be deleted
        if self.obstacles[0].y >= self.obstacle_exit_y:
            self._deleteObstacle(self.obstacles.pop(0))

        # update all obstacle positions
        self.obstacles_sprite_group.update(dt)
        # for obstacle in self.obstacles:
        #     obstacle.update(dt)
        

    def render(self, canvas:pygame.Surface):
        # render road to level canvas
        self.road.render(self.image)

        # render obstacles to level canvas
        self.obstacles_sprite_group.draw(self.image)
        # for obstacle in self.obstacles:
        #     obstacle.render(self.image)

        # render level canvas on given canvas
        canvas.blit(self.image, self.rect)