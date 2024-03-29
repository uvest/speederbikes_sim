# import gym
# from gym import spaces
# farama's gymnasium as drop in for gym (gym no longer maintained '22)
import gymnasium as gym
from gymnasium import spaces

import pygame
import numpy as np
from typing import List, Optional, Tuple, Union, Any

from speederbikes_sim.objects.level import Level
from speederbikes_sim.objects.agent import Agent

class SpeederBikesEnv(gym.Env):
    metadata = {
        "render_modes": ["human", "rgb_array"], 
        # "control_modes": ["position", "velocity", "acceleration"],
        "render_fps": 60, #[60, 120, 144, 165, 244, 250]
        "observation_modes": ["dict", "array", "array_flatten", "rgb_array", "rgb_array_flatten"]
        }

    def __init__(self, render_mode=None, control_mode=None,
                 observation_mode:str="flatten",
                 lvl_n_lanes:int=3, lvl_speed:float=200,
                 lvl_road_width:int=350, agt_speed:float=200
                 ) -> None:
        """_summary_

        Args:
            render_mode (_type_, optional): _description_. Defaults to None.
            control_mode (_type_, optional): _description_. Defaults to None.
            observation_mode (str, optional): one of 'flatten', 'array', 'dict'. Defaults to "flatten".
        """
        # super().__init__()
        self.control_mode = control_mode
        self.observation_mode = observation_mode

        self.window_size = 512
        self._bg_color = (155, 155, 155)

        # observation space depends on level specifications, thus can only be set, when reset() was called.
        # Howevef, it is needed, thus we create a dummy space using the dict mode
        self.observation_space = self._define_observation_space(mode="dict")

        # you can always only go left or right or stay put.
        self.action_space = spaces.Discrete(3)

        # map action to direction
        self._action_to_direction = {
            0: -1,  # left
            1: 0,   # stand still
            2: 1    # right
        }

        # rendering specific attributes
        assert (render_mode is None) or (render_mode in self.metadata["render_modes"])
        self.render_mode = render_mode

        # will only be set if render_mode is human
        self.window = None
        self.clock = None

        self.lvl_n_lanes = lvl_n_lanes
        self.lvl_speed = lvl_speed
        self.lvl_road_width = lvl_road_width
        self.agt_speed = agt_speed

    def _define_observation_space(self, mode:str):
        # assume Level and Player have been initialized in self.reset()
        scalar_entry = spaces.Box(0, self.window_size - 1, shape=(1,), dtype=float)

        if mode == "dict":
            observation_space = spaces.Dict(
                {
                    "agent": scalar_entry, # x position
                    # list of level's visible obstacles's part limits plus y position
                    "obstacles": spaces.Sequence( # sequence of all visible obstacles
                        spaces.Sequence( # sequence of obstacle parts limits
                            spaces.Tuple([
                                spaces.Box(0, self.window_size - 1, shape=(2,), dtype=float),
                                spaces.Box(0, self.window_size - 1, shape=(2,), dtype=float) # coords of borders of one obstacle part
                            ])
                        )
                    ),
                    # "npcs": scalar_entry # list of x positions of other agents
                }
            )
        elif mode == "array":
            self.max_visible_obstcacles = np.ceil(self.window_size / self.level.inter_obstacle_distance).astype(int)
            self.n_entries_per_obstacle = (self.level.n_lanes - 1) * 2 + 1
            observation_space = spaces.Box(low=0, high=self.window_size - 1, shape=(self.max_visible_obstcacles, self.n_entries_per_obstacle), dtype=float)
        elif mode == "flatten":
            self.max_visible_obstcacles = np.ceil(self.window_size / self.level.inter_obstacle_distance).astype(int)
            self.n_entries_per_obstacle = (self.level.n_lanes - 1) * 2 + 1
            observation_space = spaces.Box(low=0, high=self.window_size - 1, shape=((self.max_visible_obstcacles + 1) * self.n_entries_per_obstacle,), dtype=float)
        elif mode == "rgb_array":
            observation_space = spaces.Box(low=0, high=255, shape=(self.window_size, self.window_size, 3), dtype=int)
        elif mode == "rgb_array_flatten":
            observation_space = spaces.Box(low=0, high=255, shape=(self.window_size * self.window_size * 3,), dtype=int)
        else:
            print("ERROR: wrong observation mode. Must be one of 'flatten', 'array', 'dict', 'rgb_array', 'rtb_array_flatten'.")
            raise ValueError
        
        return observation_space

    def _make_array_observation(self, obs:dict) -> np.array:
        agent_obs = np.array([self.agent.y, self.agent.x])
        # fill with zeros
        # TODO: might add left and right agent boundaries instead of center
        agent_obs = np.concatenate([
            agent_obs,
            np.zeros(self.n_entries_per_obstacle - agent_obs.shape[0])
        ])

        obst_obs = []
        for obst in obs["obstacles"]:
            try:
                xs = obst[:,:,0]
                ys = obst[:,:,1]
            except IndexError:
                # encountered empty obstacle
                xs = np.array([0])
                ys = np.array([0])

            assert len(np.unique(ys)) == 1
            y = ys.flatten()[0]

            # concatenate y value and x vlaue
            no = np.concatenate([np.array([y]), xs.flatten()])
            # fill observation for single obstacle to be of maximum possible size
            no = np.concatenate([no, np.zeros(self.n_entries_per_obstacle - no.shape[0])])

            obst_obs.append(no)
        obst_obs = np.array(obst_obs)

        # fill observation of obstacles to have maximum size given the maximum possible number of present obstacles
        obst_obs = np.concatenate([
            obst_obs,
            np.zeros((self.max_visible_obstcacles - obst_obs.shape[0], obst_obs.shape[1]))
        ])

        # put together agent and obstacle observations
        new_obs = np.concatenate([
            agent_obs.reshape(1, obst_obs.shape[1]),
            obst_obs
        ])

        return new_obs

    def _flatten_observation(self, obs:np.array) -> np.array:
        return obs.flatten()

    def _get_obs(self):
        obs = {
            "agent": np.array([(self.agent.x - self.agent.level.left_border)]),
            "obstacles": [],
        }
        for obstacle in self.level.obstacles:
            obstacle_observation = []
            for i, part in enumerate(obstacle.map):
                if part:
                    obstacle_observation.append(
                        np.array([
                            np.array((obstacle.part_limits[i][0], obstacle.y)),
                            np.array((obstacle.part_limits[i][1], obstacle.y))
                        ])
                    )
            obs["obstacles"].append(np.array(obstacle_observation))
        # simpler alternative:
        # for obstacle in self._level.obstacles:
        #     obs["obstacles"].append((obstacle.y, obstacle.map))
            
        # # convert to propper numpy array
        # obs["obstacles"] = np.array(obs["obstacles"])
            
        if self.observation_mode == "array":
            obs = self._make_array_observation(obs)
        if self.observation_mode == "flatten":
            obs = self._make_array_observation(obs)
            obs = self._flatten_observation(obs)

        # visual observeration as rgb array of scene
        if self.observation_mode == "rgb_array":
            obs = self.render()
        if self.observation_mode == "rgb_array_flatten":
            obs = self.render().flatten()


        return obs

    def _get_info(self):
        info = {
            "obs_info": "'agent' returns the x position relative to the current level/ road.\n\
                'obstacles' returns a list of all obstacles, each entry is a list of the obstacle's part limits coordinates",
            # distance to next obstacle
            "distance": 0
        }
        info["distance"] = self.agent.y - self.level.obstacles[0].y
        if info["distance"] < 0:
            info["distance"] = self.agent.y - self.level.obstacles[1].y
        return info

    def reset(self, *, seed:int|None = None, options:dict={}) -> Tuple[Any, dict]:
        """Resets the environment with the given options. Poosible keys are
        - lvl_n_lanes
        - lvl_speed
        - lvl_road_width
        - agt_speed
        Options overwrite the values set at initialization.
        Args:
            seed (int | None, optional): seed for RNG. currently not used. Defaults to None.
            options (dict | None, optional): sets environment behaviour. Defaults to None.
        Returns:
            Tuple[Any, dict]: observation, information
        """
        # need to call this in order to initialise self.np_random RNG properly
        super().reset(seed=seed)

        if self.render_mode == "human":
            # we need a window to show the canvas and a clock
            if self.window is None:
                pygame.init()
                pygame.display.init()
                self.window = pygame.display.set_mode((self.window_size, self.window_size))
            if self.clock is None:
                self.clock = pygame.time.Clock()

        # create background to draw on
        self.canvas = pygame.Surface((self.window_size, self.window_size))
        # # make background grey
        # self.canvas.fill(self._bg_color) 

        # create Level (and Road and first pseudo-random obstacles)
        self.lvl_n_lanes = options["lvl_n_lanes"] if "lvl_n_lanes" in options.keys() else self.lvl_n_lanes
        self.lvl_speed = options["lvl_speed"] if "lvl_speed" in options.keys() else self.lvl_speed
        self.lvl_road_width = options["lvl_road_width"] if "lvl_road_width" in options.keys() else self.lvl_road_width
        
        self.level = Level(window_size=self.window_size, n_lanes=self.lvl_n_lanes, speed=self.lvl_speed, road_width=self.lvl_road_width)
        
        # create Agent
        self.agt_speed = options["agt_speed"] if "agt_speed" in options.keys() else self.agt_speed
        self.agent = Agent(x = int(round(self.window_size/2)), y = int(self.window_size * 0.8), level=self.level, speed=self.agt_speed)
        # self._agent = Agent(canvas=self.canvas, speed=agt_speed, window_size=self.window_size, window=self.window)

        # create observation space
        self.observation_space = self._define_observation_space(self.observation_mode)

        # generate/ complete observation
        observation = self._get_obs()
        
        # generate/ complete information
        info = self._get_info()


        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    def step(self, action:Any) -> Tuple[Any, float, bool, bool, dict]:
        """Step once through the simulation. Takes a single action
        Args:
            action (Any): Requires action to be in action space [0, 1, 2]
        Returns:
            Tuple[Any, float, bool, bool, dict]: obs, reward, terminated, truncated (stopped because of time limits), info
        """
        # return super().step(action)
        if isinstance(action, np.ndarray):
            
            action = action.item()
        agent_control = self._action_to_direction[action]
        dt = 1 / self.metadata["render_fps"] # 60 fps -> 0.0166 s

        # update agent
        self.agent.update(agent_control, dt)

        # update level
        self.level.update(dt)

        # update npcs

        # get additional information
        terminated = self.agent.collided()

        # define reward function
        reward = -100 if terminated else 1

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, terminated, False, info


    # ========================
    # rendering
    def render(self): # -> RenderFrame | List[RenderFrame] | None:
        """Behaviour defined by convention:
        “rgb_array”: Return a single frame representing the current state of the environment. 
            A frame is a np.ndarray with shape (x, y, 3) representing RGB values for an x-by-y pixel image.
        “human”: The environment is continuously rendered in the current display or terminal, usually for human consumption. 
            This rendering should occur during step() and render() doesn’t need to be called. Returns None.

        Returns:
            _type_: None or np.ndarray
        """
        if self.render_mode == "rgb_array":
            return self._render_frame("rgb_array")
        if self.observation_mode == "rgb_array":
            return self._render_frame("rgb_array")

    def _render_frame(self, mode:str|None=None):
        if mode is None:
            mode = self.render_mode
        ## collect all objects on the canvas
        # draw background
        self.canvas.fill(self._bg_color) 

        # draw level on canvas
        self.level.render(self.canvas)

        # draw agent on canvas
        self.agent.render(self.canvas)

        # draw npcs

        if mode == "human":
            # copy everything that was drawn to the canvas to the window
            # draws the content of the Surface self.canvas on the surface self.window
            self.window.blit(self.canvas, self.canvas.get_rect())

            pygame.event.pump()
            pygame.display.update()

            # update according to fps. adds delay, to keep the clock stable
            self.clock.tick(self.metadata["render_fps"])
        elif mode == "rgb_array":
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(self.canvas)), axes=(1, 0, 2)
            )

    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()

