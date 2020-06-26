import gym
from gym import error, spaces, utils
from gym.utils import seeding

from tetris_ctl import controller

class TetrisEnv(gym.Env):

    def __init__(self):
        self.action_space = spaces.Discrete(7)
        self.observation_space = spaces.Box(low=0, high=2, shape=(29, 10))
        self.controller = controller()

    """
    action space
        0: move right
        1: move left
        2: rotate clockwise
        3: rotate counterclockwise
        4: soft drop
        5: hard drop
        6: hold
    """
    def step(self, action):
        reward = 0
        if action == 0:
            self.controller.move_x(1)
        elif action == 1:
            self.controller.move_x(-1)
        elif action == 2:
            self.controller.rotate(1)
        elif action == 3:
            self.controller.rotate(-1)
        elif action == 4:
            landed, reward = self.controller.soft_drop()
        elif action == 5:
            _, reward = self.controller.hard_drop()
        elif action == 6:
            self.controller.hold()
        
        obs = self.controller.get_state()
        is_done = self.controller.gameover

        return obs, reward, is_done, {}
            

    def reset(self):
        self.controller.reset()
        return self.controller.get_state()

    def render(self, mode='human'):
        pass
    def close(self):
        pass