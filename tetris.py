from typing import List
import pygame as pg
import sys
import random
import time

"""
tetris implemented using pygame
employed MVC model, where Controller stands as a class, which contains Model, and View is provided as a bunch of functions

"""

list_2d = List[List[int]]
list_3d = List[List[List[int]]]

block_size = 60
screen_width = block_size * 30
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

i_index = 1
j_index = 2
l_index = 3
o_index = 4
s_index = 5
t_index = 6
z_index = 7

# each mino's layout, 4(rotation) x 4 x 2(blocks occupying [x, y], 
# where x and y value are offset values from upper left corner position)
I_layout = [[[1,2], [2,2], [3,2], [4,2]],
            [[2,1], [2,2], [2,3], [2,4]],
            [[0,2], [1,2], [2,2], [3,2]],
            [[2,0], [2,1], [2,2], [2,3]]]
J_layout = [[[0,0], [0,1], [1,1], [2,1]],
            [[1,0], [2,0], [1,1], [1,2]],
            [[0,1], [1,1], [2,1], [2,2]],
            [[1,0], [1,1], [0,2], [1,2]]]
L_layout = [[[2,0], [0,1], [1,1], [2,1]],
            [[1,0], [1,1], [1,2], [2,2]],
            [[0,1], [1,1], [2,1], [0,2]],
            [[0,0], [1,0], [1,1], [1,2]]]
O_layout = [[[1,0], [2,0], [1,1], [2,1]],
            [[1,1], [2,1], [1,2], [2,2]],
            [[0,1], [1,1], [0,2], [1,2]],
            [[0,0], [1,0], [0,1], [1,1]]]
S_layout = [[[1,0], [2,0], [0,1], [1,1]],
            [[1,0], [1,1], [2,1], [2,2]],
            [[1,1], [2,1], [0,2], [1,2]],
            [[0,0], [0,1], [1,1], [1,2]]]
T_layout = [[[1,0], [0,1], [1,1], [2,1]],
            [[1,0], [1,1], [2,1], [1,2]],
            [[1,1], [2,1], [0,1], [1,2]],
            [[1,0], [0,1], [1,1], [1,2]]]
Z_layout = [[[1,0], [0,0], [1,1], [2,1]],
            [[2,0], [1,1], [2,1], [1,2]],
            [[1,1], [2,2], [0,1], [1,2]],
            [[1,0], [0,1], [1,1], [0,2]]]


# each mino's SRS information. For details, check https://tetris.wiki/Super_Rotation_System
i_srs = [[[0,0],[-1,0],[2,0],[-1,0],[2,0]],
         [[-1,0],[0,0],[0,0],[0,1],[0,-2]],
         [[-1,1],[1,1],[-2,1],[1,0],[-2,0]],
         [[0,1],[0,1],[0,1],[0,-1],[0,2]]] # 4 x 5 x 2
jlstz_srs = [[[0,0],[0,0],[0,0],[0,0],[0,0]],
            [[0,0],[1,0],[1,-1],[0,2],[1,2]],
            [[0,0],[0,0],[0,0],[0,0],[0,0]],
            [[0,0],[-1,0],[-1,-1],[0,2],[-1,2]]] # 4 x 5 x 2
o_srs = [[[0,0]],
         [[0,-1]],
         [[-1,-1]],
         [[-1,0]]] # 4 x 1 x 2

# spawn location
i_spawn = [3, 0] #(x, y)
jlostz_spawn = [4, 1]

COLORS = [COLOR_BG, COLOR_I, COLOR_J, COLOR_L, COLOR_O, COLOR_S, COLOR_T, COLOR_Z]

class tetrimino:
    # block_data is 4 x 4 x 2 list, each of 4 lists representing different rotation states
    # srs_data is 4 x 5 x 2 list needed to implement super rotation system (for detail, go to https://tetris.wiki/Super_Rotation_System)
    # current_rot {0: initial state, 1: 90 degree clockwise, 2: 180 clockwise(counterclockwise), 3: 90 degree counterclockwise}
    # spawn_pos is [x, y] position where the block initially appears
    def __init__(self, mino_id: int, block_data: list_3d, srs_data: list_3d, spawn_pos: list_2d):
        self.mino_id = mino_id
        self.block_data = block_data
        self.srs_data = srs_data
        self.spawn_pos = spawn_pos
        self.current_rot = 0 
        self.current_pos = [spawn_pos[0], spawn_pos[1]]
    # Based on its current [x, y], current_rot, calculate the final position if it would be rotated, where angle is specified angle_offset
    # angle_offset = 1 or -1
    # return a list of [x, y]
    def srs_xy(self, angle_offset) -> list_2d: 
        final_angle = (self.current_rot + angle_offset) % 4
        current_srs = self.srs_data[self.current_rot]
        final_srs = self.srs_data[final_angle]
        result = []
        for i in range(len(current_srs)): # i = 1 (o_mino) i = 5 (other minos)
            x = current_srs[i][0] - final_srs[i][0]
            y = current_srs[i][1] - final_srs[i][1]
            result.append([x,y])
        return result
    # initiate mino's mutable information
    def init_mino(self):
        self.current_rot = 0
        self.current_pos = [self.spawn_pos[0], self.spawn_pos[1]]
    # Based on its current [x, y] and current_rot, calculate the space where mino's blocks occupie 
    def current_space(self) -> list_2d:
        occupied_space = []
        mino_data = self.block_data[self.current_rot] # 4 x 2 list
        for each_block in mino_data:
            x_position = self.current_pos[0] + each_block[0]
            y_position = self.current_pos[1] + each_block[1]
            occupied_space.append([x_position, y_position])
        return occupied_space
        

