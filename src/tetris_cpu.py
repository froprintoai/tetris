from tetris_view import online_view
from tetris_ctl import controller_cpu, agent_ctl

import multiprocessing as mp
import pygame as pg
import sys

def cpu(l_conn, f_conn, g_conn, lock):
    agent = agent_ctl()
    while True:
        # based on its observation, takes action
        agent.step()

        # send its layout
        lock.acquire()
        try:
            l_conn.send(agent.get_layout())
        finally:
            lock.release()

        # receive fire, and update observation
        # receive gameover, if so, break       


def cpu_play(screen):

    layout_lock = mp.Lock()
    p_layout_conn, c_layout_conn = mp.Pipe()
    p_fire_conn, c_fire_conn = mp.Pipe()
    p_gameover_conn, c_gameover_conn = mp.Pipe()

    # show basic screen
    v = online_view(screen)
    v.screen_init()
    ctl = controller_cpu(v, p_layout_conn, p_fire_conn, p_gameover_conn, layout_lock)

    p = mp.Process(target=cpu, args=(c_layout_conn, c_fire_conn, c_gameover_conn, layout_lock))

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
                    break

                ctl.update_view()
                pg.display.update()
                clock.tick(10)

                continue
        
        if ctl.check_gameover():
            break

        # receive fire and layout
        ctl.recv_fire()
        ctl.recv_layout()

        # update view
        ctl.update_view()
        pg.display.update()

        clock.tick(10)
