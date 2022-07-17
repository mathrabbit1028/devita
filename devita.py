# import module
import pygame
import random
import pyautogui
import time
import math
import keyboard
import sys

pygame.init() # initialization

# screen setting
screen_width = pyautogui.size()[0] # width size - full screen
screen_height = pyautogui.size()[1] # height size - full screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Devita") # name of game

# variable setting
global rod_width_pro, rod_height_pro, circle_radius_pro, item_width_pro, item_height_pro
global item_size, danger_size_pro, score_size_pro, score_xcoord_pro, score_ycoord_pro
global item_delay, danger_delay, danger_time, item_summon_cycle

class item: # item properties
    def __init__(self, x_pos, y_pos, color, danger, summon_time, dif):
        self.x_pos = x_pos # x coordinate of item
        self.y_pos = y_pos # y coordinate of item
        self.color = color # color of item
        self.danger = danger # laser diraction of item
        self.summon_time = summon_time # item summon time
        self.dif = dif # difficulty increasement

mouse_x, mouse_y = 0, 0 # position of mouse

diraction = 2 # diraction of mouse
item_list = [] # item
danger_list = [] # laser line
custom_item_list = [] # item in custom

press_mouse = [0, 0] # state of pressed mouse

rod_width_pro = 0.200; rod_height_pro = 0.030 # proportion of rod (screen_width)
circle_radius_pro = 0.020 # proportion of circle (screen_width)
item_width_pro = 0.030; item_height_pro = 0.030 # proportion of item (screen_width)
item_size = round(((screen_width * item_width_pro / 2)**2 + (screen_width * item_height_pro / 2)**2)**0.5, 0) # radius of item
danger_size_pro = 1.20 # proportion of width of danger zone (item_size)
score_size_pro = 0.040 # proportion of score font size
score_xcoord_pro = 0.120; score_ycoord_pro = 0.030 # score position
idx_size_pro = 0.040 # proportion of custom item index size
idx_xcoord_pro = 0.150; idx_ycoord_pro = 0.030 # proportion of custom item index position
laser_thick = 10 # thickness of laser

score = 0 # score

difficulty = 0 # difficulty
max_misses = 3 # max continuous misses
misses = 0 # new continuous misses
increase_dif = 1 # increase of difficulty

# time variable setting
item_delay = 2.20 # te time that between summoning and engaging item
danger_delay = 2.40 # the time that between summoning and deleting item
danger_time = 2.50 # the time that between summoning and deleting danger zone; detecting = [danger_delay, danger_time]
item_summon_cycle = 2.50 # the time that between summoning item and next item

starting_time = time.time() # time of start
summon_block_time = time.time() # cycle of summoning block

'''=============================functions============================='''
# function veriable list
# center coordinate: (cen_x, cen_y)
# x-axis length: size_x
# y-axis: length size_y
# angle: between x-axis and below edge
# line_width: width of line

# get point of rectangle
def get_rect_point(cen_x, cen_y, size_x, size_y, angle):
    tx1 = size_x/2 * math.cos(angle)
    tx2 = - size_y/2 * math.sin(angle)
    ty1 = size_x/2 * math.sin(angle)
    ty2 = size_y/2 * math.cos(angle)

    return (
        (cen_x - tx1 + tx2, cen_y - ty1 + ty2),
        (cen_x - tx1 - tx2, cen_y - ty1 - ty2),
        (cen_x + tx1 - tx2, cen_y + ty1 - ty2),
        (cen_x + tx1 + tx2, cen_y + ty1 + ty2)
    )

# draw rectangle
def draw_rect(cen_x, cen_y, size_x, size_y, angle, color, line_width):
    pygame.draw.polygon(screen, color, (\
        get_rect_point(cen_x, cen_y, size_x, size_y, angle)
    ), line_width)

# draw rod that we move and rotate
def draw_rod(mouse_x, mouse_y, size_x, size_y, diraction, press_mouse):
    rod_color = (0, 0, 0)
    if press_mouse == [0, 0]: rod_color = (0, 0, 0)
    if press_mouse == [1, 0]: rod_color = (255, 0, 0)
    if press_mouse == [0, 1]: rod_color = (0, 0, 255)
    draw_rect(mouse_x, mouse_y, size_x, size_y, math.pi / 4 * diraction, rod_color, 0)

# draw judgment line(circle)
def draw_circle(mouse_x, mouse_y, radius):
    pygame.draw.circle(screen, (0, 255, 0), [mouse_x, mouse_y], int(radius), 5)

# draw view item: item position preview
def draw_view_item(select):
    item_color = (0, 0, 0)
    if select.color == 0: item_color = (241, 174, 204)
    if select.color == 1: item_color = (80, 188, 223)
    draw_rect(select.x_pos, select.y_pos, screen_width * item_width_pro, screen_width * item_height_pro, \
        time.time() - select.summon_time, item_color, 0)

# draw item: item view
def draw_item(select):
    item_color = (0, 0, 0)
    if select.color == 0: item_color = (255, 0, 0)
    if select.color == 1: item_color = (0, 0, 255)
    draw_rect(select.x_pos, select.y_pos, screen_width * item_width_pro, screen_width * item_height_pro, \
        time.time() - select.summon_time, item_color, 0)

