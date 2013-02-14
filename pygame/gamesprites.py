#!/usr/bin/env python

import pygame

class Player(pygame.sprite.Sprite):
	def __init__(self, image, xCenter, yCenter):
		pygame.sprite.Sprite.__init__(self)

		self.screen = pygame.display.get_surface().get_rect()
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.centerx = xCenter
		self.rect.centery = yCenter

	def update(self, xAmount):
		self.rect = self.rect.move([xAmount, 0])

		# make sure we don't go off screen
		if (self.rect.x < 0) or (self.rect.x >= self.screen.width):
			self.rect = self.rect.move([-xAmount, 0])

class Object(pygame.sprite.Sprite):
	def __init__(self,image, xCenter):
		pygame.sprite.Sprite.__init__(self)

		self.image = image
		self.rect = self.image.get_rect()
		self.rect.centerx = xCenter

	def update(self, yAmount):
		self.rect = self.rect.move([0, yAmount])