class controller:
    I_mino = tetrimino(1, I_layout, i_srs, i_spawn)
    J_mino = tetrimino(2, J_layout, jlstz_srs, jlostz_spawn)
    L_mino = tetrimino(3, L_layout, jlstz_srs, jlostz_spawn)
    O_mino = tetrimino(4, O_layout, o_srs, jlostz_spawn)
    S_mino = tetrimino(5, S_layout, jlstz_srs, jlostz_spawn)
    T_mino = tetrimino(6, T_layout, jlstz_srs, jlostz_spawn)
    Z_mino = tetrimino(7, Z_layout, jlstz_srs, jlostz_spawn)

    minos = {
        1: I_mino,
        2: J_mino,
        3: L_mino,
        4: O_mino,
        5: S_mino, 
        6: T_mino,
        7: Z_mino
    }

    def __init__(self, screen):
        self.screen = screen
        self.field = [[0 for i in range(10)] for j in range(23)]
        self.dropping_mino = controller.minos[random.randint(1, 7)] 
        self.next_minos = [] # 1 ~ 7
        self.score = 0
        self.hold_mino_id = None # 1 ~ 7
        
    def init(self):
        self.next_minos_init()
    
    def next_round(self):
        self.dropping_mino.init_mino()
        self.dropping_mino = controller.minos[self.next_minos[0]]
        self.next_minos_update()
    
    # move dropping mino an offset specified by x, right(x>0) or left(x<0)
    def move_x(self, x): 
        x_position = self.dropping_mino.current_pos[0] + x
        y_position = self.dropping_mino.current_pos[1]
        if self.check_collision(self.dropping_mino.current_rot, [x_position, y_position]) == False: # won't collide
            self.dropping_mino.current_pos[0] += x

    # rotate dropping mino after calculating its final position 
    # calculation is done using Super Rotation System used in tetris world rule
    def rotate(self, angle_offset):
        srs_offset = self.dropping_mino.srs_xy(angle_offset)
        for xy_offset in srs_offset: # xy_offset is [x, y]
            x_position = self.dropping_mino.current_pos[0] + xy_offset[0]
            y_position = self.dropping_mino.current_pos[1] - xy_offset[1] # minus because y axis is downward
            rot = (self.dropping_mino.current_rot + angle_offset) % 4
            if self.check_collision(rot, [x_position, y_position]) == False:
                self.dropping_mino.current_rot = rot
                self.dropping_mino.current_pos = [x_position, y_position]
                break

    # check if the dropping mino would collide to either of wall, floor, or stacks, when it is located xy with angle of rot
    # xy is absolute position, and each x and y value can have negative values when the dropping mino is near the left wall 
    # rot is absolute angle:
    #        {0: initial state, 1: 90 degree clockwise, 2: 180 clockwise(counterclockwise), 3: 90 degree counterclockwise}
    def check_collision(self, rot, xy) -> bool:
        # get a list of [x, y], representing the location where blocks occupy
        # Note here we could not use dropping_mino.current_space(), 
        # because it calculates the space occupied based on current location and rotation angle.
        occupied_space = []
        mino_data = self.dropping_mino.block_data[rot] # 4 x 2 list
        for each_block in mino_data:
            x_position = xy[0] + each_block[0]
            y_position = xy[1] + each_block[1]
            occupied_space.append([x_position, y_position])

        for each_block in occupied_space:
            # wall and floor check
            if each_block[0] < 0 or each_block[0] > 9 or each_block[1] > 22:
                return True
            # stack check
            if self.field[each_block[1]][each_block[0]] > 0:
                return True
        return False

    # return 0 if it drops , returns 1 if it lands
    def soft_drop(self):
        x_position = self.dropping_mino.current_pos[0]
        y_position = self.dropping_mino.current_pos[1] + 1
        if self.check_collision(self.dropping_mino.current_rot, [x_position, y_position]) == False: # won't collide
            self.dropping_mino.current_pos[1] += 1
            return 0
        else:
            self.land()
            return 1
    def hard_drop(self):
        x_position = self.dropping_mino.current_pos[0]
        y_position = self.dropping_mino.current_pos[1] + 1
        while self.check_collision(self.dropping_mino.current_rot, [x_position, y_position]) == False:
            y_position += 1
        self.dropping_mino.current_pos[1] = y_position - 1
        self.land()

    # update field
    def land(self):
        space = self.dropping_mino.current_space()
        mino_color = self.dropping_mino.mino_id
        for xy in space:
            self.field[xy[1]][xy[0]] = mino_color

    # update View based on Model (MVC)
    def update_view(self):
        update_screen(self.screen, self.field, self.dropping_mino, self.next_minos, self.score, self.hold_mino_id)

    # 7 out of 10 minos in next_minos should be different types
    def next_minos_init(self):
        self.next_minos = random.sample([1,2,3,4,5,6,7,8,9,10], 10)
        for i in range(len(self.next_minos)):
            if self.next_minos[i] > 7:
                self.next_minos[i] = random.randint(1,7)
                
    # maintain the rule of 7 out of 10
    def next_minos_update(self):
        popped_mino = self.next_minos.pop(0)
        flag = 0
        for i in range(len(self.next_minos)):
            if self.next_minos[i] == popped_mino:
                self.next_minos.append(random.randint(1,7))
                flag = 1
        if flag == 0:
            self.next_minos.append(popped_mino)



