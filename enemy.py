"""
敵人機制
"""
import random
from typing import Tuple
import pygame
import battle


HP_BOSS = 200
HP_ENEMY = 30


# 敵人本身設定
class Enemy(pygame.sprite.Sprite):
    initial_hp = HP_ENEMY
    all_images = []

    def __init__(self):
        super(Enemy, self).__init__()
        self.image = self.all_images[0]
        self.rect = self.image.get_rect()
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.radius = max(self.rect.width, self.rect.height) / 2
        self.speed = 2
        self.rect.left = random.randrange(self.area.width - self.rect.width)
        self.rect.top = self.area.top
        self.hp = self.initial_hp
        self.missile_number = 0
        self.number_appear = 1
        self.direction = 1
        self.frame = 0

    def revival(self):
        Enemy.initial_hp += 10
        self.hp = self.initial_hp

    def appearnce(self):
        # Change image to the next
        self.image = self.all_images[self.number_appear - 1]

        self.radius = max(self.rect.width, self.rect.height)
        self.rect.left = random.randrange(self.area.width - self.rect.width)
        self.rect.top = self.area.top


    def update(self):
        if not self.frame % 80:  # 讓敵人可以隨機左右移動
            if (random.randrange(2) == 0):
                self.direction *= -1
        self.frame += 1
        self.rect = self.rect.move(0.5 * self.direction * self.speed, 1.5 * self.speed)

        if not (self.area.right >= self.rect.right and self.rect.left >= self.area.left):
            self.direction *= -1

        if self.hp <= 0:
            Explosion.position(self.rect.center)
            self.kill()

        if self.rect.bottom > self.area.bottom:
            self.kill()

# 魔王本身設定
class Boss(pygame.sprite.Sprite):
    initial_hp = HP_BOSS
    def __init__(self):
        super(Boss, self).__init__()
        self.image, self.rect = battle.load_image('boss1.png', colorkey=-1, scale=(96, 102))
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.radius = max(self.rect.width, self.rect.height) / 2
        self.speed = 1.5
        self.rect.left = random.randrange(self.area.width - self.rect.width)
        self.rect.top = self.area.top
        self.hp = HP_BOSS
        self.direction = 1
        self.number_appear = 1


    def revival(self):
        Boss.initial_hp += 80
        self.hp = self.initial_hp


    def appearnce(self):
        # if self.number_appear % 5 == 1:
        #     self.image, self.rect = battle.load_image('boss1.png', colorkey=-1, scale=(96, 102))
        if self.number_appear % 5 == 2:
            self.image, self.rect = battle.load_image('boss2.png', colorkey=-1, scale=(96, 102))
        elif self.number_appear % 5 == 3:
            self.image, self.rect = battle.load_image('boss3.png', colorkey=-1, scale=(96, 102))
        elif self.number_appear % 5 == 4:
            self.image, self.rect = battle.load_image('boss4.png', colorkey=-1, scale=(96, 102))
        elif self.number_appear % 5 == 0:
            self.image, self.rect = battle.load_image('boss5.png', colorkey=-1, scale=(96, 102))


        self.radius = max(self.rect.width, self.rect.height)
        self.rect.left = random.randrange(self.area.width - self.rect.width)
        self.rect.top = self.area.top


    def update(self):
        self.rect = self.rect.move(self.direction * self.speed, 0)

        if not (self.area.right >= self.rect.right and self.rect.left >= self.area.left):
            self.direction *= -1

        if self.hp <= 0:
            self.kill()


# 敵人射出的飛彈
class Enemy_Missile(pygame.sprite.Sprite):
    pool = pygame.sprite.Group()
    active = pygame.sprite.Group()

    def __init__(self):
        super().__init__()
        self.image, self.rect = battle.load_image('bullet_enemy.png', colorkey=-1, scale=(5, 21))
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.speed = 2

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

# 死掉時的爆炸畫面
class Explosion(pygame.sprite.Sprite):
    pool = pygame.sprite.Group()
    active = pygame.sprite.Group()

    def __init__(self):
        super().__init__()
        self.explode_image, _ = battle.load_image('enemy_ex.png', colorkey=-1, scale=(32, 34))
        self.ash_image, self.rect = battle.load_image('enemy_ash.png', colorkey=-1, scale=(32, 34))
        self.image = self.explode_image
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.speed = 2
        self.remaining_time = 0

    @classmethod
    def position(cls, location: Tuple[int, int], num: int = 1):
        if len(cls.pool) < num:
            cls.pool.add([Explosion() for _ in range(num)])
        explosion = cls.pool.sprites()[0]
        explosion.add(cls.allsprites, cls.active)
        explosion.remove(cls.pool)
        explosion.rect.center = location
        explosion.image = explosion.explode_image
        explosion.remaining_time = 7


    def recycle(self):
        self.add(self.pool)
        self.remove(self.allsprites, self.active)

    def update(self):
        if not self.remaining_time:
            self.recycle()
            return
        self.remaining_time -= 1
        self.rect = self.rect.move(0, 2 * self.speed) # 敵人移動速度
        if self.remaining_time == 1:
            self.image = self.ash_image