# draw view laser: laser diraction preview
def draw_danger_line(select):
    w = 1
    if select.danger == 1 or select.danger == 3: w = math.sqrt(2) # width correction
    draw_rect(select.x_pos + item_size * danger_size_pro * math.sin(select.danger * math.pi / 4), \
        select.y_pos - item_size * danger_size_pro * math.cos(select.danger * math.pi / 4), \
        (screen_width + screen_height)*2, \
        0, select.danger * math.pi / 4, (128, 0, 0), int(laser_thick * w))
    draw_rect(select.x_pos - item_size * danger_size_pro * math.sin(select.danger * math.pi / 4), \
        select.y_pos + item_size * danger_size_pro * math.cos(select.danger * math.pi / 4), \
        (screen_width + screen_height)*2, \
        0, select.danger * math.pi / 4, (128, 0, 0), int(laser_thick * w))

# draw laser: laser move
def draw_danger_laser(select):
    w = 1
    if select.danger == 1 or select.danger == 3: w = math.sqrt(2) # width correction
    if select.danger == 0: 
        length = (2 * screen_width) \
            * (time.time() - select.summon_time - (danger_time - 0.50) / select.dif) / (0.50 / select.dif) # length of laser(time)
        draw_rect(0, select.y_pos - item_size * danger_size_pro,
            length, 0, select.danger * math.pi / 4, (255, 0, 0), int(laser_thick * w))
        draw_rect(0, select.y_pos + item_size * danger_size_pro,
            length, 0, select.danger * math.pi / 4, (255, 0, 0), int(laser_thick * w))
    else:
        length = (2 * screen_height * math.sqrt(2)) \
            * (time.time() - select.summon_time - (danger_time - 0.50) / select.dif) / (0.50 / select.dif) # length of laser(time)
        cal_x = select.x_pos - (math.cos(select.danger * math.pi / 4) * select.y_pos + item_size * danger_size_pro) \
            / math.sin(select.danger * math.pi / 4)
        draw_rect(cal_x, 0, length, 0, select.danger * math.pi / 4, (255, 0, 0), int(10 * w))
        cal_x = select.x_pos - (math.cos(select.danger * math.pi / 4) * select.y_pos - item_size * danger_size_pro) \
            / math.sin(select.danger * math.pi / 4)
        draw_rect(cal_x, 0, length, 0, select.danger * math.pi / 4, (255, 0, 0), int(10 * w))

# touch item: to check item collistion to circle
def collision_item(mouse_x, mouse_y, radius, select):
    if ((mouse_x - select.x_pos)**2 + (mouse_y - select.y_pos)**2)**0.5 <= radius + item_size: return True
    else: return False

# touch laser: to check block collistion to laser
def collision_laser(mouse_x, mouse_y, size_x, size_y, diraction, select):
    minv = 10**100; maxv = -10**100
    angle = diraction * math.pi / 4
    rect_point = get_rect_point(mouse_x, mouse_y, size_x, size_y, angle)
    for coord in rect_point:
        cal = math.sin(select.danger * math.pi / 4) * (coord[0] - select.x_pos) \
            - math.cos(select.danger * math.pi / 4) * (coord[1] - select.y_pos)
        minv = min(minv, cal)
        maxv = max(maxv, cal)
    if minv <= item_size * danger_size_pro - laser_thick/2 <= maxv or \
        minv <= - item_size * danger_size_pro + laser_thick/2 <= maxv : # to consider laser thickness
        return True
    else: return False

# to draw English text
def blit(message, font_size, cen_x, cen_y, color):
    font = pygame.font.SysFont('consolas', font_size)
    text = font.render(message, True, color)
    text_rect = text.get_rect()
    text_rect.center = (cen_x, cen_y)
    screen.blit(text, text_rect)

# to draw Korean text
def blit_kor(message, font_size, cen_x, cen_y, color):
    font = pygame.font.SysFont("malgungothic", font_size)
    text = font.render(message, True, color)
    text_rect = text.get_rect()
    text_rect.center = (cen_x, cen_y)
    screen.blit(text, text_rect)

# to check click button(rectangle)
def if_click_rect(coord1, coord2):
    if screen_width * coord1[0] <= pygame.mouse.get_pos()[0] <= screen_width * coord2[0] \
        and screen_height * coord1[1] <= pygame.mouse.get_pos()[1] <= screen_height * coord2[1]: return True
    else: return False

# to draw button (rectangle + text)
def button(coord1, coord2, message, font_size, color):
    pygame.draw.polygon(screen, color, [
        [screen_width * coord1[0], screen_height * coord1[1]],
        [screen_width * coord2[0], screen_height * coord1[1]],
        [screen_width * coord2[0], screen_height * coord2[1]],
        [screen_width * coord1[0], screen_height * coord2[1]]
    ], 10)
    blit(message, font_size, screen_width * (coord1[0] + coord2[0]) / 2, \
        screen_height * (coord1[1] + coord2[1] + font_size * 1/8000) / 2, (0, 0, 0))

'''=============================functions============================='''

'''==========================in-game screens=========================='''

# game menu screen
def menu_screen():
    running = True # store running?
    while running:
        for event in pygame.event.get(): # detect event
            if event.type == pygame.QUIT: running = False # quit when exit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False # quit when press ESC
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    if if_click_rect([0.30, 0.30], [0.70, 0.40]): infinity_play_setting_screen() # play click
                    if if_click_rect([0.30, 0.50], [0.70, 0.60]): custom_menu_screen() # custom click
                    if if_click_rect([0.30, 0.70], [0.70, 0.80]): running = False # exit click
        
        screen.fill((255, 255, 255)) # fill background to use RGB system

        # title
        blit("Devita", 150, screen_width * 0.50, screen_height * 0.15, (0, 0, 0))

        # make button
        button([0.30, 0.30], [0.70, 0.40], "PLAY", 80, (0, 0, 0))
        button([0.30, 0.50], [0.70, 0.60], "CUSTOM", 80, (0, 0, 0))
        button([0.30, 0.70], [0.70, 0.80], "EXIT", 80, (0, 0, 0))

        pygame.display.update() # update screen

