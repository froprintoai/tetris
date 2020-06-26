import gym
import numpy as np

env = gym.make("gym_tetris:tetris-v0")
print(env.observation_space)
x = env.reset()
x = np.array(x)
print(x.shape)
print(x)
