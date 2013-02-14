#!/usr/bin/env python

import levelbase
import gamesprites
import pygame

class Level(levelbase.Level):

	def getPlayer(self):
		return pygame.image.load('ship.gif')

	def getObjects(self):
		return [pygame.image.load('asteroid.gif')]

	def getLayout(self):
		return [[1, 1, 1, 1, 0, 0, 1, 1, 1, 1],\
			[0, 1, 1, 0, 0, 0, 0, 1, 1, 0],\
			[1, 0, 0, 0, 0, 0, 0, 0, 0, 1],\
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],\
		        [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],\
		        [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],\
		        [1, 1, 1, 0, 0, 0, 1, 1, 0, 0],\
		        [0, 0, 0, 0, 1, 0, 0, 0, 0, 1],\
		        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],\
		        [1, 1, 0, 0, 0, 0, 1, 0, 0, 0],\
		        [1, 1, 1, 0, 0, 0, 0, 0, 0, 0]]

	def getBackground(self):
		return pygame.image.load('background.gif'), 5


while 1:
	Level = Level()
	player = Level.getPlayer
	objects = Level.getObjects
	layout = Level.getLayout

	gamesprites.Player(player, 25, 25)
	background = Level.getBackground
