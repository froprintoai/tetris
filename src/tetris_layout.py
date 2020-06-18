
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

op_field_x = nexts_x[0] + nexts_width + 80
op_field_y = field_y
op_field_width = field_width
op_field_length = field_length

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

#online play option layout data
op_size = [700, 160]
op_center = [
            screen_width / 2,
            sp_y + sp_size[1] + options_margin + op_size[1] / 2
           ]
op_x = op_center[0] - op_size[0] / 2
op_y = op_center[1] - op_size[1] / 2
op_color = (100, 0, 0)


# p: pause layout while playing
pause_option_x = 50
pause_option_y = 50
pause_option_size = [300, 50]

# pause layout
#   pause background
pause_size = [800, 400]
pause_center = [screen_width / 2, screen_length /2]
pause_x = pause_center[0] - pause_size[0] / 2
pause_y = pause_center[1] - pause_size[1] / 2
pause_color = (0, 0, 150)

#   pause resume button
pause_resume_from_top = 30
pause_resume_size = [600, 150]
pause_resume_center = [pause_center[0], pause_y + pause_resume_from_top + pause_resume_size[1] / 2]
pause_resume_x = pause_resume_center[0] - pause_resume_size[0] / 2
pause_resume_y = pause_y + pause_resume_from_top

#   pause back-to-menu button
pause_to_menu_from_bottom = 30
pause_to_menu_size = [600, 150]
pause_to_menu_center = [pause_center[0], pause_y + pause_size[1] - pause_to_menu_from_bottom - pause_to_menu_size[1] / 2]
pause_to_menu_x = pause_to_menu_center[0] - pause_to_menu_size[0] / 2
pause_to_menu_y = pause_to_menu_center[1] - pause_to_menu_size[1] / 2