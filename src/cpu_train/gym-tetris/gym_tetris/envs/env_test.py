import gym
import numpy as np
import pygame as pg
import time
import sys
from tetris_ctl import minos

# data for single play
num_rows = 23
num_columns = 10

block_size = 60
screen_width = block_size * 40 
screen_length = block_size * 22

field_width = block_size * 10
field_length = block_size * 20
field_x = block_size * 7
field_y = block_size * 1

hold_ratio = 0.8
hold_block_size = block_size * hold_ratio
hold_width = hold_block_size * 5
hold_length = hold_block_size * 5
hold_x = block_size * 1
hold_y = block_size * 8
hold_text_x = block_size * 1
hold_text_y = block_size * 7

score_width = block_size * 5
score_length = block_size * 1
score_x = block_size * 1
score_y = block_size * 17
score_text_x = block_size * 1
score_text_y = block_size * 16


nexts_ratio = 0.7
nexts_block_size = block_size * nexts_ratio
nexts_width = nexts_block_size * 5
nexts_length = nexts_block_size * 5
nexts_text_x = field_x + field_width + block_size * 2
nexts_text_y = block_size * 1
nexts_x = [field_x + field_width + block_size * 2] * 5
nexts_y = [nexts_text_y + block_size + i * (nexts_length + 10) for i in range(5)]

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

COLOR_BG = (43, 43, 43)
COLOR_I = (38, 203, 226)
COLOR_J = (0, 0, 200)
COLOR_L = (221, 109, 23)
COLOR_O = (243, 250, 0)
COLOR_S = (114, 238, 0)
COLOR_T = (140, 3, 140)
COLOR_Z = (250, 0, 0)
# color for fires
COLOR_F = (65, 85, 86)

COLORS = [COLOR_BG, COLOR_I, COLOR_J, COLOR_L, COLOR_O, COLOR_S, COLOR_T, COLOR_Z, COLOR_F]

# View functions here
def draw_hold(screen):
    # show the square blank for held mino
    pg.draw.rect(screen, COLOR_BG, [hold_x, hold_y, hold_width, hold_length])

# show field based on its contents
# draw dropping tetriminos as well
def draw_field(self):
    pg.draw.rect(screen, BLACK, [field_x, field_y, field_width, field_length], 5)
    pg.draw.rect(screen, COLOR_BG, [field_x, field_y, field_width, field_length])

def draw_nexts(self):
    # show string "NEXT"
    for i in range(5):
        pg.draw.rect(screen, COLOR_BG, [nexts_x[i], nexts_y[i], nexts_width, nexts_length])

def screen_init(screen):
    screen.fill(BLACK)
    draw_hold(screen)
    draw_field(screen)
    draw_nexts(screen)

# Note that this doesn't update screen if there is nothing in hold
def update_hold(screen, hold_mino_id):
    draw_hold(screen)
    if hold_mino_id != None:
        # delete current drawing first
        draw_mino(screen, hold_mino_id, hold_x, hold_y, hold_block_size, 0)


def update_score(self, score, score_text):
    # reset
    pg.draw.rect(self.screen, COLOR_BG, [score_x, score_y, score_width, score_length])
    # reset text
    pg.draw.rect(self.screen, BLACK, [score_x, score_y + block_size, field_x - score_x, score_length])

    # draw new value
    font = pg.font.Font(None, block_size)
    txt = font.render(str(score), True, WHITE)
    self.screen.blit(txt, [score_x, score_y])
    # show string "SCORE"
    font = pg.font.Font(None, block_size)
    txt = font.render(score_text, True, WHITE)
    self.screen.blit(txt, [score_x, score_y + block_size])

def update_field(screen, field):
    draw_field(screen)
    for y in range(20):
        for x in range(10):
            if field[y + 3][x] > 0: # if there is a block
                color = COLORS[field[y + 3][x]]
                start_x = block_size * x + field_x
                start_y = block_size * y + field_y
                pg.draw.rect(screen, color, [start_x, start_y, block_size, block_size])
                # enclose it with bg color line
                pg.draw.rect(screen, COLOR_BG, [start_x, start_y, block_size, block_size], 1)

def draw_mino(screen, mino_id, draw_x, draw_y, b_size, rot):
    mino_layout = minos[mino_id].block_data[rot] # 4 x 2
    for xy in mino_layout:
        d_x = draw_x + xy[0] * b_size
        d_y = draw_y + xy[1] * b_size
        pg.draw.rect(screen, COLORS[mino_id], [d_x, d_y, b_size, b_size])
        pg.draw.rect(screen, COLOR_BG, [d_x, d_y, b_size, b_size], 1)

def update_nexts(screen, next_minos):
    for i in range(5):
        draw_x = nexts_x[i]
        draw_y = nexts_y[i]
        pg.draw.rect(screen, COLOR_BG, [draw_x, draw_y, nexts_width, nexts_length])
        draw_mino(screen, next_minos[i], draw_x, draw_y, nexts_block_size, 0)

def update_drop(screen, dropping_mino):
    if dropping_mino != None:
        d_x = dropping_mino.current_pos[0] * block_size + field_x
        d_y = dropping_mino.current_pos[1] * block_size + field_y - (23-20) * block_size
        draw_mino(screen, dropping_mino.mino_id, d_x, d_y, block_size, dropping_mino.current_rot)
        pg.draw.rect(screen, BLACK, [field_x, 0, field_width, block_size])
        

def screen_update(screen, env):
    ctl = env.controller
    update_hold(screen, ctl.hold_mino_id)
    update_field(screen, ctl.field)
    update_nexts(screen, ctl.next_minos)
    update_drop(screen, ctl.dropping_mino)

env = gym.make("gym_tetris:tetris-v0")

pg.init()
pg.display.set_caption("tetris env test")
screen = pg.display.set_mode((screen_width, screen_length))
screen_init(screen)
pg.display.update()

while True:
    obs = None
    reward = 0
    is_done = False
    event = pg.event.wait()
    if event.type == pg.QUIT:
        pg.quit()
        sys.exit()
    elif event.type == pg.KEYDOWN:
        if event.key == pg.K_a:
            obs, reward, is_done, _ = env.step(1)
        elif event.key == pg.K_s:
            obs, reward, is_done, _ = env.step(0)
        elif event.key == pg.K_z:
            obs, reward, is_done, _ = env.step(4)
        elif event.key == pg.K_w:
            obs, reward, is_done, _ = env.step(5)
        elif event.key == pg.K_RIGHT:
            obs, reward, is_done, _ = env.step(2)
        elif event.key == pg.K_LEFT:
            obs, reward, is_done, _ = env.step(3)
        elif event.key == pg.K_SPACE:
            obs, reward, is_done, _ = env.step(6)

    print(np.array(obs))
    if reward > 0:
        print("reward is " + str(reward))
    if is_done:
        env.reset()

    screen_update(screen, env)
    pg.display.update()

    pg.event.clear()