# difficulty setting in infinity play 
def infinity_play_setting_screen():
    global difficulty, item_delay, danger_delay, danger_time, item_summon_cycle, increase_dif, max_misses
    difficulty_color = [(0, 0, 0), (0, 0, 255), (0, 0, 0)] # color list; if select, color blue
    difficulty = 2 # first setting
    running = True # store running?
    while running:
        for event in pygame.event.get(): # detect event
            if event.type == pygame.QUIT: running = False # quit when exit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False # quit when press ESC
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    if if_click_rect([0.15, 0.25], [0.35, 0.35]):
                        difficulty = 1 # easy
                        difficulty_color = [(0, 0, 0), (0, 0, 0), (0, 0, 0)] # color reset
                        difficulty_color[0] = (0, 0, 255) # color change
                        item_delay, danger_delay, danger_time, item_summon_cycle, increase_dif, max_misses \
                            = 1.25, 1.40, 1.50, 2.00, 1, 3 # easy setting value
                    if if_click_rect([0.40, 0.25], [0.60, 0.35]):
                        difficulty = 2 # medium
                        difficulty_color = [(0, 0, 0), (0, 0, 0), (0, 0, 0)] # color reset
                        difficulty_color[1] = (0, 0, 255) # color change
                        item_delay, danger_delay, danger_time, item_summon_cycle, increase_dif, max_misses \
                            = 1.00, 1.10, 1.20, 1.50, 2, 3 # medium setting value
                    if if_click_rect([0.65, 0.25], [0.85, 0.35]):
                        difficulty = 3 # hard
                        difficulty_color = [(0, 0, 0), (0, 0, 0), (0, 0, 0)] # color reset
                        difficulty_color[2] = (0, 0, 255) # color change
                        item_delay, danger_delay, danger_time, item_summon_cycle, increase_dif, max_misses \
                            = 0.65, 0.70, 0.80, 1.00, 4, 3 # hard setting value
                    if if_click_rect([0.35, 0.41], [0.65, 0.49]): 
                        difficulty = 0 # no difficulty
                        difficulty_color = [(0, 0, 0), (0, 0, 0), (0, 0, 0)] # color reset
                        infinity_play_specific_setting_screen() # click specific setting
                    if if_click_rect([0.30, 0.80], [0.70, 0.95]): infinity_play_screen() # click play
                    if if_click_rect([0.80, 0.81], [0.95, 0.89]): tutorial_screen() # tutorial
        
        screen.fill((255, 255, 255)) # fill background to use RGB system

        # difficulty setting
        blit("Difficulty", 100, screen_width * 0.50, screen_height * 0.15, (0, 0, 0))
        button([0.15, 0.25], [0.35, 0.35], "EASY", 80, difficulty_color[0])
        button([0.40, 0.25], [0.60, 0.35], "MEDIUM", 80, difficulty_color[1])
        button([0.65, 0.25], [0.85, 0.35], "HARD", 80, difficulty_color[2])

        # make button
        button([0.35, 0.41], [0.65, 0.49], "Specific Setting", 60, (0, 0, 0))
        button([0.30, 0.80], [0.70, 0.95], "START", 120, (0, 0, 0))
        button([0.80, 0.81], [0.95, 0.89], "Tutorial", 60, (0, 0, 0))

        pygame.display.update() # update screen

