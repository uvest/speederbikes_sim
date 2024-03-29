import gymnasium as gym
from gymnasium.core import Env
import numpy as np

class ArrayObservationWrapper(gym.ObservationWrapper):
    """NOT USABLE
    Instead I rewrote the environment directly. But if ever needed: Import and use like
    env = ArrayObservationWrapper(env, flatten=...)

    Args:
        gym (_type_): _description_
    """
    def __init__(self, env: Env, flatten:bool=False) -> None:
        super().__init__(env)
        self.flatten = flatten

        # =====
        obs_max_count = np.ceil(self.env.window_size / self.env.level.inter_obstacle_distance)

        obs_max_parts = self.env.level.n_lanes
        obst_obs_shape = ((obs_max_parts - 1) * 2 + 1,)

        self.observation_space = gym.spaces.Box(low=0, high=self.env.window_size, shape=(obs_max_count, obst_obs_shape))
    
    def observation(self, observation):
        new_obs = []
        agent = observation["agent"]
        new_obs.push(agent)

        # obs_max_parts = self.env.get_wrapper_attr("level").n_lanes
        # obst_obs_shape = ((obs_max_parts - 1) * 2 + 1,)

        new_obs = []
        for obst in observation["obstacles"]:
            xs = obst[:,:,0]
            ys = obst[:,:,1]

            assert len(np.unique(ys)) == 1
            y = ys.flatten()[0]

            # concatenate y value and x vlaue
            no = np.concatenate([np.array([y]), xs.flatten()])
            # fill observation for single obstacle to be of maximum possible size
            no = np.concatenate([no, np.zeros(self.observation_space.shape[1] - no.shape[0])])

            new_obs.append(no)
        new_obs = np.array(new_obs)

        # fill observation of obstacles to have maximum size given the maximum possible number of present obstacles
        
        new_obs = np.concatenate([
            new_obs,
            np.zeros(self.observation_space.shape[0] - new_obs.shape[0], new_obs.shape[1])
        ])

        if self.flatten:
            new_obs = new_obs.flatten()

        return new_obs

        
