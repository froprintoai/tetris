from tetris_mino import tetrimino
from tetris_utils import fire
from network_config import *
from tetris_data import *

import pygame as pg
import random
import numpy as np
import time
import copy
import asyncio

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
            temp_field.insert(0, [0 for i in range(10)])
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


class ClientProtocol:
    def __init__(self, message, on_con_lost):
        self.message = message
        self.on_con_lost = on_con_lost
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        self.transport.sendto(self.message)
        self.transport.close()

    def datagram_received(self, data, addr):
        pass

    def error_received(self, exc):
        print("error occured in ClientProtocol")

    def connection_lost(self, exc):
        self.on_con_lost.set_result(True)


class ServerProtocol:
    def __init__(self):
        self.data_received = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        #message = data.decode()
        #print('Received %r from %s' % (message, addr))
        self.data_received = data

class online_controller(controller):
    def __init__(self, view, ri, rs):
        super(online_controller, self).__init__(view)
        self.opponent_layout = [[0 for i in range(10)] for j in range(20)]
        self.incoming_fire = fire()
        self.ren = 0
        self.btb_ready = False
        self.room_index = ri
        self.room_side = rs

    async def send_layout(self):
        loop = asyncio.get_running_loop()
        on_con_lost = loop.create_future()
        layout = self.get_layout()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: ClientProtocol(layout, on_con_lost),
            local_addr=(client_ip, client_udp_port_sending),
            remote_addr=(server_ip, server_udp_port))

        try:
            await on_con_lost
        finally:
            transport.close()

    # C D index side info
    def get_layout(self):
        suffix = ('CD').encode() + (self.room_index).to_bytes(1, "big") + (self.room_side).to_bytes(1, "big")
        layout = self.create_layout()
        byte_field = [bytes(line) for line in layout[3:]] # ignore first three lines out of screen
        for byte_line in byte_field:
            suffix += bytes(byte_line)
        return suffix

    def create_layout(self):
        new_layout = copy.deepcopy(self.field)
        d_mino_space = self.dropping_mino.current_space()
        for x, y in d_mino_space:
            new_layout[y][x] = self.dropping_mino.mino_id
        return new_layout

    async def receive_layout(self, event, update_rate=0.1):
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: ServerProtocol(),
            local_addr=(client_ip, client_udp_port),
        )
        while event.is_set() != True:
            await asyncio.sleep(update_rate)
            if protocol.data_received != None:
                if protocol.data_received[:2] == ('XY').encode():
                    self.update_op_layout(protocol.data_received[2:])
                else: # fire check
                    pass
        transport.close()

    def update_op_layout(self, bytes_layout):
        print("update op layout")
        for i, bytes_line in enumerate(self.line_generator(bytes_layout)):
            #self.opponent_layout[i] = [int.from_bytes(b, "big") for b in bytes_line]
            length = len(bytes_line)
            if length == 10:
                self.opponent_layout[i] = [b for b in bytes_line]
            elif length < 10:
                self.opponent_layout[i] = [bytes_line[i] if i < length else 0 for i in range(10)]
        print(self.opponent_layout)

    # take bytesarray and generate its contents 10 bytes per once
    def line_generator(self, bytes_field):
        i = 0
        while True:
            yield bytes_field[i:i+10]
            i += 10 
            if i >= len(bytes_field):
                break

    # update View based on Model (MVC)
    def update_view(self):
        self.view.update_screen(self.field, self.dropping_mino,
                                self.next_minos, self.score, self.score_text,
                                 self.hold_mino_id, self.highlight, self.opponent_layout)
    