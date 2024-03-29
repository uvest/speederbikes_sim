from speederbikes_sim.envs.speederbikes_env import SpeederBikesEnv

# """
# If your environment is not registered, you may optionally pass a module to import,
# that would register your environment before creating it like this - env = gym.make('module:Env-v0'), 
# where module contains the registration code. 
# For the GridWorld env, the registration code is run by importing gym_examples so if it were not possible to import gym_examples explicitly,
# you could register while making by env = gym.make('gym_examples:gym_examples/GridWorld-v0). 
# This is especially useful when you're allowed to pass only the environment ID into a third-party codebase (eg. learning library). 
# This lets you register your environment without needing to edit the library's source code.
# See: https://www.gymlibrary.dev/content/environment_creation/#registering-envs
# """