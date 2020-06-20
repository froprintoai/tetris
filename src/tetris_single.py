import pygame as pg
import sys

from tetris_ctl import controller
from tetris_view import view, pause
from tetris_layout import BLACK

def single_play(screen):
    
    # show basic screen
    v = view(screen)
    v.screen_init()


    # initiate controller
    ctl = controller(v)
    ctl.init()

    clock = pg.time.Clock()

    tmr = 0
    hard_drop_sensitive = 0 # control the sensitivity for the key corresponding to hard drop
    hold_used = False
    gameover = False

    while True:
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
                hold_used = False
                tmr = 0
                hard_drop_sensitive = 1
            else:
                hard_drop_sensitive = 0
        if key[pg.K_RIGHT] == 1: # rotate clockwise
            ctl.rotate(1)
        if key[pg.K_LEFT] == 1: # rotate counterclockwise
            ctl.rotate(-1)
        if key[pg.K_SPACE] == 1: #hold
            if hold_used == False:
                ctl.hold()
                hold_used = True
        if key[pg.K_p] == 1: #pause
            resume = pause(screen)
            if resume != True:
                break
            screen.fill(BLACK)

        # control soft drop
        if tmr > 7:
            hard_drop_sensitive = 0
            tmr = 0
            land = ctl.soft_drop()
            if land == 1:
                gamevoer = ctl.next_round()
                if gameover:
                    break
                hold_used = False

                ctl.update_view()
                pg.display.update()
                clock.tick(10)

                continue
        
        if ctl.check_gameover():
            break

        # update view
        ctl.update_view()
        pg.display.update()

        clock.tick(10)
