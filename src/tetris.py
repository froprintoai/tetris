import time
import asyncio

import pygame as pg

from tetris_view import main_menu
from tetris_single import single_play
from tetris_online import online_play
from tetris_layout import screen_width, screen_length
from tetris_cpu import challenge_ai

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
            challenge_ai(screen)
        time.sleep(1)



if __name__ == '__main__':
    main()