def infinity_play_specific_setting_screen():
    global increase_dif, max_misses, item_delay, danger_delay, danger_time, item_summon_cycle
    select_color = [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)] # color list, if select, color blue
    select_value = [item_delay * 1000, danger_delay * 1000, item_summon_cycle * 1000, increase_dif, max_misses] # value of variable
    select = 0 # no select
    up_press = 0; down_press = 0; up_press_time = time.time(); down_press_time = time.time() # fast changing value
    running = True # store running?
    while running:
        for event in pygame.event.get(): # detect event
            if event.type == pygame.QUIT: running = False # quit when exit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False # quit when press ESC
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    if if_click_rect([0.60, 0.26], [0.90, 0.34]):
                        select = 1 # first variable
                        select_color = [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)] # color reset
                        select_color[0] = (0, 0, 255) # color change
                    if if_click_rect([0.60, 0.36], [0.90, 0.44]):
                        select = 2 # second variable
                        select_color = [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)] # color reset
                        select_color[1] = (0, 0, 255) # color change
                    if if_click_rect([0.60, 0.46], [0.90, 0.54]):
                        select = 3 # third variable
                        select_color = [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)] # color reset
                        select_color[2] = (0, 0, 255) # color change
                    if if_click_rect([0.60, 0.56], [0.90, 0.64]):
                        select = 4 # fourth variable
                        select_color = [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)] # color reset
                        select_color[3] = (0, 0, 255) # color change
                    if if_click_rect([0.60, 0.66], [0.90, 0.74]):
                        select = 5 # fifth variable
                        select_color = [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)] # color reset
                        select_color[4] = (0, 0, 255) # color change
                    if if_click_rect([0.30, 0.80], [0.70, 0.95]): infinity_play_screen() # click play

        # change value
        if keyboard.is_pressed("Up"): # if press "up"
            if up_press == 0 or time.time() - up_press_time > 0.5: # if first click or click more than 0.5s
                if select <= 3: select_value[select - 1] = select_value[select - 1] + 10 # +10 (1~3)
                else: select_value[select - 1] = select_value[select - 1] + 1 # +1 (4~5)
            up_press = 1 # already add value
        else: # not click
            up_press_time = time.time()
            up_press = 0 # reset
        if keyboard.is_pressed("Down"): # if press "down"
            if down_press == 0 or time.time() - down_press_time > 0.5: # if first click or click more than 0.5s
                if select <= 3: select_value[select - 1] = max(0, select_value[select - 1] - 10) # +10 (1~3)
                else: select_value[select - 1] = max(0, select_value[select - 1] - 1) # +1 (4~5)
            down_press = 1 # already add value
        else:
            down_press_time = time.time()
            down_press = 0 # reset
        
        # value correction: item_delay <= danger_delay
        if select_value[1] < select_value[0]: 
            if select == 1: select_value[0] = select_value[1]
            if select == 2: select_value[1] = select_value[0]

        screen.fill((255, 255, 255)) # fill background to use RGB system

        # title
        blit("Specific Setting", 150, screen_width * 0.50, screen_height * 0.15, (0, 0, 0))

        # variable name
        blit("item delay", 60, screen_width * 0.25, screen_height * 0.30, (0, 0, 0))
        blit("laser time", 60, screen_width * 0.25, screen_height * 0.40, (0, 0, 0))
        blit("item summon time", 60, screen_width * 0.25, screen_height * 0.50, (0, 0, 0))
        blit("difficulty increasement", 60, screen_width * 0.25, screen_height * 0.60, (0, 0, 0))
        blit("MAX continuous misses", 60, screen_width * 0.25, screen_height * 0.70, (0, 0, 0))

        # buttons
        button([0.60, 0.26], [0.90, 0.34], str(int(select_value[0])), 60, select_color[0])
        button([0.60, 0.36], [0.90, 0.44], str(int(select_value[1])), 60, select_color[1])
        button([0.60, 0.46], [0.90, 0.54], str(int(select_value[2])), 60, select_color[2])
        button([0.60, 0.56], [0.90, 0.64], str(int(select_value[3])), 60, select_color[3])
        button([0.60, 0.66], [0.90, 0.74], str(int(select_value[4])), 60, select_color[4])
        button([0.30, 0.80], [0.70, 0.95], "START", 120, (0, 0, 0))
        
        # value update
        item_delay = select_value[0] / 1000
        danger_delay = select_value[1] / 1000
        danger_time = danger_delay - 0.050
        item_summon_cycle = select_value[2] / 1000
        incraese_dif = select_value[3]
        max_misses = select_value[4]

        pygame.display.update() # update screen

