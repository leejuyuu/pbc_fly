"""
敵人機制
"""
import pygame 
from typing import Tuple
import battle
import random

INITIAL_HP_ENEMY = 30
INITIAL_HP_BOSS = 100

# 敵人本身設定
class Enemy(pygame.sprite.Sprite):

    def __init__(self):
        super(Enemy, self).__init__()
        self.image, self.rect = battle.load_image('enemy1.png', colorkey=-1, scale=(32, 34))

        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.radius = max(self.rect.width, self.rect.height)
        self.speed = 0.9
        self.rect.left = random.randrange(self.area.width - self.rect.width)
        self.rect.top = self.area.top
        self.hp = INITIAL_HP_ENEMY
        self.missile_number = 0


    def update(self):
        self.rect = self.rect.move(0, 1.5 * self.speed)

        if self.hp <= 0:
            self.kill()

        if self.rect.bottom > self.area.bottom:
            self.kill()

# 魔王本身設定
class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super(Boss, self).__init__()
        self.image, self.rect = battle.load_image('boss1.png', colorkey=-1, scale=(64, 68))
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.radius = max(self.rect.width, self.rect.height)
        self.speed = 0.7
        self.rect.left = random.randrange(self.area.width - self.rect.width)
        self.rect.top = self.area.top
        self.hp = INITIAL_HP_BOSS


    def update(self):
        self.rect = self.rect.move(1.2 * self.speed, 0)

        if self.rect.right >= self.area.right:
            self.rect = self.rect.move(-1.2 * self.speed, 0)

        if self.rect.left >= self.area.left:
            self.rect = self.rect.move(-1.2 * self.speed, 0)

        if self.hp <= 0:
            self.kill()



# 魔王射出的飛彈
class Boss_Missile(pygame.sprite.Sprite):
    pool = pygame.sprite.Group()
    active = pygame.sprite.Group()

    def __init__(self):
        super().__init__()
        self.image, self.rect = battle.load_image('bullet.png', colorkey=-1, scale=(5, 20))
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.speed = 1

    @classmethod
    def position(cls, location: Tuple[int, int], num: int = 1):
        if len(cls.pool) < num:
            cls.pool.add([Boss_Missile() for _ in range(num)])
        x_all = ((-(num-1)/2 + i)*30 for i in range(num))
        for x in x_all:
            missile = cls.pool.sprites()[0]
            missile.add(cls.allsprites, cls.active)
            missile.remove(cls.pool)
            missile.rect.bottom = location[1]
            missile.rect.centerx = int(x + location[0])

    def recycle(self):
        self.add(self.pool)
        self.remove(self.allsprites, self.active)

    def update(self):
        self.rect = self.rect.move(0, 2 * self.speed) # 敵人移動速度
        if self.rect.bottom > self.area.bottom:
            self.recycle()


# 敵人射出的飛彈
class Enemy_Missile(pygame.sprite.Sprite):
    pool = pygame.sprite.Group()
    active = pygame.sprite.Group()

    def __init__(self):
        super().__init__()
        self.image, self.rect = battle.load_image('bullet.png', colorkey=-1, scale=(5, 20))
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.speed = 1

    @classmethod
    def position(cls, location: Tuple[int, int], num: int = 1):
        if len(cls.pool) < num:
            cls.pool.add([Enemy_Missile() for _ in range(num)])
        x_all = ((-(num-1)/2 + i)*30 for i in range(num))
        for x in x_all:
            missile = cls.pool.sprites()[0]
            missile.add(cls.allsprites, cls.active)
            missile.remove(cls.pool)
            missile.rect.bottom = location[1]
            missile.rect.centerx = int(x + location[0])

    def recycle(self):
        self.add(self.pool)
        self.remove(self.allsprites, self.active)

    def update(self):
        self.rect = self.rect.move(0, 2 * self.speed) # 敵人移動速度
        if self.rect.bottom > self.area.bottom:
            self.recycle()



