# from gym.envs.registration import register
from gymnasium.envs.registration import register

register(
    id="speederbikes/SpeederBikes-v0",
    entry_point="speederbikes_sim.envs:SpeederBikesEnv",
    # max_episode_steps=300, # automatically generate done signal after 300 steps. will be flagged in info["TimeLimit.truncated"]
)

# more keyword arguments:
# reward_threshold float
# nondeterministic bool=False (true if this env is non-deterministic even after seeding)
# order_enforce (bool=True) adds OrderEnforcing Wrapper
# autoreset bool=False
# kwargs