def tutorial_screen():
    global mouse_x, mouse_y, item_list, danger_list, diraction, score, difficulty, max_misses, increase_dif
    global rod_width_pro, rod_height_pro, circle_radius_pro, item_width_pro, item_height_pro
    global item_size, danger_size_pro, score_size_pro, score_xcoord_pro, score_ycoord_pro
    global item_delay, danger_delay, danger_time, item_summon_cycle, starting_time, summon_block_time
    step = 0 # tutorial step
    laser_tutorial_time = 0 # for tutorial laser
    item_list.clear(); danger_list.clear() # reset
    running = True # store running?
    while running:
        for event in pygame.event.get(): # detect event
            if event.type == pygame.QUIT: running = False # quit when exit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False # quit when press ESC
                if event.key == pygame.K_a: diraction = (diraction + 3) % 4
                if event.key == pygame.K_s: diraction = (diraction + 1) % 4 # rod diraction change
                if event.key == pygame.K_RIGHT:
                    step = step + 1 # next tutorial
                    if step == 4: # show item
                        item_list.append(item(345, 550, 0, 1, time.time(), 1))
                        danger_list.append(item_list[len(item_list)-1])
                    if step == 12: # show laser
                        laser_tutorial_time = time.time() # time setting
                if event.key == pygame.K_LEFT: # move step
                    step = max(step - 1, 0)
                    if step == 3: # reset
                        item_list.clear()
                        danger_list.clear()
            # mouse click
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: press_mouse[0] = 1
                if event.button == 3: press_mouse[1] = 1
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: press_mouse[0] = 0
                if event.button == 3: press_mouse[1] = 0
        
        screen.fill((255, 255, 255)) # fill background to use RGB system

        # make item
        for select in item_list:
            if step <= 5:
                draw_view_item(select)
            if step >= 6:
                draw_item(select)
        
        # make danger
        for select in danger_list:
            draw_danger_line(select)
            if step >= 12: # move laser
                length = (2 * screen_height * math.sqrt(2)) * (time.time() - laser_tutorial_time) / (1.00)
                cal_x = select.x_pos - (math.cos(select.danger * math.pi / 4) * select.y_pos + item_size * danger_size_pro) \
                    / math.sin(select.danger * math.pi / 4)
                draw_rect(cal_x, 0, length, 0, select.danger * math.pi / 4, (255, 0, 0), 14)
                cal_x = select.x_pos - (math.cos(select.danger * math.pi / 4) * select.y_pos - item_size * danger_size_pro) \
                    / math.sin(select.danger * math.pi / 4)
                draw_rect(cal_x, 0, length, 0, select.danger * math.pi / 4, (255, 0, 0), 14)
        
        # make rod
        mouse_x, mouse_y = pygame.mouse.get_pos()
        draw_rod(mouse_x, mouse_y, screen_width * rod_width_pro, screen_width * rod_height_pro, diraction, press_mouse)
        draw_circle(mouse_x, mouse_y, screen_width * circle_radius_pro)

        # below message
        if step <= 14: blit_kor("좌우 화살표를 눌러 이동하세요", 60, screen_width * 0.50, screen_height * 0.90, (0, 0, 0))
        if step == 15: blit_kor("오른쪽 화살표를 눌러 종료하세요", 60, screen_width * 0.50, screen_height * 0.90, (0, 0, 0)) # last step

        # message (step)
        if step == 0:
            blit_kor("막대는 마우스를 따라 움직입니다", 80, screen_width * 0.50, screen_height * 0.50, (0, 0, 0))
        if step == 1:
            blit_kor("a와 s로 막대를 회전할 수 있습니다", 80, screen_width * 0.50, screen_height * 0.50, (0, 0, 0))
        if step == 2:
            blit_kor("우클릭과 좌클릭으로 막대의 색을 바꿀 수 있습니다", 80, screen_width * 0.50, screen_height * 0.50, (0, 0, 0))
        if step == 3:
            blit_kor("좌측 상단에 있는 것은 점수입니다", 80, screen_width * 0.50, screen_height * 0.50, (0, 0, 0))
        if step == 4:
            blit_kor("분홍색(하늘색)은 아이템의 위치를 보여줍니다", 80, screen_width * 0.50, screen_height * 0.50, (0, 0, 0))  
        if step == 5:
            blit_kor("진한 빨간색은 레이저의 각도를 미리 보여줍니다", 80, screen_width * 0.50, screen_height * 0.50, (0, 0, 0))
        if step == 6:
            blit_kor("시간이 지나면 아이템의 색이 변합니다", 80, screen_width * 0.50, screen_height * 0.50, (0, 0, 0))
        if step == 7:
            blit_kor("클릭으로 막대를 같은 색으로 만드세요", 80, screen_width * 0.50, screen_height * 0.50, (0, 0, 0))
        if step == 8:
            blit_kor("초록색 원이 아이템과 닿게 하면 아이템을 먹습니다", 80, screen_width * 0.50, screen_height * 0.50, (0, 0, 0))
        if step == 9:
            blit_kor("아이템을 하나 먹을 때 마다 점수가 1 오릅니다", 80, screen_width * 0.50, screen_height * 0.50, (0, 0, 0))
        if step == 10:
            blit_kor("시간이 지나면 아이템이 사라지고 레이저가 나옵니다", 80, screen_width * 0.50, screen_height * 0.50, (0, 0, 0))
        if step == 11:
            blit_kor("레이저에 닿지 않게 방향을 맞추세요", 80, screen_width * 0.50, screen_height * 0.50, (0, 0, 0))
        if step == 12:
            blit_kor("그러면 레이저를 피할 수 있습니다", 80, screen_width * 0.50, screen_height * 0.50, (0, 0, 0))
        if step == 13:
            blit_kor("만약 레이저에 닿으면 게임이 종료됩니다", 80, screen_width * 0.50, screen_height * 0.50, (0, 0, 0))
        if step == 14:
            blit_kor("여러번 연속해서 아이템을 못 먹어도 게임이 끝납니다", 80, screen_width * 0.50, screen_height * 0.50, (0, 0, 0))
        if step >= 15:
            running = False

        # collision and item remove
        for select in item_list:
            if 6 <= step <= 9: # can touch item (score +1)
                if collision_item(mouse_x, mouse_y, screen_width * circle_radius_pro, select):
                    # match color
                    if select.color == 0 and press_mouse[0] == 1: 
                        score = score + 1
                        item_list.remove(select)
                    if select.color == 1 and press_mouse[1] == 1: 
                        score = score + 1
                        item_list.remove(select)
        
        # score
        blit("score: " + str(score).zfill(3), int(screen_width * score_size_pro), \
            screen_width * score_xcoord_pro, screen_width * score_ycoord_pro, (0, 0, 0))

        pygame.display.update() # update screen

