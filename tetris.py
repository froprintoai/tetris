from typing import List
import pygame as pg
import sys
import random
import time
import numpy as np

"""
tetris implemented using pygame
employed MVC model, where Controller stands as a class, which contains Model, and View is provided as a bunch of functions

"""

# data for single play
num_rows = 23
num_columns = 10

list_2d = List[List[int]]
list_3d = List[List[List[int]]]

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

# data for main menu
# title should be the center of the screen
title_name = 'Tetris'
title_size = [800, 300]
title_from_top = 100
title_center = [screen_width / 2, title_from_top + title_size[1] / 2]
title_x = title_center[0] - title_size[0] / 2
title_y = title_from_top

options_margin = 80 # margin between options
# single play option layout data
sp_size = [700, 160]
sp_center = [
             screen_width / 2,
             title_y + title_size[1] + options_margin + sp_size[1] / 2
            ]
sp_x = sp_center[0] - sp_size[0] / 2
sp_y = sp_center[1] - sp_size[1] / 2
sp_color = (38, 17, 115)

pause_option_x = 50
pause_option_y = 50
pause_option_size = [300, 50]

pause_size = [800, 400]
pause_center = [screen_width / 2, screen_length /2]
pause_x = pause_center[0] - pause_size[0] / 2
pause_y = pause_center[1] - pause_size[1] / 2
pause_color = (0, 0, 150)

pause_resume_from_top = 30
pause_resume_size = [600, 150]
pause_resume_center = [pause_center[0], pause_y + pause_resume_from_top + pause_resume_size[1] / 2]
pause_resume_x = pause_resume_center[0] - pause_resume_size[0] / 2
pause_resume_y = pause_y + pause_resume_from_top