# View functions here
def draw_hold(screen):
    # show string "HOLD"
    font = pg.font.Font(None, block_size)
    txt = font.render("HOLD", True, WHITE)
    screen.blit(txt, [hold_text_x, hold_text_y])
    # show the square blank for held mino
    pg.draw.rect(screen, COLOR_BG, [hold_x, hold_y, hold_width, hold_length])

def draw_score(screen):
    # show string "SCORE"
    font = pg.font.Font(None, block_size)
    txt = font.render("SCORE", True, WHITE)
    screen.blit(txt, [score_text_x, score_text_y])
    # show the square blank for held mino
    pg.draw.rect(screen, COLOR_BG, [score_x, score_y, score_width, score_length])

# show field based on its contents
# draw dropping tetriminos as well
def draw_field(screen):
    pg.draw.rect(screen, COLOR_BG, [field_x, field_y, field_width, field_length])

def draw_nexts(screen):
    # show string "NEXT"
    font = pg.font.Font(None, block_size)
    txt = font.render("NEXT", True, WHITE)
    screen.blit(txt, [nexts_text_x, nexts_text_y])
    for i in range(5):
        pg.draw.rect(screen, COLOR_BG, [nexts_x[i], nexts_y[i], nexts_width, nexts_length])

def screen_init(screen):
    screen.fill(BLACK)
    draw_hold(screen)
    draw_score(screen)
    draw_field(screen)
    draw_nexts(screen)

# Note that this doesn't update screen if there is nothing in hold
def update_hold(screen, hold_mino_id):
    if hold_mino_id != None:
        # delete current drawing first
        pg.draw.rect(screen, COLOR_BG, [hold_x, hold_y, hold_width, hold_length])
        draw_mino(screen, hold_mino_id, hold_x, hold_y, hold_block_size, 0)


def update_score(screen, score):
    font = pg.font.Font(None, block_size)
    txt = font.render(str(score), True, WHITE)
    screen.blit(txt, [score_x, score_y])

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
    mino_layout = controller.minos[mino_id].block_data[rot] # 4 x 2
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
        

def update_screen(screen, field, dropping_mino, next_minos, score, hold_mino_id):
    update_hold(screen, hold_mino_id)
    update_score(screen, score)
    update_field(screen, field)
    update_nexts(screen, next_minos)
    update_drop(screen, dropping_mino)

        
def main():
    pg.init()
    pg.display.set_caption("tetris")
    screen = pg.display.set_mode((screen_width, screen_length))
    # show basic screen
    screen_init(screen)


    # initiate controller
    ctl = controller(screen)
    ctl.init()

    clock = pg.time.Clock()

    tmr = 0
    hard_drop_sensitive = 0

    while True:
        tmr = tmr + 1
        if tmr > 10:
            hard_drop_sensitive = 0
            tmr = 0
            land = ctl.soft_drop()
            if land == 1:
                ctl.next_round()

                ctl.update_view()
                pg.display.update()
                clock.tick(10)

                continue
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
            tmr += 3 
        if key[pg.K_w] == 1: # hard drop
            if hard_drop_sensitive == 0:
                ctl.hard_drop()
                ctl.next_round()
                tmr = 0
                hard_drop_sensitive = 1
            else:
                hard_drop_sensitive = 0
        if key[pg.K_RIGHT] == 1: # rotate clockwise
            ctl.rotate(1)
        if key[pg.K_LEFT] == 1: # rotate counterclockwise
            ctl.rotate(-1)


        # update view
        ctl.update_view()
        pg.display.update()

        clock.tick(10)

if __name__ == '__main__':
    main()