def infinity_play_screen():
    global mouse_x, mouse_y, item_list, danger_list, diraction, score, max_misses, increase_dif
    global rod_width_pro, rod_height_pro, circle_radius_pro, item_width_pro, item_height_pro
    global item_size, danger_size_pro, score_size_pro, score_xcoord_pro, score_ycoord_pro
    global item_delay, danger_delay, danger_time, item_summon_cycle, starting_time, summon_block_time

    # initialization
    diraction = 2; item_list = []; danger_list = []; score = 0; press_mouse = [0, 0]
    summon_block_time = time.time(); starting_time = time.time(); misses = 0

    running = True # store running?
    while running:
        for event in pygame.event.get(): # detect event
            if event.type == pygame.QUIT: running = False # quit when exit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False # quit when press ESC
                if event.key == pygame.K_a: diraction = (diraction + 3) % 4
                if event.key == pygame.K_s: diraction = (diraction + 1) % 4 # rod diraction change
            # mouse click
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: press_mouse[0] = 1
                if event.button == 3: press_mouse[1] = 1
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: press_mouse[0] = 0
                if event.button == 3: press_mouse[1] = 0
        
        screen.fill((255, 255, 255)) # fill background to use RGB system

        # add item
        if time.time() - summon_block_time > item_summon_cycle / (increase_dif * (time.time() - starting_time) / 1000 + 1):
            item_list.append(
                item(
                    random.randint(item_size, screen_width - item_size),
                    random.randint(item_size, screen_height - item_size), 
                    random.randint(0, 1), random.randint(0, 3), time.time(), 
                    increase_dif * (time.time() - starting_time) / 1000 + 1
                )
            )
            danger_list.append(item_list[len(item_list)-1]) # also add laser list
            summon_block_time = time.time() # reset
        
        # make item
        for select in item_list:
            if time.time() - select.summon_time < item_delay / select.dif: # preview item
                draw_view_item(select)
            if item_delay / select.dif <= time.time() - select.summon_time <= danger_delay / select.dif: # real item
                draw_item(select)
        
        # make danger
        for select in danger_list:
            draw_danger_line(select) # preview laser
            if (danger_time - 0.50) / select.dif < time.time() - select.summon_time: # real laser
                draw_danger_laser(select)
        
        # make rod
        mouse_x, mouse_y = pygame.mouse.get_pos()
        draw_rod(mouse_x, mouse_y, screen_width * rod_width_pro, screen_width * rod_height_pro, diraction, press_mouse)
        draw_circle(mouse_x, mouse_y, screen_width * circle_radius_pro)

        # collision and item remove
        for select in item_list:
            if item_delay / select.dif <= time.time() - select.summon_time <= danger_delay / select.dif: # real item
                if collision_item(mouse_x, mouse_y, screen_width * circle_radius_pro, select):
                    # match color
                    if select.color == 0 and press_mouse[0] == 1:
                        score = score + 1
                        misses = 0
                        item_list.remove(select)
                    if select.color == 1 and press_mouse[1] == 1: 
                        score = score + 1
                        misses = 0
                        item_list.remove(select)
        
        for select in danger_list:
            if time.time() - select.summon_time >= danger_time / select.dif: # real laser
                if collision_laser(mouse_x, mouse_y, screen_width * rod_width_pro, screen_width * rod_height_pro, diraction, select):
                    running = False # game over
                else:
                    # delete
                    try: 
                        item_list.remove(select)
                        misses = misses + 1
                    except: pass # item can be deleted because of touching laser and item
                    danger_list.remove(select)

        # score
        blit("score: " + str(score).zfill(3), int(screen_width * score_size_pro), \
            screen_width * score_xcoord_pro, screen_width * score_ycoord_pro, (0, 0, 0))

        # misses game over
        if misses > max_misses: running = False

        pygame.display.update() # update screen

    game_over_screen()
 
def custom_menu_screen():
    running = True # store running?
    while running:
        for event in pygame.event.get(): # detect event
            if event.type == pygame.QUIT: running = False # quit when exit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False # quit when press ESC
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    if if_click_rect([0.15, 0.30], [0.45, 0.50]):
                        custom_play_screen() # click play
                    if if_click_rect([0.55, 0.30], [0.85, 0.50]):
                        custom_make_screen() # click make
        
        screen.fill((255, 255, 255)) # fill background to use RGB system

        # title
        blit("Custom", 150, screen_width * 0.50, screen_height * 0.15, (0, 0, 0))

        # button
        button([0.15, 0.30], [0.45, 0.50], "PLAY", 120, (0, 0, 0))
        button([0.55, 0.30], [0.85, 0.50], "MAKE", 120, (0, 0, 0))

        pygame.display.update() # update screen

def custom_make_screen():
    global custom_item_list
    now_idx = 1 # made index
    show_idx = 1 # showed index
    custom_item_list.clear()
    custom_item_list.append(item(-1000, -1000, 0, 0, 0, 0))
    custom_item_list.append(item(-1000, -1000, 0, 0, 0, 0)) # initialization
    up_press = 0; down_press = 0; up_press_time = time.time(); down_press_time = time.time() # fast changing value
    running = True # store running?
    while running:
        for event in pygame.event.get(): # detect event
            if event.type == pygame.QUIT: running = False # quit when exit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False # quit when press ESC
                if event.key == pygame.K_LEFT: show_idx = max(show_idx - 1, 1)
                if event.key == pygame.K_RIGHT: show_idx = min(show_idx + 1, now_idx) # change index
                if event.key == pygame.K_SPACE: # make item
                    now_idx = now_idx + 1
                    show_idx = show_idx + 1
                    custom_item_list.append(item(
                        -1000, -1000, 0, 0, custom_item_list[now_idx - 1].summon_time, 1
                    ))
                if event.key == pygame.K_a: 
                    custom_item_list[now_idx].danger = (custom_item_list[now_idx].danger + 3) % 4
                if event.key == pygame.K_s: 
                    custom_item_list[now_idx].danger = (custom_item_list[now_idx].danger + 1) % 4 # laser rotation
            # mouse click
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    custom_item_list[now_idx] = item(
                        pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1],
                        0, 0, custom_item_list[now_idx - 1].summon_time, 1
                    )
                if event.button == 3: 
                    custom_item_list[now_idx] = item(
                        pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1],
                        1, 0, custom_item_list[now_idx - 1].summon_time, 1
                    )
        
        # time
        if keyboard.is_pressed("Up"): # if press "up"
            if up_press == 0 or time.time() - up_press_time > 0.5: # if first click or click more than 0.5s
                custom_item_list[now_idx].summon_time = custom_item_list[now_idx].summon_time + 10 # +10
            up_press = 1 # already pressed
        else: # not press
            up_press_time = time.time()
            up_press = 0 # reset
        if keyboard.is_pressed("Down"): # if press "down"
            if down_press == 0 or time.time() - down_press_time > 0.5: # if first click or click more than 0.5s
                custom_item_list[now_idx].summon_time = max(
                        custom_item_list[now_idx].summon_time - 10, 
                        custom_item_list[now_idx - 1].summon_time
                    ) # +10
            down_press = 1 # already pressed
        else: # not press
            down_press_time = time.time()
            down_press = 0 # reset

        # background color
        if show_idx == now_idx:
            screen.fill((255, 255, 255)) # fill background to use RGB system
        else:
            screen.fill((211, 211, 211)) # fill background to use RGB system

        # show item and laser
        draw_item(custom_item_list[show_idx])
        draw_danger_line(custom_item_list[show_idx])
        
        # between time
        blit(
            str(int(custom_item_list[show_idx].summon_time - custom_item_list[show_idx - 1].summon_time)), 
            50, custom_item_list[show_idx].x_pos, custom_item_list[show_idx].y_pos, (0, 0, 0)
        )

        # "show index / made index"
        blit(str(show_idx).zfill(4) + ' / ' + str(now_idx).zfill(4), int(screen_width * idx_size_pro), \
            screen_width * idx_xcoord_pro, screen_width * idx_ycoord_pro, (0, 0, 0))

        pygame.display.update() # update screen
    
    custom_save_screen()

