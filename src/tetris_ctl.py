from tetris_mino import tetrimino
from tetris_utils import fire
from network_config import *
from tetris_data import *

import pygame as pg
import random
import torch
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

    # last_deleted is whether any line was deleted at last round
    # btb_ready is wheter last deletion was either t-spin or tetris
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
        self.ren = 0
        self.last_deleted = False
        self.btb_ready = False
        self.hold_used = False

        self.next_minos_init()
    
    def next_round(self) -> bool:
        self.dropping_mino.init_mino()
        self.dropping_mino = controller.minos[self.next_minos[0]]
        self.next_minos_update()
        self.last_move_is_rotate = False
        self.hold_used = False
        self.update_highlight()
        return self.is_gameover()
    
    def is_gameover(self) -> bool:
        space = self.dropping_mino.current_space()
        for xy in space:
            if self.field[xy[1]][xy[0]] > 0:
                return True
        return False
    
    def check_gameover(self):
        if sum(self.field[1]) > 0:
            return True
        else:
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

    # return send, basis, btb, ren, all_deletion info
    def land(self):
        # update field
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
        if lines_deleted == 0:
            self.last_deleted = False
            self.ren = 0
            return False, 0, 0, 0, 0
            
        else: # deletion required
            if self.last_deleted:
                self.ren += 1
            self.last_deleted = True

            # deletion animation
            self.view.draw_deleted_lines(y_list)
            pg.display.update()
            time.sleep(0.5)

            # determine basis
            #scoring
            basis = 0
            t_spin_check = self.t_spin_checker()
            if t_spin_check == 0:
                self.score_not_t_spin(lines_deleted)
                if lines_deleted == 2 or lines_deleted == 3:
                    basis = lines_deleted - 1
                if lines_deleted == 4:
                    basis = 4
            elif t_spin_check == 1:
                self.score_t_spin_mini(lines_deleted)
            elif t_spin_check == 2:
                self.score_t_spin(lines_deleted)
                basis = lines_deleted * 2
            
            btb = 0
            if t_spin_check > 1 or lines_deleted == 4: #tetris or t-spin (/mini)
                if self.btb_ready:
                    btb = 1
                self.btb_ready = True
            else:
                self.btb_ready = False

            self.delete_lines(y_list)
            all_deleted = 0
            # the bottom line filled with 0 means all deletion occured
            if self.field[22] == [0 for i in range(10)]:
                all_deleted = 4
            
            return True, basis, btb, self.ren, all_deleted


                
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
        self.view.update_screen(self.field, self.dropping_mino, 
            self.next_minos, self.score, self.score_text, self.hold_mino_id, self.highlight)

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
        if self.hold_used:
            pass
        else:
            if self.hold_mino_id == None:
                self.hold_mino_id = self.dropping_mino.mino_id
                self.next_round()
            else:
                self.last_move_is_rotate = False
                self.dropping_mino.init_mino()
                temp_next_mino_id = self.hold_mino_id
                self.hold_mino_id = self.dropping_mino.mino_id
                self.dropping_mino = controller.minos[temp_next_mino_id]
            self.hold_used = True
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
    def __init__(self, online_ctl):
        self.data_received = None
        self.ctl = online_ctl

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        #message = data.decode()
        #print('Received %r from %s' % (message, addr))
        if data != None:
            if data[:2] == ('XY').encode():
                self.ctl.update_op_layout(data[2:])
            elif data[:2] == ('FI').encode(): # fire check
                print("receiving fire")
                self.ctl.incoming_fire.add(data[2])
            else:
                print("get something")
                print(data)
    def connection_lost(self, exc):
        pass

