from tetris_layout import BLACK, WHITE
from network_config import *
from tetris_ctl import online_controller
from tetris_view import online_view

import pygame as pg
import asyncio
import sys

async def show_loading(screen):
    screen.fill(BLACK)
    font = pg.font.Font(None, 80)
    for i in range(1, 4):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
        i += 1
        txt = "Finding a player online" + ". " * i
        txt = font.render(txt, True, WHITE)
        screen.blit(txt, [10, 10])
        pg.display.update()
        await asyncio.sleep(1)

async def find_oponent():
    counter = 0
    while True:
        try:
            reader, writer = await asyncio.open_connection(
                server_ip, server_tcp_port)
        except ConnectionRefusedError:
            await asyncio.sleep(1)
            counter += 1
            if counter < 5:
                continue
            else:
                return
        except Exception:
            raise
        else:
            b_udp_port = client_udp_port.to_bytes(2, 'big')
            magic_num = ('AB').encode()
            writer.write(magic_num + b_udp_port)
            await writer.drain()

            data = await reader.read(100)
            writer.close()
            await writer.wait_closed()
            return data[0], data[1]

async def matching(screen):
    task_screen = asyncio.create_task(show_loading(screen))
    task_match = asyncio.create_task(find_oponent())

    room_index, room_side = await task_match
    await task_screen
    return room_index, room_side

async def game_start(ctl, screen, event):
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
        
        # give up the time to other coroutines
        await asyncio.sleep(0.1)

        # update view
        ctl.update_view()
        pg.display.update()


        clock.tick(10)
    event.set()

async def layout_sender(ctl, event):
    while event.is_set() != True:
        await asyncio.sleep(0.5)
        await ctl.send_layout()


async def online_play(screen):
    room_index, room_side = await matching(screen)
    if room_index == None:
        return
    elif room_index == 32:
        print("Server Error")
        return
    
    # show basic screen
    v = online_view(screen)
    v.screen_init()

    ctl = online_controller(v, room_index, room_side)
    ctl.init()

    # synchronized using event
    # game_start is the event setter
    event = asyncio.Event()
    udp_receive_task = asyncio.create_task(ctl.receive_layout(event))
    fire_send_task = asyncio.create_task(ctl.send_fire(event))
    await asyncio.gather(
        game_start(ctl, screen, event),
        layout_sender(ctl, event),
        udp_receive_task,
        fire_send_task
    )