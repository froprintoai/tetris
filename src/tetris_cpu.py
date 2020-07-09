from tetris_view import online_view
from tetris_ctl import controller_cpu, agent_ctl
from tetris_agent import agent
from model import v_net

import multiprocessing as mp
import pygame as pg
import gym
import torch
import sys
import time

def cpu(l_conn, f_conn, g_conn, lock):
    env = gym.make("gym_tetris:tetris-v0")
    net = v_net(env.observation_space.shape,
                    env.action_space.n)
    # net.load_state_dict(torch.load("tetris-best_3.pit", map_location=torch.device('cpu')))
    # net.eval()
    a = agent(env, net, f_conn)
    while True:
        # based on its observation, takes action
        is_done = a.step()
        if is_done:
            g_conn.send(True)
            break

        # send its layout
        lock.acquire()
        try:
            layout = a.get_layout()
            l_conn.send(layout)
        finally:
            lock.release()

        # receive fire, and update observation
        a.recv_fire()

        # receive gameover, if so, break       
        if g_conn.poll():
            g_conn.recv()
            break
        time.sleep(0.5)



def challenge_ai(screen):

    layout_lock = mp.Lock()
    p_layout_conn, c_layout_conn = mp.Pipe()
    p_fire_conn, c_fire_conn = mp.Pipe()
    p_gameover_conn, c_gameover_conn = mp.Pipe()

    # show basic screen
    v = online_view(screen)
    v.screen_init()
    ctl = controller_cpu(v, p_layout_conn, p_fire_conn, p_gameover_conn, layout_lock)

    p = mp.Process(target=cpu, args=(c_layout_conn, c_fire_conn, c_gameover_conn, layout_lock))
    p.start()

    clock = pg.time.Clock()
    tmr = 0
    hard_drop_sensitive = 0 # control the sensitivity for the key corresponding to hard drop
    gameover = False

    while True:
        if ctl.recv_gameover():
            break

        tmr = tmr + 1

        # check user input
        # if the block is rotated when it touches the stack or floor, tmr need to be decreased so it allows block to float for a while
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
        key = pg.key.get_pressed()
        if key[pg.K_a] == 1: # left
            ctl.move_x(-1)
        if key[pg.K_s] == 1: # right
            ctl.move_x(1)
        if key[pg.K_z] == 1: # down
            tmr += 6 
        if key[pg.K_w] == 1: # hard drop
            if hard_drop_sensitive == 0:
                ctl.hard_drop()
                gameover = ctl.next_round()
                if gameover:
                    p_gameover_conn.send(True)
                    break
                tmr = 0
                hard_drop_sensitive = 1
            else:
                hard_drop_sensitive = 0
        if key[pg.K_RIGHT] == 1: # rotate clockwise
            ctl.rotate(1)
        if key[pg.K_LEFT] == 1: # rotate counterclockwise
            ctl.rotate(-1)
        if key[pg.K_SPACE] == 1: #hold
            ctl.hold()

        # control soft drop
        if tmr > 7:
            hard_drop_sensitive = 0
            tmr = 0
            land = ctl.soft_drop()
            if land == 1:
                gamevoer = ctl.next_round()
                if gameover:
                    p_gameover_conn.send(True)
                    break

                ctl.update_view()
                pg.display.update()
                clock.tick(10)

                continue
        
        if ctl.check_gameover():
            p_gameover_conn.send(True)
            break

        # receive fire and layout
        ctl.recv_fire()
        ctl.recv_layout()

        # update view
        ctl.update_view()
        pg.display.update()

        clock.tick(10)
    p.join()