pause_to_menu_from_bottom = 30
pause_to_menu_size = [600, 150]
pause_to_menu_center = [pause_center[0], pause_y + pause_size[1] - pause_to_menu_from_bottom - pause_to_menu_size[1] / 2]
pause_to_menu_x = pause_to_menu_center[0] - pause_to_menu_size[0] / 2
pause_to_menu_y = pause_to_menu_center[1] - pause_to_menu_size[1] / 2

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

    def __init__(self, v):
        self.view = v
        self.field = [[0 for i in range(10)] for j in range(23)]
        self.dropping_mino = controller.minos[random.randint(1, 7)] 
        self.next_minos = [] # 1 ~ 7
        self.score = 0
        self.hold_mino_id = None # 1 ~ 7
        self.score_text = ""
        self.last_move_is_rotate = False
        self.highlight = []
        
    def init(self):
        self.next_minos_init()
    
    def next_round(self) -> bool:
        self.dropping_mino.init_mino()
        self.dropping_mino = controller.minos[self.next_minos[0]]
        self.next_minos_update()
        self.last_move_is_rotate = False
        self.update_highlight()
        return self.is_gameover()
    
    def is_gameover(self) -> bool:
        space = self.dropping_mino.current_space()
        for xy in space:
            if self.field[xy[1]][xy[0]] > 0:
                return True
        return False
    
    # move dropping mino an offset specified by x, right(x>0) or left(x<0)
    def move_x(self, x): 
        x_position = self.dropping_mino.current_pos[0] + x
        y_position = self.dropping_mino.current_pos[1]
        if self.check_collision(self.dropping_mino.current_rot, [x_position, y_position]) == False: # won't collide
            self.dropping_mino.current_pos[0] += x
            self.last_move_is_rotate = False
        self.update_highlight()

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
                self.last_move_is_rotate = True
                break
        self.update_highlight()

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
            self.last_move_is_rotate = False
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
        #line deletion 
        y_list = []
        for xy in space:
            y_list.append(xy[1])
        y_list = list(dict.fromkeys(y_list)) #remove duplication
        y_list = [y for y in y_list if np.prod(self.field[y]) != 0]


        lines_deleted = len(y_list)
        if lines_deleted > 0: # if deletion required
            # deletion animation
            self.view.draw_deleted_lines(y_list)
            pg.display.update()
            time.sleep(0.5)

            #scoring
            t_spin_check = self.t_spin_checker()
            if t_spin_check == 0:
                self.score_not_t_spin(lines_deleted)
            elif t_spin_check == 1:
                self.score_t_spin_mini(lines_deleted)
            elif t_spin_check == 2:
                self.score_t_spin(lines_deleted)

            self.delete_lines(y_list)

                
    # 0 --> no t spin 1--> t spin mini 2 --> t spin
    def t_spin_checker(self) -> int:
        if self.dropping_mino.mino_id != t_index:
            return 0
        elif self.last_move_is_rotate != True:
            return 0
        else:
            diago_squares = []
            x = self.dropping_mino.current_pos[0]
            y = self.dropping_mino.current_pos[1]
            for i in [0, 2]:
                for j in [0, 2]:
                    diago_squares.append([x + i, y + j])
            filled_counter = 0
            wall_floor_counter = 0
            for xy in diago_squares:
                # wall and floor check
                if xy[0] < 0 or xy[0] > 9 or xy[1] > 22:
                    wall_floor_counter += 1
                # stack check
                elif self.field[xy[1]][xy[0]] > 0:
                    filled_counter += 1
            if filled_counter > 2:
                return 2
            elif wall_floor_counter + filled_counter > 2:
                return 1
            else:
                return 0

    # deleting field lines specified by y_list
    def delete_lines(self, y_list):
        temp_field = []
        for i in range(len(self.field)): # 0 ~ 22
            if i not in y_list:
                temp_field.append(self.field[i])
        zeros_inserted = len(self.field) - len(temp_field) # number of zero rows inserted
        for i in range(zeros_inserted):
            temp_field.insert(0, [0 for i in range(num_columns)])
        self.field = temp_field
    
    def score_not_t_spin(self, num_lines):
        if num_lines < 4:
            gain = num_lines * 200 - 100
            self.score += gain
            self.score_text = "+" + str(gain)
        else:
            gain = 800
            self.score += gain
            self.score_text = "Tetris! +800"

    def score_t_spin(self, num_lines):
        if num_lines == 1:
            self.score += 800
            self.score_text = "T-Spin Single"
        if num_lines == 2:
            self.score += 1200
            self.score_text = "T-Spin Double"
        if num_lines == 3:
            self.score += 1600
            self.score_text = "T-Spin Triple"

        
    def score_t_spin_mini(self, num_lines):
        if num_lines == 1:
            self.score += 200
            self.score_text = "T-Spin mini single"
        elif num_lines == 2:
            self.score += 400
            self.score_text = "T-Spin mini double"

    # update View based on Model (MVC)
    def update_view(self):
        self.view.update_screen(self.field, self.dropping_mino, self.next_minos, self.score, self.score_text, self.hold_mino_id, self.highlight)

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
                break
        if flag == 0:
            self.next_minos.append(popped_mino)
    
    # exchange or hold
    def hold(self):
        if self.hold_mino_id == None:
            self.hold_mino_id = self.dropping_mino.mino_id
            self.next_round()
        else:
            self.dropping_mino.init_mino()
            temp_next_mino_id = self.hold_mino_id
            self.hold_mino_id = self.dropping_mino.mino_id
            self.dropping_mino = controller.minos[temp_next_mino_id]
        self.update_highlight()
    
    def update_highlight(self):
        self.highlight = []
        x_position = self.dropping_mino.current_pos[0]
        y_position = self.dropping_mino.current_pos[1] + 1
        while self.check_collision(self.dropping_mino.current_rot, [x_position, y_position]) == False:
            y_position += 1
        y_position -= 1
        current_rot = self.dropping_mino.current_rot
        block_offset = self.dropping_mino.block_data[current_rot]
        for xy in block_offset:
            self.highlight.append([xy[0] + x_position, xy[1] + y_position])


