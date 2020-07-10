import numpy as np
import collections
import random
import copy
import torch
from tetris_utils import fire

from tetris_data import *



class agent:
    def __init__(self, env, v_net, f_conn):
        self.v_net = v_net
        self.env = env
        self.f_conn = f_conn
        self.incoming_fire = fire()
    
        self.env.reset()

    def step(self, epsilon=0.0):
        explore_result = self.explore()

        action_seq = None
        if np.random.random() < epsilon:
            action_seq = random.choice(explore_result)[0]
        else:
            action_seq, _ = max(explore_result, key=lambda item: item[1])
        
        for action in action_seq:
            _, _, _, info = self.env.step(action)

        #landed = info[0]
        sending_fire = info[1]

        if sending_fire > 0:
            remainder = self.incoming_fire.subtract(sending_fire)
            if remainder > 0:
                self.f_conn.send(remainder)
        # fire insertion to field
        num_fire = self.incoming_fire.countdown()
        if num_fire > 0:
            self.env.add_fire(num_fire)

        # line 20を超えたらゲームオーバー？
        height = self.env.controller.highest()
        return height > 20

    # returns [[action_seq, reward + values], ...]
    def explore(self):
        results = []
        net_inputs = []

        mino = self.env.controller.dropping_mino
        mino_idx = mino.mino_id - 1

        # rot_needed = [2, 4, 4, 1, 3, 4, 3]
        for rot in range(rot_needed[mino_idx]):
            x_len = 11 - mino_width[mino_idx][rot]
            for x in range(x_len):
                # add rotation action to action_seq rot times
                action_seq = [2 for i in range(rot)]

                # add move x action at required times
                x_offset = x - (mino.spawn_pos[0] + mino_left[mino_idx][rot])
                if x_offset > 0: # move right
                    action_seq.extend([0 for i in range(x_offset)])
                elif x_offset < 0: # move left
                    action_seq.extend([1 for i in range(-x_offset)])
                
                # add hard drop action
                action_seq.append(5)

                obs, reward, pos = self.step_venv(action_seq)
                obs = np.expand_dims(obs, axis=0)
                net_inputs.append(obs)
                results.append([action_seq, reward])

        # hold version
        if self.env.controller.hold_mino_id is not None:
            mino_idx = self.env.controller.hold_mino_id - 1
        else:
            mino_idx = self.env.controller.next_minos[0] - 1
        mino = self.env.controller.minos[mino_idx + 1]
        
        for rot in range(rot_needed[mino_idx]):
            x_len = 11 - mino_width[mino_idx][rot]
            for x in range(x_len):
                # add hold action first, then rotation action to action_seq rot times
                action_seq = [6] + [2 for i in range(rot)]

                # add move x action at required times
                x_offset = x - (mino.spawn_pos[0] + mino_left[mino_idx][rot])
                if x_offset > 0: # move right
                    action_seq.extend([0 for i in range(x_offset)])
                elif x_offset < 0: # move left
                    action_seq.extend([1 for i in range(-x_offset)])
                
                # add hard drop action
                action_seq.append(5)

                obs, reward, pos = self.step_venv(action_seq)
                obs = np.expand_dims(obs, axis=0)
                net_inputs.append(obs)
                results.append([action_seq, reward])
        # calculate value and add to results
        net_inputs_v = torch.tensor(net_inputs, dtype=torch.float32)
        values_v = self.v_net(net_inputs_v)

        for i, value in enumerate(values_v):
            results[i][1] += value.item()
        
        return results
                
    # simulates actions on virtual environment and returns observatio, reward and pos afterward
    def step_venv(self, action_seq):
        venv = copy.deepcopy(self.env)

        total_reward = 0.0
        obs = None
        info = [0, 0, [0, 0, 0]]
        for action in action_seq:
            obs, reward, _, info = venv.step(action)
            total_reward += reward
        
        return obs, total_reward, info[2]
    
    # search space where T mino with the angle=rot fits in the range from pos to floor
    # also, the space under it must be floor or some block so the mino would land on it 
    def search_t_space(self, pos, rot):
        open_pos = []
        field = self.env.controller.field
        while pos[1] < 22:
            if (self.collide_T(pos, rot) == False) and (self.collide_T([pos[0], pos[1] + 1]) == True):
                open_pos.append([pos[0], pos[1]])
            pos[1] += 1
        
        return open_pos

    # return True if it collides the field stack or floor when the T mino placed at pos with rotation=rot
    # note that this doesn't check wall collision because it's assumed not to collide both walls
    def collide_T(self, pos, rot):
        field = self.env.controller.field
        occupied_space = [[pos[0] + mino_layout[0], pos[1] + mino_layout[1]] for mino_layout in T_layout[rot]]

        # if any occupied block is under the floor, break
        if any(xy[1] > 22 for xy in occupied_space):
            return True

        for x, y in occupied_space:
            if field[y][x] > 0:
                return True
        
        return False

    def get_layout(self):
        field_copy = copy.deepcopy(self.env.controller.field)
        return field_copy

    def recv_fire(self):
        while self.f_conn.poll():
            self.incoming_fire.add(self.f_conn.recv())

