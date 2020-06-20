from typing import List
list_3d = List[List[List[int]]]
import sys
import random
import time
import numpy as np
import asyncio
from collections import namedtuple
import copy

import pygame as pg
from tetris_layout import screen_width, screen_length
from tetris_view import main_menu
from tetris_single import single_play
from tetris_online import online_play

"""
tetris implemented using pygame
employed MVC model, where Controller stands as a class, which contains Model, and View is provided as a bunch of functions

"""

def main():
    pg.init()
    pg.display.set_caption("tetris")
    screen = pg.display.set_mode((screen_width, screen_length))

    while True:
        select = main_menu(screen)
        if select == 0:
            single_play(screen)
        elif select == 1:
            asyncio.run(online_play(screen))
        elif select == 2:
            pass
        time.sleep(1)



if __name__ == '__main__':
    main()

