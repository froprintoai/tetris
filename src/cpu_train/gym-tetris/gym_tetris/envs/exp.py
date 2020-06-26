import gym

env = gym.make("gym_tetris:tetris-v0")
print(env.observation_space)
env = gym.make("PongNoFrameskip-v4")
print(env.observation_space)