class online_controller(controller):
    def __init__(self, view, ri, rs, e):
        super(online_controller, self).__init__(view)
        self.opponent_layout = [[0 for i in range(10)] for j in range(20)]
        self.incoming_fire = fire()
        self.sending_fire = 0
        self.room_index = ri
        self.room_side = rs
        self.event = e

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

    async def receive_layout(self, event, update_rate=0.01):
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: ServerProtocol(self),
            local_addr=(client_ip, client_udp_port),
        )
        await event.wait()
        transport.close()
        print("recieve_layout end")

    async def send_fire(self, terminator, lock):
        await lock.acquire()
        while terminator.is_set() != True:
            lock.release()
            # event is set by land() only when necessary
            await self.event.wait()

            print("sending fire")
            loop = asyncio.get_running_loop()
            on_con_lost = loop.create_future()
            fire = self.get_fire()
            transport, protocol = await loop.create_datagram_endpoint(
                lambda: ClientProtocol(fire, on_con_lost),
                remote_addr=(server_ip, server_udp_port))

            try:
                await on_con_lost
            finally:
                transport.close()
                self.sending_fire = 0
                self.event.clear()
                await lock.acquire()
        lock.release()
        print("send_fire end")
        
    # used by send_fire
    def get_fire(self):
        suffix = ('EF').encode() + (self.room_index).to_bytes(1, "big") \
            + (self.room_side).to_bytes(1, "big") + self.sending_fire.to_bytes(1, "big")
        return suffix
    


    def update_op_layout(self, bytes_layout):
        for i, bytes_line in enumerate(self.line_generator(bytes_layout)):
            #self.opponent_layout[i] = [int.from_bytes(b, "big") for b in bytes_line]
            length = len(bytes_line)
            if length == 10:
                self.opponent_layout[i] = [b for b in bytes_line]
            elif length < 10:
                self.opponent_layout[i] = [bytes_line[i] if i < length else 0 for i in range(10)]

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
                                 self.hold_mino_id, self.highlight, self.opponent_layout, len(self.incoming_fire))
    def land(self):
        send, basis, btb, ren, all_deleted = super(online_controller, self).land()
        if send:
            sending_lines = basis + btb + ren_bonus[ren] + all_deleted
            remainder = self.incoming_fire.subtract(sending_lines)
            if remainder > 0:
                self.sending_fire += remainder
                self.event.set()

        num_fire = self.incoming_fire.countdown()
        
        # fire insertion to field
        if num_fire > 0:
            empty_index = random.randint(0, 9)
            added_stacks = [[8 if i != empty_index else 0 for i in range(10)] for i in range(num_fire)]
            self.field.extend(added_stacks)
            self.field = self.field[num_fire:]

class controller_cpu(controller):
    def __init__(self, view, l_conn, f_conn, g_conn, lock):
        super(controller_cpu, self).__init__(view)
        self.opponent_layout = [[0 for i in range(10)] for j in range(20)]
        self.incoming_fire = fire()

        self.layout_lock = lock
        self.layout_conn = l_conn
        self.fire_conn = f_conn
        self.gameover_conn = g_conn

    def update_view(self):
        self.view.update_screen(self.field, self.dropping_mino,
                                self.next_minos, self.score, self.score_text,
                                 self.hold_mino_id, self.highlight, self.opponent_layout, len(self.incoming_fire))
    
    def land(self):
        send, basis, btb, ren, all_deleted = super(controller_cpu, self).land()
        if send:
            sending_lines = basis + btb + ren_bonus[ren] + all_deleted
            remainder = self.incoming_fire.subtract(sending_lines)
            if remainder > 0:
                self.fire_conn.send(remainder)
        
        # fire insertion to field
        num_fire = self.incoming_fire.countdown()
        if num_fire > 0:
            empty_index = random.randint(0, 9)
            added_stacks = [[8 if i != empty_index else 0 for i in range(10)] for i in range(num_fire)]
            self.field.extend(added_stacks)
            self.field = self.field[num_fire:]
    
    def recv_fire(self):
        while self.fire_conn.poll():
            self.incoming_fire.add(self.fire_conn.recv())

    # get the first layout from the layout pipe and delete the rest
    def recv_layout(self):
        self.layout_lock.acquire()
        try:
            if self.layout_conn.poll():
                self.opponent_layout = self.layout_conn.recv()
                # empty the pipe
                while self.layout_conn.poll():
                    self.layout_conn.recv()
        finally:
            self.layout_lock.release()
    
    def recv_gameover(self):
        if self.gameover_conn.poll():
            self.gameover_conn.recv()
            return True
        else:
            return False
    

class agent_ctl():
    def __init__(self, env, net, f_conn):
        self.env = env
        self.net = net
        self.state = self.env.reset()
        self.f_conn = f_conn
        self.incoming_fire = fire()

    
    def step(self):
        state_a = np.array([self.state], copy=False)
        print(state_a)
        state_v = torch.tensor(state_a)
        q_vals_v = self.net(state_v)
        print(q_vals_v)
        _, act_v = torch.max(q_vals_v, dim=1)
        action = int(act_v.item())

        print("action : " + str(action))
        self.state, _, is_done, info_list = self.env.step(action)

        landed = info_list[0]
        sending_fire = info_list[1]


        if landed:
            if sending_fire > 0:
                remainder = self.incoming_fire.subtract(sending_fire)
                if remainder > 0:
                    self.fire_conn.send(remainder)
            # fire insertion to field
            num_fire = self.incoming_fire.countdown()
            if num_fire > 0:
                self.env.add_fire(num_fire)
            
        return is_done


    def get_layout(self):
        temp = np.squeeze(self.state[:, 9: ,:], axis=0)
        temp = temp.astype(int)
        return temp.tolist()
    
    def recv_fire(self):
        while self.f_conn.poll():
            self.incoming_fire.add(self.f_conn.recv())