def custom_save_screen():
    custom_item_delay, custom_danger_delay, custom_danger_time = 2.20, 2.40, 2.50
    select_color = [(0, 0, 0), (0, 0, 0)] # color list: if select, color blue
    select_value = [custom_item_delay * 1000, custom_danger_time * 1000] # value list
    select = 0 # no select
    up_press = 0; down_press = 0; up_press_time = time.time(); down_press_time = time.time() # fast changing value
    running = True # store running?
    while running:
        for event in pygame.event.get(): # detect event
            if event.type == pygame.QUIT: running = False # quit when exit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False # quit when press ESC
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    if if_click_rect([0.60, 0.26], [0.90, 0.34]):
                        select = 1 # first value
                        select_color = [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)] # color reset
                        select_color[0] = (0, 0, 255) # color change
                    if if_click_rect([0.60, 0.36], [0.90, 0.44]):
                        select = 2 # second value
                        select_color = [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)] # color reset
                        select_color[1] = (0, 0, 255) # color change
                    if if_click_rect([0.30, 0.80], [0.70, 0.95]):
                        # file print
                        sys.stdout = open('./map_out.txt','w')
                        print("{} {} {}".format(
                            round(custom_item_delay, 3), 
                            round(custom_danger_delay, 3), 
                            round(custom_danger_time, 3)
                        )) # print time delay
                        print(len(custom_item_list) - 2) # print item count
                        for select in custom_item_list[1:-1:1]:
                            print("{} {} {} {} {}".format(
                                select.x_pos, select.y_pos, select.color, select.danger, 
                                round(select.summon_time, 3))
                            ) # print item
                        sys.stdout.close()
                        running = False

        # change value
        if keyboard.is_pressed("Up"): # if click "up"
            if up_press == 0 or time.time() - up_press_time > 0.5: # if first click or click more than 0.5s 
                select_value[select - 1] = select_value[select - 1] + 10 # +10
            up_press = 1 # already pressed
        else: # not click
            up_press_time = time.time()
            up_press = 0 # reset
        if keyboard.is_pressed("Down"): # if click "down"
            if down_press == 0 or time.time() - down_press_time > 0.5: # if first click or click more than 0.5s
                select_value[select - 1] = max(0, select_value[select - 1] - 10) # +10
            down_press = 1 # already pressed
        else: # not click
            down_press_time = time.time()
            down_press = 0 # reset
        
        # value correction
        if select_value[1] < select_value[0]: 
            if select == 1: select_value[0] = select_value[1]
            if select == 2: select_value[1] = select_value[0]

        screen.fill((255, 255, 255)) # fill background to use RGB system

        # title
        blit("Value Setting", 150, screen_width * 0.50, screen_height * 0.15, (0, 0, 0))

        # variables
        blit("item delay", 60, screen_width * 0.25, screen_height * 0.30, (0, 0, 0))
        blit("laser time", 60, screen_width * 0.25, screen_height * 0.40, (0, 0, 0))

        # button
        button([0.60, 0.26], [0.90, 0.34], str(int(select_value[0])), 60, select_color[0])
        button([0.60, 0.36], [0.90, 0.44], str(int(select_value[1])), 60, select_color[1])
        button([0.30, 0.80], [0.70, 0.95], "SAVE", 120, (0, 0, 0))

        # update value
        custom_item_delay = select_value[0] / 1000
        custom_danger_time = select_value[1] / 1000
        custom_danger_delay = custom_danger_time - 0.100

        pygame.display.update() # update screen
    
