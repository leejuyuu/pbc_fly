
"""
This module handles all battle mechanisms.
"""
import math
import random
from typing import Tuple
import pygame
import main


# Constants to control gameplay and hardness
SCROLLING_SPEED = 2
INITIAL_HP = 160
HP_INCREMENT = 40
HP_PACK_PROB = 0.001
POWER_UP_PROB = 0.001
HIT_HP_DROP = 10
COLLIDE_HP_DROP = 20

HP_BOSS = 200
HP_ENEMY = 30
FIRE_WAIT = 25
ENEMY_FIRE_PERIOD = 120


class Plane(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.all_images = [main.load_image('plane_lv{}.png'.format(i),
                                           colorkey=-1,
                                           scale=(64, 68))[0] for i in range(1, 4)]
        self.image = self.all_images[0]
        self.rect = self.image.get_rect()

        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        # Put the rect at the bottom center of the screen
        self.rect.centerx = int(self.area.width // 2)
        self.rect.bottom = int(self.area.height * 0.95)
        self.radius = max(self.rect.width, self.rect.height) // 2
        self.vert = 0
        self.horiz = 0
        self.speed = 2
        self.hp = INITIAL_HP
        self.power = 0

    def key_pressed(self):
        keys_pressed = pygame.key.get_pressed()
        self.vert = 0
        self.horiz = 0
        if keys_pressed[pygame.K_LEFT]:
            self.horiz = -2 * self.speed
        if keys_pressed[pygame.K_RIGHT]:
            self.horiz = 2 * self.speed
        if keys_pressed[pygame.K_UP]:
            self.vert = -2 * self.speed
        if keys_pressed[pygame.K_DOWN]:
            self.vert = 2 * self.speed

    def update(self):
        new_rect = self.rect.move((self.horiz, self.vert))

        if not self.area.contains(new_rect):
            if new_rect.left < self.area.left:
                new_rect.left = self.area.left
            elif new_rect.right > self.area.right:
                new_rect.right = self.area.right
            elif new_rect.top < self.area.top:
                new_rect.top = self.area.top
            elif new_rect.bottom > self.area.bottom:
                new_rect.bottom = self.area.bottom
        self.rect = new_rect

        if self.hp > INITIAL_HP:
            self.hp = INITIAL_HP

    def powerup(self):
        if self.power < 2:
            self.power += 1
            self.image = self.all_images[self.power]

    def fire(self):
        Missile.position(self.rect.midtop, self.power + 1)

    def remove_powerup(self):
        self.power = 0
        self.image = self.all_images[0]


class Missile(pygame.sprite.Sprite):
    pool = pygame.sprite.Group()
    active = pygame.sprite.Group()

    def __init__(self):
        super().__init__()
        self.image, self.rect = main.load_image('bullet.png', colorkey=-1, scale=(5, 20))
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.speed = 10

    @classmethod
    def position(cls, location: Tuple[int, int], num: int = 1):
        if len(cls.pool) < num:
            cls.pool.add([Missile() for _ in range(num)])
        x_all = ((-(num-1)/2 + i)*30 for i in range(num))
        for x in x_all:
            missile = cls.pool.sprites()[0]
            missile.add(cls.allsprites, cls.active)
            missile.remove(cls.pool)
            missile.rect.bottom = location[1]
            missile.rect.x = int(x + location[0])

    def recycle(self):
        self.add(self.pool)
        self.remove(self.allsprites, self.active)

    def update(self):
        self.rect = self.rect.move(0, -1 * self.speed)
        if self.rect.top < self.area.top:
            self.recycle()


class FallingItem(pygame.sprite.Sprite):
    """
    The base class for all randomly falling items which show up once in a while.
    """
    allsprites = None  # Handle to the 'allsprites' group in the main function
    def __init__(self):
        super().__init__()
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.speed = SCROLLING_SPEED

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


class PowerUp(FallingItem):
    """Sprite for falling powerup items. See base class."""
    def __init__(self):
        super().__init__()
        self.image, self.rect = main.load_image('powerup.png', colorkey=-1, scale=(25, 25))


class HpPack(FallingItem):
    """Sprite for falling HP packs. See base class."""
    def __init__(self):
        super().__init__()
        self.image, self.rect = main.load_image('hp_pack.png', colorkey=-1, scale=(25, 25))


class HpBar():
    def __init__(self, tracking_object: Plane):
        self.tracking_object = tracking_object
        self.screen = pygame.display.get_surface()
        self.width = 160
        self.height = 15
        self.x = 5
        self.y = 620

    def draw(self):
        pygame.draw.rect(self.screen, (0, 0, 150),
                         [self.x - 3, self.y - 3, self.width + 6, self.height + 6])
        pygame.draw.rect(self.screen, (130, 0, 0),
                         [self.x, self.y, self.width, self.height])
        pygame.draw.rect(self.screen, (200, 0, 0),
                         [self.x, self.y, self.tracking_object.hp, self.height])


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
        self.fire_count_down = 0
        self.fire_cycle = ENEMY_FIRE_PERIOD

    def revival(self):
        Enemy.initial_hp += 10
        self.hp = self.initial_hp

    def appearnce(self):
        # Change image to the next
        self.image = self.all_images[self.number_appear - 1]

        self.radius = max(self.rect.width, self.rect.height)
        self.rect.left = random.randrange(self.area.width - self.rect.width)
        self.rect.top = self.area.top
        if self.number_appear == 4:
            self.speed = 1
        if self.number_appear == 0:
            self.speed = 1
        if self.number_appear == 4 or self.number_appear == 0:
            self.fire_cycle = 2*ENEMY_FIRE_PERIOD
        else:
            self.fire_cycle = ENEMY_FIRE_PERIOD


    def update(self):
        if not self.frame % 80:  # 讓敵人可以隨機左右移動
            if random.randrange(2) == 0:
                self.direction *= -1
        self.frame += 1
        self.rect = self.rect.move(0.5 * self.direction * self.speed, 1.5 * self.speed)

        if not (self.area.right >= self.rect.right and self.rect.left >= self.area.left):
            self.direction *= -1

        if self.hp <= 0:
            ExplosionEnemy.position(self.rect.center)
            self.kill()

        if self.rect.bottom > self.area.bottom:
            self.kill()
        if self.missile_number > 0 and self.fire_count_down == 0:
            self._fire()
        if self.fire_count_down > 0:
            self.fire_count_down -= 1
        if self.speed == 0 and self.missile_number == 0:
            self.speed = 2


    def fire(self):
        if not self.frame % self.fire_cycle:
            if self.number_appear == 0:
                self.missile_number = 5
            elif self.number_appear == 4:
                self.missile_number = 5
            else:
                self.missile_number = 3
            self._fire()

    def _fire(self):
        if self.missile_number > 0:
            if self.number_appear == 0:
                n = 6
                for i in range(n):
                    vector = (math.cos(2*math.pi*i/n),
                              math.sin(2*math.pi*i/n))
                    EnemyMissile.position([int(round(x + dx*self.radius)) for x, dx in zip(self.rect.center, vector)],
                                          direction=vector)

                self.fire_count_down = int(0.5*FIRE_WAIT)
            elif self.number_appear == 4:
                n = 6
                for i in range(n):
                    vector = (math.cos(2*math.pi*i/n),
                              math.sin(2*math.pi*i/n))
                    vector2 = (math.cos(2*math.pi*(i/n) + self.missile_number*2/(n+1)),
                               math.sin(2*math.pi*(i/n) + self.missile_number*2/(n+1)))
                    position = [int(round(x + dx*self.radius)) for x, dx in zip(self.rect.center, vector2)]
                    EnemyMissile.position(position, direction=vector)

                self.fire_count_down = int(0.5*FIRE_WAIT)

            else:
                EnemyMissile.position(self.rect.midbottom)
                self.fire_count_down = FIRE_WAIT
            self.missile_number -= 1


# 魔王本身設定
class Boss(pygame.sprite.Sprite):
    initial_hp = HP_BOSS
    all_images = []
    def __init__(self):
        super(Boss, self).__init__()
        self.image = self.all_images[0]
        self.rect = self.image.get_rect()
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.radius = max(self.rect.width, self.rect.height) / 2
        self.speed = 1.5
        self.rect.left = random.randrange(self.area.width - self.rect.width)
        self.rect.top = self.area.top
        self.hp = HP_BOSS
        self.direction = 1
        self.number_appear = 1
        self.missile_number = 0
        self.fire_count_down = 0
        self.firing_dir = 1


    def revival(self):
        Boss.initial_hp += 80
        self.hp = self.initial_hp


    def appearnce(self):
        self.image = self.all_images[self.number_appear % 5 -1]
        self.rect = self.image.get_rect()

        self.rect.left = random.randrange(self.area.width - self.rect.width)
        self.rect.top = self.area.top


    def update(self):
        self.rect = self.rect.move(self.direction * self.speed, 0)

        if not (self.area.right >= self.rect.right and self.rect.left >= self.area.left):
            self.direction *= -1
        if self.missile_number > 0 and self.fire_count_down == 0:
            self._fire()
        if self.fire_count_down > 0:
            self.fire_count_down -= 1
        if self.speed == 0 and self.missile_number == 0:
            self.speed = 1.5

    def die(self):
        ExplosionBoss.position(self.rect.center)
        self.kill()

    def fire(self):
        if self.missile_number > 0:
            return
        if self.number_appear == 1:
            self.firing_dir *= -1
            self.missile_number = 20
            # self.speed = 0
        else:
            self.missile_number = 1
        self._fire()

    def _fire(self):
        if self.number_appear == 1:
            vector = (self.firing_dir*math.cos(math.pi*(0.8*self.missile_number/20 + 0.1)),
                      math.sin(math.pi*(0.8*self.missile_number/20 + 0.1)))
            EnemyMissile.position(self.rect.midbottom,
                                  direction=vector)

            self.fire_count_down = int(0.3*FIRE_WAIT)
        else:
            EnemyMissile.position(self.rect.midbottom, 3)
        self.missile_number -= 1


# 敵人射出的飛彈
class EnemyMissile(pygame.sprite.Sprite):
    pool = pygame.sprite.Group()
    active = pygame.sprite.Group()

    def __init__(self):
        super().__init__()
        self.image, self.rect = main.load_image('bullet_enemy.png', colorkey=-1, scale=(5, 21))
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.speed = 4
        self.direction = (0, 1)

    @classmethod
    def position(cls, location: Tuple[int, int], num: int = 1, direction: Tuple[int, int] = (0, 1)):
        if len(cls.pool) < num:
            cls.pool.add([EnemyMissile() for _ in range(num)])
        x_all = ((-(num-1)/2 + i)*30 for i in range(num))
        for x in x_all:
            missile = cls.pool.sprites()[0]
            missile.add(cls.allsprites, cls.active)
            missile.remove(cls.pool)
            missile.rect.bottom = location[1]
            missile.rect.centerx = int(x + location[0])
            missile.direction = direction

    def recycle(self):
        self.add(self.pool)
        self.remove(self.allsprites, self.active)

    def update(self):
        self.rect = self.rect.move([int(round(d*self.speed)) for d in self.direction])
        if self.rect.bottom > self.area.bottom:
            self.recycle()


# 死掉時的爆炸畫面
class ExplosionEnemy(pygame.sprite.Sprite):
    pool = pygame.sprite.Group()
    active = pygame.sprite.Group()

    def __init__(self):
        super().__init__()
        self.explode_image, _ = main.load_image('enemy_ex.png', colorkey=-1, scale=(32, 34))
        self.ash_image, self.rect = main.load_image('enemy_ash.png', colorkey=-1, scale=(32, 34))
        self.image = self.explode_image
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.speed = 2
        self.remaining_time = 0
        self.wait = 7

    @classmethod
    def position(cls, location: Tuple[int, int], num: int = 1):
        if len(cls.pool) < num:
            cls.pool.add([cls() for _ in range(num)])
        explosion = cls.pool.sprites()[0]
        explosion.add(cls.allsprites, cls.active)
        explosion.remove(cls.pool)
        explosion.rect.center = location
        explosion.image = explosion.explode_image
        explosion.remaining_time = explosion.wait


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


class ExplosionBoss(pygame.sprite.Sprite):
    pool = pygame.sprite.Group()
    active = pygame.sprite.Group()

    def __init__(self):
        super().__init__()
        self.explode_image, _ = main.load_image('enemy_ex.png', colorkey=-1, scale=(96, 102))
        self.ash_image, self.rect = main.load_image('enemy_ash.png', colorkey=-1, scale=(96, 102))
        self.image = self.explode_image
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.speed = 2
        self.remaining_time = 0
        self.wait = 10

    @classmethod
    def position(cls, location: Tuple[int, int], num: int = 1):
        if len(cls.pool) < num:
            cls.pool.add([cls() for _ in range(num)])
        explosion = cls.pool.sprites()[0]
        explosion.add(cls.allsprites, cls.active)
        explosion.remove(cls.pool)
        explosion.rect.center = location
        explosion.image = explosion.explode_image
        explosion.remaining_time = explosion.wait

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


class Button(object):
    def __init__(self, image1, image2, position, status=False):
        self.imageUp, _ = main.load_image(image1)
        self.imageDown, _ = main.load_image(image2)
        self.position = position
        self.status = False

    def isOver(self):
        point_x, point_y = pygame.mouse.get_pos()
        x, y = self. position
        w, h = self.imageUp.get_size()

        in_x = x - w/2 < point_x < x + w/2
        in_y = y - h/2 < point_y < y + h/2
        return in_x and in_y

    def render(self, screen):
        w, h = self.imageUp.get_size()
        x, y = self.position

        if self.isOver():
            screen.blit(self.imageDown, (int(x-w/2), int(y-h/2)))
            if pygame.mouse.get_pressed()[0]:
                self.status = True
        else:
            screen.blit(self.imageUp, (int(x-w/2), int(y-h/2)))
