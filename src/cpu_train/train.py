from model import DQN

import torch
import torch.nn as nn
import torch.optim as optim

import time
import gym
import collections
import numpy as np
import argparse

from tensorboardX import SummaryWriter

MEAN_REWARD_BOUND = 20

GAMMA = 0.99
BATCH_SIZE = 32
REPLAY_SIZE = 10000
LEARNING_RATE = 1e-4
SYNC_TARGET_FRAMES = 1000
REPLAY_START_SIZE = 10000

EPSILON_DECAY_LAST_FRAME = 1000000
EPSILON_START = 0.8
EPSILON_FINAL = 0.01

Experience = collections.namedtuple(
    'Experience', field_names=['state', 'action', 'reward',
                               'done', 'new_state'])

class ExperienceBuffer:
    def __init__(self, capacity):
        self.buffer = collections.deque(maxlen=capacity)
    
    def __len__(self):
        return len(self.buffer)
    
    def append(self, exp):
        self.buffer.append(exp)
    
    def sample(self, batch_size):
        indices = np.random.choice(len(self.buffer), batch_size,
                replace=False)
        states, actions, rewards, dones, next_states = \
            zip(*[self.buffer[idx] for idx in indices])
        return np.array(states), np.array(actions), \
                np.array(rewards, dtype=np.float32), \
                np.array(dones, dtype=np.uint8), \
                np.array(next_states)
    
    def sample_n_steps(self, batch_size, n_steps):
        indices = np.random.choice(len(self.buffer) - n_steps + 1, batch_size,
                replace=False)
        n_states = []
        n_actions = []
        n_rewards = []
        n_dones = []
        n_next_states = []
        for idx in indices:
            states = []
            actions = []
            rewards = []
            dones = []
            next_states = []
            for i in range(n_steps):
                states.append(self.buffer[idx + i].state)
                actions.append(self.buffer[idx + i].action) 
                rewards.append(self.buffer[idx + i].reward) 
                dones.append(self.buffer[idx + i].done) 
                next_states.append(self.buffer[idx + i].new_state) 
                if self.buffer[idx + i].done:
                    break
            n_states.append(states)
            n_actions.append(actions)
            n_rewards.append(rewards)
            n_dones.append(dones)
            n_next_states.append(next_states)
        return n_states, n_actions, \
                n_rewards, n_dones, n_next_states


class Agent:
    def __init__(self, env, exp_buffer):
        self.env = env
        self.exp_buffer = exp_buffer
        self._reset()

    def _reset(self):
        self.state = env.reset()
        self.total_reward = 0.0

    @torch.no_grad()
    def play_step(self, net, epsilon=0.0, device="cpu"):
        done_reward = None

        if np.random.random() < epsilon:
            action = env.action_space.sample()
        else:
            state_a = np.array([self.state], copy=False)
            state_v = torch.tensor(state_a).to(device)
            q_vals_v = net(state_v)
            _, act_v = torch.max(q_vals_v, dim=1)
            action = int(act_v.item())

        new_state, reward, is_done, _ = self.env.step(action)
        self.total_reward += reward

        exp = Experience(self.state, action, reward,
                         is_done, new_state)
        self.exp_buffer.append(exp)
        self.state = new_state
        if is_done:
            done_reward = self.total_reward
            self._reset()
        return done_reward
    


def calc_loss(batch, net, tgt_net, device="cpu"):
    states, actions, rewards, dones, next_states = batch

    states_v = torch.tensor(np.array(
        states, copy=False)).to(device)
    next_states_v = torch.tensor(np.array(
        next_states, copy=False)).to(device)
    actions_v = torch.tensor(actions).to(device)
    rewards_v = torch.tensor(rewards).to(device)
    done_mask = torch.BoolTensor(dones).to(device)

    state_action_values = net(states_v).gather(
        1, actions_v.unsqueeze(-1)).squeeze(-1)
    with torch.no_grad():
        next_state_values = tgt_net(next_states_v).max(1)[0]
        next_state_values[done_mask] = 0.0
        next_state_values = next_state_values.detach()

    expected_state_action_values = next_state_values * GAMMA + \
                                   rewards_v
    return nn.MSELoss()(state_action_values,
                        expected_state_action_values)

