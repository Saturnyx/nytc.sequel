import time

import pygame
from ugot import ugot

pygame.init()
screen = pygame.display.set_mode((800, 640))

bot = ugot.UGOT()
bot.initialize("192.168.88.1")
bot.balance_start_balancing()

bot.balance_set_acceleration(1)


def move_forward():
    bot.balance_move_speed(0, 40)


def move_backward():
    bot.balance_move_speed(1, 40)


def turn_left():
    bot.balance_turn_speed(2, 120)


def turn_right():
    bot.balance_turn_speed(3, 120)


c = True
try:
    while c:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                c = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    move_forward()
                elif event.key == pygame.K_s:
                    move_backward()
                elif event.key == pygame.K_a:
                    turn_left()
                elif event.key == pygame.K_d:
                    turn_right()
                elif event.key == pygame.K_e:
                    c = False
            elif event.type == pygame.KEYUP:
                bot.balance_stop_balancing()
        time.sleep(0.1)
    pygame.quit()
    bot.balance_set_acceleration(0)  # try to kill movement
except Exception as e:
    print(e)
