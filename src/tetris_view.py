from tetris_layout import *
from tetris_ctl import controller
import pygame as pg
import sys

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

class online_view(view):
    def __init__(self, screen):
        super(online_view, self).__init__(screen)
    
    def screen_init(self):
        super(online_view, self).screen_init()
        self.draw_op_field()
        self.draw_fire()
    
    def draw_op_field(self):
        pg.draw.rect(self.screen, BLACK, [op_field_x, op_field_y, op_field_width, op_field_length], 5)
        pg.draw.rect(self.screen, COLOR_BG, [op_field_x, op_field_y, op_field_width, op_field_length])
    
    def draw_fire(self):
        pg.draw.rect(self.screen, BLACK, [fire_x, fire_y, fire_width, fire_length], 5)
        pg.draw.rect(self.screen, COLOR_BG, [fire_x, fire_y, fire_width, fire_length])
        
    def update_screen(self, field, dropping_mino, next_minos, score,
                score_text, hold_mino_id, highlight, op_layout, num_fire):
        super(online_view, self).update_screen(field, dropping_mino, next_minos, score, score_text, hold_mino_id, highlight)
        self.update_op_field(op_layout)
        self.update_fire(num_fire)
        
    def update_op_field(self, op_layout):
        self.draw_op_field()
        for y in range(20):
            for x in range(10):
                if op_layout[y][x] > 0: # if there is a block
                    color = COLORS[op_layout[y][x]]
                    start_x = block_size * x + op_field_x
                    start_y = block_size * y + op_field_y
                    pg.draw.rect(self.screen, color, [start_x, start_y, block_size, block_size])
                    # enclose it with bg color line
                    pg.draw.rect(self.screen, COLOR_BG, [start_x, start_y, block_size, block_size], 1)
    
    def update_fire(self, num_fire):
        self.draw_fire()
        bottom_x = fire_x
        bottom_y = fire_y + fire_length
        d_x = bottom_x
        d_y = bottom_y
        for i in range(num_fire):
            d_y -= block_size
            pg.draw.rect(self.screen, COLOR_F, [d_x, d_y, block_size, block_size])
            pg.draw.rect(self.screen, COLOR_BG, [d_x, d_y, block_size, block_size], 1)

# return 0 if single play
def main_menu(screen):
    screen.fill(BLACK)
    # show title text
    show_option(screen, title_size, BLACK, title_name, WHITE, title_x, title_y, title_center)

    # show single play text
    show_option(screen, sp_size, sp_color, "single play", WHITE, sp_x, sp_y, sp_center)

    # show online play text
    show_option(screen, op_size, op_color, "online play", WHITE, op_x, op_y, op_center)

    # show AI play text
    show_option(screen, ca_size, ca_color, "challenge AI", WHITE, ca_x, ca_y, ca_center)
    
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
            if mouse_x > op_x and mouse_x < op_x + op_size[0] \
                and mouse_y > op_y and mouse_y < op_y + op_size[1]:
                return 1
            if mouse_x > ca_x and mouse_x < ca_x + ca_size[0] \
                and mouse_y > ca_y and mouse_y < ca_y + ca_size[1]:
                print("here")
                return 2

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