def calc_loss_n_steps(batch, net, tgt_net, device="cpu", double=False):
    n_states, n_actions, n_rewards, n_dones, n_next_states = batch

    init_states = [n_states[i][0] for i in range(BATCH_SIZE)]
    states_v = torch.tensor(np.array(
        init_states, copy=False)).to(device)
    init_actions = [n_actions[i][0] for i in range(BATCH_SIZE)]
    actions_v = torch.tensor(np.array(init_actions)).to(device)

    # [Q, Q, ... ,Q]
    state_action_values = net(states_v).gather(
        1, actions_v.unsqueeze(-1)).squeeze(-1)
    # [y, y, ... ,y]
    expected_state_action_values = []
    gammas = []
    for i in range(BATCH_SIZE):
        y = 0.0
        for j in range(len(n_dones[i])):
            y += n_rewards[i][j] * (GAMMA ** j)
        expected_state_action_values.append(y)
        gammas.append(GAMMA ** len(n_dones[i]))
    rewards_v = torch.tensor(np.array(expected_state_action_values, dtype=np.float32)).to(device)

    next_states = [n_next_states[i][-1] for i in range(BATCH_SIZE)]
    next_states_v = torch.tensor(np.array(next_states, copy=False)).to(device) # [s', s', ...]
    dones = [n_dones[i][-1] for i in range(BATCH_SIZE)]
    done_mask = torch.BoolTensor(dones).to(device) # eg. [F, T, F, ...]
    next_state_values = None
    with torch.no_grad():
        if double:
            next_state_acts = net(next_states_v).max(1)[1] # [index, index, ...]
            next_state_values = tgt_net(next_states_v).gather(
                        1, next_state_acts.unsqueeze(-1)).squeeze(-1)
        else:
            next_state_values = tgt_net(next_states_v).max(1)[0]
        next_state_values[done_mask] = 0.0
        next_state_values = next_state_values.detach()

    gammas = torch.tensor(gammas).to(device)
    y = next_state_values * gammas + rewards_v
    #print("Updating Q : {0:.3f} with y : {1:.3f} + {2:.3f}".format(state_action_values[0], rewards_v[0], next_state_values[0]))
    return nn.MSELoss()(state_action_values, y)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", type=int, default=1)
    parser.add_argument("--double", default=False, action="store_true")
    args = parser.parse_args()
    n_steps = args.n
    is_double = args.double
    print(n_steps)
    print(is_double)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(device)

    env = gym.make("gym_tetris:tetris-v0")

    net = DQN(env.observation_space.shape,
                    env.action_space.n).to(device)
    """
    net.load_state_dict(torch.load("tetris-9000_6.pit"))
    net.eval()
    """
    tgt_net = DQN(env.observation_space.shape,
                    env.action_space.n).to(device)
    """
    tgt_net.load_state_dict(torch.load("tetris-9000_6.pit"))
    tgt_net.eval()
    """
    writer = SummaryWriter(comment="-tetris")

    buffer = ExperienceBuffer(REPLAY_SIZE)
    agent = Agent(env, buffer)
    epsilon = EPSILON_START

    optimizer = optim.Adam(net.parameters(), lr=LEARNING_RATE)
    total_rewards = []
    frame_idx = 0
    ts_frame = 0
    ts = time.time()
    best_m_reward = None

    
    while True:
        frame_idx += 1
        epsilon = max(EPSILON_FINAL, EPSILON_START -
                      frame_idx / EPSILON_DECAY_LAST_FRAME)

        reward = agent.play_step(net, epsilon, device=device)
        if reward is not None: # just ended one episode
            total_rewards.append(reward)
            speed = (frame_idx - ts_frame) / (time.time() - ts)
            ts_frame = frame_idx
            ts = time.time()
            m_reward = np.mean(total_rewards[-100:])
            print("%d: done %d games, reward %.3f, "
                  "eps %.2f, speed %.2f f/s" % (
                frame_idx, len(total_rewards), m_reward, epsilon,
                speed
            ))
            writer.add_scalar("epsilon", epsilon, frame_idx)
            writer.add_scalar("speed", speed, frame_idx)
            writer.add_scalar("reward_100", m_reward, frame_idx)
            writer.add_scalar("reward", reward, frame_idx)
            if best_m_reward is None or best_m_reward < m_reward:
                torch.save(net.state_dict(), 
                           "tetris-best_%.0f.pit" % m_reward)
                if best_m_reward is not None:
                    print("Best reward updated %.3f -> %.3f" % (
                        best_m_reward, m_reward))
                best_m_reward = m_reward
            if len(total_rewards) % 1000 == 0:
                torch.save(net.state_dict(), 
                           "tetris-%d.pit" % len(total_rewards))
            if m_reward > MEAN_REWARD_BOUND:
                torch.save(net.state_dict(), 
                           "tetris-best_%.0f.pit" % m_reward)
                print("Solved in %d frames!" % frame_idx)
                break

        if len(buffer) < REPLAY_START_SIZE:
            continue

        if frame_idx % SYNC_TARGET_FRAMES == 0:
            tgt_net.load_state_dict(net.state_dict())

        optimizer.zero_grad()
        #batch = buffer.sample(BATCH_SIZE)
        batch = buffer.sample_n_steps(BATCH_SIZE, n_steps)
        #loss_t = calc_loss(batch, net, tgt_net, device=device)
        loss_t = calc_loss_n_steps(batch, net, tgt_net, device=device, double=is_double)
        loss_t.backward()
        optimizer.step()
    writer.close()