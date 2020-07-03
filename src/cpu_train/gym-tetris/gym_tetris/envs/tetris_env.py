import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np

from gym_tetris.envs.tetris_ctl import controller

class TetrisEnv(gym.Env):

    def __init__(self):
        self.action_space = spaces.Discrete(7)
        self.observation_space = spaces.Box(low=0, high=2, shape=(1, 29, 10), dtype=np.float32)
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
        landed = False
        fire = 0
        if action == 0:
            self.controller.move_x(1)
        elif action == 1:
            self.controller.move_x(-1)
        elif action == 2:
            self.controller.rotate(1)
        elif action == 3:
            self.controller.rotate(-1)
        elif action == 4 or action == 5:
            if action == 4:
                landed, reward, column_list, perfect_landed = self.controller.soft_drop()
            elif action == 5:
                landed, reward, column_list, perfect_landed = self.controller.hard_drop()
            fire = reward
            if reward > 0:
                print("line deletion happened " + str(reward))
            # punishment for making holes
            if landed:
                if perfect_landed:
                    reward += 0.3
                # holes = self.controller.hole_columns_at(column_list)
                # reward -= holes * 0.1
                # rewards if landed without holes
                #if holes == 0:
                    #reward += 0.3
                # punishment for the height of the stack
                # height = self.controller.highest()
                # reward -= height * 0.1
        elif action == 6:
            self.controller.hold()
        

        
        obs = np.array(self.controller.get_state(), dtype=np.float32)
        obs = np.expand_dims(obs, axis=0)
        is_done = self.controller.gameover

        return obs, reward, is_done, [landed, fire]
            

    def reset(self):
        self.controller.reset()
        obs = np.array(self.controller.get_state(), dtype=np.float32)
        obs = np.expand_dims(obs, axis=0)
        return obs
        #return self.controller.get_state()

    def render(self, mode='human'):
        pass
    def close(self):
        pass

    def add_fire(self, fire):
        self.controller.add_fire(fire)