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


class FallingItem(pygame.sprite.Sprite):
    allsprites = None
    def __init__(self):
        super().__init__()
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.speed = 1

    def appear(self, position: int = None):
        self.rect.top = self.area.top
        if position is None:
            self.rect.left = random.randrange(self.area.width - 2 * self.rect.width)
        else:
            self.rect.x = position
        self.add(self.allsprites)

    def update(self):
        self.rect = self.rect.move(0, 1 * self.speed)
        if self.rect.bottom > self.area.bottom:
            self.kill()


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
 