def custom_play_screen():
    global mouse_x, mouse_y, item_list, danger_list, diraction, score, max_misses
    global rod_width_pro, rod_height_pro, circle_radius_pro, item_width_pro, item_height_pro
    global item_size, danger_size_pro, score_size_pro, score_xcoord_pro, score_ycoord_pro
    global item_delay, danger_delay, danger_time, starting_time

    # initialization
    diraction = 2; item_list = []; danger_list = []; score = 0; press_mouse = [0, 0]
    clear = 0; starting_time = time.time(); misses = 0

    # file input
    try: f = open("./map_in.txt", "r")
    except: print("file load error"); exit(0) # if fail
    try: item_delay, danger_delay, danger_time = map(float, f.readline()[0:-1:1].split())
    except: print("file format error"); exit(0) # if fail

    try: count = int(f.readline()[0:-1:1])
    except: print("file format error"); exit(0) # if fail
    for _ in range(count):
        try: temp = list(map(float, f.readline()[0:-1:1].split()))
        except: print("file format error"); exit(0) # if fail
        item_list.append(item(temp[0], temp[1], temp[2], temp[3], temp[4], 1))
        item_list[len(item_list)-1].summon_time /= 1000
        danger_list.append(item_list[len(item_list)-1])

    starting_time = time.time()

    running = True # store running?
    while running:
        for event in pygame.event.get(): # detect event
            if event.type == pygame.QUIT: running = False # quit when exit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False # quit when press ESC
                if event.key == pygame.K_a: diraction = (diraction + 3) % 4
                if event.key == pygame.K_s: diraction = (diraction + 1) % 4 # rod rotation
            # mouse click
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: press_mouse[0] = 1
                if event.button == 3: press_mouse[1] = 1
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: press_mouse[0] = 0
                if event.button == 3: press_mouse[1] = 0
        
        screen.fill((255, 255, 255)) # fill background to use RGB system
        
        # game clear
        if len(item_list) <= 0:
            clear = 1
            running = False

        # make item
        for select in item_list:
            if 0 <= time.time() - starting_time - select.summon_time <= item_delay: # preview item
                draw_view_item(select)
            if item_delay <= time.time() - starting_time - select.summon_time <= danger_delay: # real item
                draw_item(select)
            if time.time() - starting_time - select.summon_time < 0: break # optimization
        
        # make danger
        for select in danger_list:
            if 0 <= time.time() - starting_time - select.summon_time <= danger_time: # preview laser
                draw_danger_line(select)
            if danger_time - 0.05 <= time.time() - starting_time - select.summon_time <= danger_time: # real laser
                draw_danger_laser(select)
            if time.time() - starting_time - select.summon_time < 0: break # optimization
        
        # make rod
        mouse_x, mouse_y = pygame.mouse.get_pos()
        draw_rod(mouse_x, mouse_y, screen_width * rod_width_pro, screen_width * rod_height_pro, diraction, press_mouse)
        draw_circle(mouse_x, mouse_y, screen_width * circle_radius_pro)

        # collision and item remove
        for select in item_list:
            if item_delay <= time.time() - starting_time - select.summon_time <= danger_delay: # real item
                if collision_item(mouse_x, mouse_y, screen_width * circle_radius_pro, select):
                    if select.color == 0 and press_mouse[0] == 1: # color check
                        score = score + 1
                        misses = 0
                        item_list.remove(select)
                    if select.color == 1 and press_mouse[1] == 1: # color check
                        score = score + 1
                        misses = 0
                        item_list.remove(select)
            if time.time() - starting_time - select.summon_time < item_delay: break
        
        for select in danger_list:
            if danger_time <= time.time() - starting_time - select.summon_time: # real laser
                if collision_laser(mouse_x, mouse_y, screen_width * rod_width_pro, screen_width * rod_height_pro, diraction, select):
                    running = False
                else:
                    # delete
                    try: 
                        item_list.remove(select)
                        misses = misses + 1
                    except: pass # item can be deleted because of touching laser and item
                    danger_list.remove(select)
            if time.time() - starting_time - select.summon_time < danger_time: break # optimization

        # score
        blit("score: " + str(score).zfill(3), int(screen_width * score_size_pro), \
            screen_width * score_xcoord_pro, screen_width * score_ycoord_pro, (0, 0, 0))

        # misses game over
        if misses > max_misses: running = False

        pygame.display.update() # update screen

    if clear == 0: # game over
        running = False
        custom_game_over_screen()
    else: # game clear
        running = False
        custom_game_clear_screen()

def game_over_screen():
    global score
    game_over_time = time.time() # automatic restart
    running = True # store running?
    while running:
        for event in pygame.event.get(): # detect event
            if event.type == pygame.QUIT: running = False # quit when exit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False # quit when press ESC
        
        screen.fill((255, 255, 255)) # fill background to use RGB system

        blit("GAME OVER", 200, screen_width * 0.50, screen_height * 0.40, (0, 0, 0))
        blit("Score: " + str(score), 100, screen_width * 0.50, screen_height * 0.55, (0, 0, 0))

        # automatic restart
        if time.time() - game_over_time > 3:
            running = False
            infinity_play_screen() # replay
        
        pygame.display.update() # update screen

def custom_game_clear_screen():
    global score
    game_over_time = time.time() # automatic restart
    running = True # store running?
    while running:
        for event in pygame.event.get(): # detect event
            if event.type == pygame.QUIT: running = False # quit when exit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False # quit when press ESC
        
        screen.fill((255, 255, 255)) # fill background to use RGB system

        blit("GAME CLEAR!!", 200, screen_width * 0.50, screen_height * 0.40, (0, 0, 0))
        blit("Score: " + str(score), 100, screen_width * 0.50, screen_height * 0.55, (0, 0, 0))

        if time.time() - game_over_time > 3: # automatic restart
            running = False
            custom_menu_screen() # back to the menu
        
        pygame.display.update() # update screen

def custom_game_over_screen():
    global score
    game_over_time = time.time() # automatic restart
    running = True # store running?
    while running:
        for event in pygame.event.get(): # detect event
            if event.type == pygame.QUIT: running = False # quit when exit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False # quit when press ESC
        
        screen.fill((255, 255, 255)) # fill background to use RGB system

        blit("GAME OVER", 200, screen_width * 0.50, screen_height * 0.40, (0, 0, 0))
        blit("Score: " + str(score), 100, screen_width * 0.50, screen_height * 0.55, (0, 0, 0))

        if time.time() - game_over_time > 3: # automatic restart
            running = False
            custom_play_screen() # replay
        
        pygame.display.update() # update screen

'''==========================in-game screens=========================='''

menu_screen() # game start