class view():
    def __init__(self, screen):
        self.screen = screen

    # View functions here
    def draw_hold(self):
        # show string "HOLD"
        font = pg.font.Font(None, block_size)
        txt = font.render("HOLD", True, WHITE)
        self.screen.blit(txt, [hold_text_x, hold_text_y])
        # show the square blank for held mino
        pg.draw.rect(self.screen, COLOR_BG, [hold_x, hold_y, hold_width, hold_length])

    def draw_score(self):
        # show string "SCORE"
        font = pg.font.Font(None, block_size)
        txt = font.render("SCORE", True, WHITE)
        self.screen.blit(txt, [score_text_x, score_text_y])
        # show the square blank for held mino
        pg.draw.rect(self.screen, COLOR_BG, [score_x, score_y, score_width, score_length])

    # show field based on its contents
    # draw dropping tetriminos as well
    def draw_field(self):
        pg.draw.rect(self.screen, BLACK, [field_x, field_y, field_width, field_length], 5)
        pg.draw.rect(self.screen, COLOR_BG, [field_x, field_y, field_width, field_length])

    def draw_nexts(self):
        # show string "NEXT"
        font = pg.font.Font(None, block_size)
        txt = font.render("NEXT", True, WHITE)
        self.screen.blit(txt, [nexts_text_x, nexts_text_y])
        for i in range(5):
            pg.draw.rect(self.screen, COLOR_BG, [nexts_x[i], nexts_y[i], nexts_width, nexts_length])

    def screen_init(self):
        self.screen.fill(BLACK)
        self.draw_hold()
        self.draw_score()
        self.draw_field()
        self.draw_nexts()

    # Note that this doesn't update screen if there is nothing in hold
    def update_hold(self, hold_mino_id):
        self.draw_hold()
        if hold_mino_id != None:
            # delete current drawing first
            self.draw_mino(hold_mino_id, hold_x, hold_y, hold_block_size, 0)


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

    def update_field(self, field):
        self.draw_field()
        for y in range(20):
            for x in range(10):
                if field[y + 3][x] > 0: # if there is a block
                    color = COLORS[field[y + 3][x]]
                    start_x = block_size * x + field_x
                    start_y = block_size * y + field_y
                    pg.draw.rect(self.screen, color, [start_x, start_y, block_size, block_size])
                    # enclose it with bg color line
                    pg.draw.rect(self.screen, COLOR_BG, [start_x, start_y, block_size, block_size], 1)

    def draw_mino(self, mino_id, draw_x, draw_y, b_size, rot):
        mino_layout = controller.minos[mino_id].block_data[rot] # 4 x 2
        for xy in mino_layout:
            d_x = draw_x + xy[0] * b_size
            d_y = draw_y + xy[1] * b_size
            pg.draw.rect(self.screen, COLORS[mino_id], [d_x, d_y, b_size, b_size])
            pg.draw.rect(self.screen, COLOR_BG, [d_x, d_y, b_size, b_size], 1)

    def update_nexts(self, next_minos):
        for i in range(5):
            draw_x = nexts_x[i]
            draw_y = nexts_y[i]
            pg.draw.rect(self.screen, COLOR_BG, [draw_x, draw_y, nexts_width, nexts_length])
            self.draw_mino(next_minos[i], draw_x, draw_y, nexts_block_size, 0)

    def update_drop(self, dropping_mino):
        if dropping_mino != None:
            d_x = dropping_mino.current_pos[0] * block_size + field_x
            d_y = dropping_mino.current_pos[1] * block_size + field_y - (23-20) * block_size
            self.draw_mino(dropping_mino.mino_id, d_x, d_y, block_size, dropping_mino.current_rot)
            pg.draw.rect(self.screen, BLACK, [field_x, 0, field_width, block_size])
            

    def update_screen(self, field, dropping_mino, next_minos, score, score_text, hold_mino_id, highlight):
        self.update_hold(hold_mino_id)
        self.update_score(score, score_text)
        self.update_field(field)
        self.update_nexts(next_minos)
        self.update_drop(dropping_mino)
        self.draw_highlight(highlight)
        self.draw_back_menu()
        

    def draw_deleted_lines(self, y_list):
        for y in y_list:
            self.draw_deleted_line(y)

    def draw_deleted_line(self, y):
        d_y = field_y + (y - 3) * block_size
        pg.draw.rect(self.screen, COLOR_BG, [field_x, d_y, field_width, block_size])


    def draw_highlight(self, highlight):
        for xy in highlight:
            d_x = field_x + xy[0] * block_size
            d_y = xy[1] * block_size + field_y - (23-20) * block_size
            pg.draw.rect(self.screen, WHITE, [d_x, d_y, block_size, block_size], 5)
    
    def draw_back_menu(self):
        pg.draw.rect(self.screen, sp_color, [pause_option_x, pause_option_y, pause_option_size[0], pause_option_size[1]])
        font = pg.font.Font(None, pause_option_size[1])
        txt = font.render("P: pause", True, WHITE)
        rect = txt.get_rect()
        rect.center = (200, 75)
        self.screen.blit(txt, rect)


