
"""
This module handles all battle mechanisms.
"""
from pathlib import Path
import random
from typing import Tuple
import pygame
import enemy


# Constants to control gameplay and hardness
SCROLLING_SPEED = 2
INITIAL_HP = 160
HP_INCREMENT = 40
HP_PACK_PROB = 0.001
POWER_UP_PROB = 0.001
HIT_HP_DROP = 10
COLLIDE_HP_DROP = 20



class Plane(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.all_images = [load_image('plane_lv{}.png'.format(i),
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
        self.image, self.rect = load_image('bullet.png', colorkey=-1, scale=(5, 20))
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
        self.image, self.rect = load_image('powerup.png', colorkey=-1, scale=(25, 25))


class HpPack(FallingItem):
    """Sprite for falling HP packs. See base class."""
    def __init__(self):
        super().__init__()
        self.image, self.rect = load_image('hp_pack.png', colorkey=-1, scale=(25, 25))


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


class Button(object) :
  def __init__(self, image1, image2, position, status = False):
    self.imageUp, ___ = load_image(image1)
    self.imageDown, ____ = load_image(image2)
    self.position = position
    self.status = False
  
  def isOver(self):
    point_x,point_y = pygame.mouse.get_pos()
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
        if pygame.mouse.get_pressed()[0] == True :
            self.status = True
    else:
        screen.blit(self.imageUp, (int(x-w/2), int(y-h/2)))


