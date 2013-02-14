#! /usr/bin/ python

background_image_filename = 'background.jpg'
ship_image_filename = 'ship.png'
screen_width = 640
screen_height = 480

import pygame
from pygame.locals import *
from sys import exit

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((screen_width, screen_height), 0, 32)
background = pygame.image.load(background_image_filename).convert()
ship = pygame.image.load(ship_image_filename).convert_alpha()

# make the ship start near the center of the screen
x, y = 320,400 
move_x, move_y = 0, 0

# set number of frames to display intro
intro_frames = 1000
i = 0

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        elif event.type == KEYDOWN:
            if event.key == K_LEFT:
                move_x = -250
            elif event.key == K_RIGHT:
                move_x = +250
            elif event.key == K_UP:
                move_y = -250
            elif event.key == K_DOWN:
                move_y = +250
        elif event.type == KEYUP:
            if event.key == K_LEFT:
                move_x = 0
            elif event.key == K_RIGHT:
                move_x = 0
            elif event.key == K_UP:
                move_y = 0
            elif event.key == K_DOWN:
                move_y = 0

    # 30 fps max
    time_passed = clock.tick()
    time_passed_seconds = time_passed / 1000.0

    x_distance_moved = time_passed_seconds * move_x
    y_distance_moved = time_passed_seconds * move_y
    
    x+= x_distance_moved
    y+= y_distance_moved

    # don't let the ship go off the screen
    if x > screen_width - ship.get_width():
        x = screen_width - ship.get_width()
    elif x < 0:
        x = 0
    if y > screen_height - ship.get_height():
        y = screen_height - ship.get_height()
    elif y < 0:
        y = 0

    if i < intro_frames:
        screen.fill((0, 0, 0))
        my_font = pygame.font.SysFont("arial", 18)
        text_surface = my_font.render("Simple Galaga Remake", True, (255,0,0))
	screen.blit(text_surface, ((screen_width/2)-100, 0))
        i+=1
    else:
        screen.blit(background, (0, 0))
        screen.blit(ship, (x, y))

    pygame.display.update()