# return 0 if single play
def main_menu(screen):
    screen.fill(BLACK)
    # show title text
    show_option(screen, title_size, BLACK, title_name, WHITE, title_x, title_y, title_center)

    # show single play text
    show_option(screen, sp_size, sp_color, "single play", WHITE, sp_x, sp_y, sp_center)
    pg.display.update()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
        mouse_x, mouse_y = pg.mouse.get_pos()
        left_clicked, _, _ = pg.mouse.get_pressed()
        if left_clicked == 1:
            if mouse_x > sp_x and mouse_x < sp_x + sp_size[0] \
                and mouse_y > sp_y and mouse_y < sp_y + sp_size[1]:
                return 0

#return True for resume, False for back to main menu
def pause(screen):
    pg.draw.rect(screen, pause_color, [pause_x, pause_y, pause_size[0], pause_size[1]])
    show_option(screen, pause_resume_size, pause_color, "resume", WHITE, pause_resume_x, pause_resume_y, pause_resume_center)
    show_option(screen, pause_to_menu_size, pause_color, "main menu", WHITE, pause_to_menu_x, pause_to_menu_y, pause_to_menu_center)
    pg.display.update()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
        mouse_x, mouse_y = pg.mouse.get_pos()
        left_clicked, _, _ = pg.mouse.get_pressed()
        if left_clicked == 1:
            if mouse_x > pause_resume_x and mouse_x < pause_resume_x + pause_resume_size[0] \
                and mouse_y > pause_resume_y and mouse_y < pause_resume_y + pause_resume_size[1]:
                return True
            if mouse_x > pause_to_menu_x and mouse_x < pause_to_menu_x + pause_to_menu_size[0] \
                and mouse_y > pause_to_menu_y and mouse_y < pause_to_menu_y + pause_to_menu_size[1]:
                return False

def show_option(screen, bg_size, bg_color, txt, txt_color, x, y, center):
    pg.draw.rect(screen, bg_color, [x, y, bg_size[0], bg_size[1]])
    font = pg.font.Font(None, bg_size[1])
    txt = font.render(txt, True, txt_color)
    rect = txt.get_rect()
    rect.center = (center[0], center[1])
    screen.blit(txt, rect)

def single_play(screen):
    
    # show basic screen
    v = view(screen)
    v.screen_init()


    # initiate controller
    ctl = controller(v)
    ctl.init()

    clock = pg.time.Clock()

    tmr = 0
    hard_drop_sensitive = 0
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
            tmr += 8 
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
        if tmr > 10:
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

        # update view
        ctl.update_view()
        pg.display.update()

        clock.tick(10)
        
def main():
    pg.init()
    pg.display.set_caption("tetris")
    screen = pg.display.set_mode((screen_width, screen_length))

    while True:
        select = main_menu(screen)
        if select == 0:
            single_play(screen)
        elif select == 1:
            pass
        elif select == 2:
            pass



if __name__ == '__main__':
    main()
