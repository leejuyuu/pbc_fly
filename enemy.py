"""
敵人機制
"""
import pygame

class Enemy(pygame.sprite.Sprite):
	
	def __init__(self, position):
		super(Enemy, self).__init__()
		self.image = pygame.image.load('enemy.png')
		self.rect = self.image.get_rect()
		self.rect.x = position[0]
		self.rect.y = position[1]
		self.speed = 1

	def update(self):
		self.rect.y += self.speed 

from src.enemy import enemy
from enemy import *

pygame.init()

enemy_sprites = pygame.sprite.Group()

for i in range(60):
	enemy = Enemy((random.randrange(0, WIDTH), random.randrange(0,50)))
	enemy_sprites.add(enemy)
	all_sprites.add(enemy)

pygame.display.update()

pygame.quit()
 
