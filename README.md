# Speederbike simulation envirionment
RL focussed sim env using gymansium's gym implementation.

## Usage

After cloning the repository run from the folder where you cloned your project into

```bash
pip install -e speederbikes_sim/
```

In your code you need to import

```python
import gymnasium as gym
import speederbikes_sim

env = gym.make('speederbikes/SpeederBikes-v0', render_mode="human")
```

For creating a window

```python
env.reset()
```

you may provide the following arguments in a dictionary to reset (example values):

```python
env.reset(options={
    "lvl_n_lanes":5,
    "lvl_speed":400,
    "lvl_road_width":350, # should not exceed the window size which is by defautl 512
    "agt_speed": 300
})
```