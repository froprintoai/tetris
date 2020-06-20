from typing import List
list_3d = List[List[List[int]]]
list_2d = List[List[int]]

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