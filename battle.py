"""
This module handles all battle mechanisms.
"""
from pathlib import Path
import random
from typing import Tuple
import pygame

INITIAL_HP = 100
HP_INCREMENT = 10
HP_PACK_PROB = 0.001
POWER_UP_PROB = 0.001
IMG_DIR = Path(__file__).resolve().parent / 'img'
print(__file__)
print(IMG_DIR)
# functions to create our resources
def load_image(name, colorkey=None):
    fullname = IMG_DIR / name
    try:
        image = pygame.image.load(str(fullname))
    except pygame.error:
        print("Cannot load image:", fullname)
        raise SystemExit(str(pygame.compat.geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)
    return image, image.get_rect()

class Plane(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image, self.rect = load_image('plane.png')

        self.screen = pygame.display.get_surface()
        self.area = self.screen.get_rect()
        # Put the rect at the bottom of the screen
        self.rect.midbottom = (self.screen.get_width() // 2, self.area.bottom - self.screen.get_height() * 0.05)
        self.radius = max(self.rect.width, self.rect.height)
        self.alive = True
        self.vert = 0
        self.horiz = 0
        self.speed = 1
        self.hp = INITIAL_HP

    def key_pressed(self):
        keys_pressed = pygame.key.get_pressed()
        self.vert = 0
        self.horiz = 0
        if keys_pressed[pygame.K_LEFT]:
            self.horiz = -2 * self.speed
        if keys_pressed[pygame.K_RIGHT]:
            self.horiz = 2 * self.speed

    def move(self, diff: int):
        self.horiz = diff

    def update(self):
        new_rect = self.rect.move((self.horiz, self.vert))

        if not self.area.contains(new_rect):
            if new_rect.left < self.area.left:
                new_rect.left = self.area.left
            elif new_rect.right > self.area.right:
                new_rect.right = self.area.right
        self.rect = new_rect

        if self.hp > INITIAL_HP:
            self.hp = INITIAL_HP


class Missile(pygame.sprite.Sprite):
    pool = pygame.sprite.Group()
    active = pygame.sprite.Group()

    def __init__(self):
        super().__init__()
        self.image, self.rect = load_image('bullet.png')
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.speed = 10

    @classmethod
    def position(cls, location: Tuple[int, int], num: int = 1):
        if len(cls.pool) < num:
            cls.pool.add([Missile() for _ in range(num)])
        x_all = ((-(num-1)/2 + i)*50 for i in range(num))
        for x in x_all:
            missile = cls.pool.sprites()[0]
            missile.add(cls.allsprites, cls.active)
            missile.remove(cls.pool)
            missile.rect.bottom = location[1]
            missile.rect.x = x + location[0]

    def recycle(self):
        self.add(self.pool)
        self.remove(self.allsprites, self.active)

    def update(self):
        self.rect = self.rect.move(0, -1 * self.speed)
        if self.rect.top < self.area.top:
            self.recycle()


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

class PowerUp(FallingItem):
    def __init__(self):
        super().__init__()
        self.image, self.rect = load_image('powerup.png')


class HpPack(FallingItem):
    def __init__(self):
        super().__init__()
        self.image, self.rect = load_image('hp_pack.png')


def main():
    pygame.init()
    screen = pygame.display.set_mode((480, 640))
    pygame.display.set_caption('pbc fly')
    pygame.mouse.set_visible(0)

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))

    plane = Plane()
    allsprites = pygame.sprite.RenderPlain((plane))
    # Create 10 missiles and store them in the class variable pool
    Missile.pool = pygame.sprite.Group([Missile() for _ in range(10)])
    Missile.allsprites = allsprites
    FallingItem.allsprites = allsprites
    hp_pack = HpPack()
    powerup = PowerUp()
    fire_period = 20
    clock = pygame.time.Clock()

    n_missile = 1
    frame = 0
    while True:
        frame += 1
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

        plane.key_pressed()
        if not frame % fire_period:
            Missile.position(plane.rect.midtop, n_missile)

        if powerup not in allsprites and random.random() <= POWER_UP_PROB:
            powerup.appear()

        if hp_pack not in allsprites:
            if random.random() <= HP_PACK_PROB:
                hp_pack.appear()

        allsprites.update()

        if powerup in allsprites and pygame.sprite.collide_rect(plane, powerup):
            n_missile += 1
            powerup.kill()

        if hp_pack in allsprites and pygame.sprite.collide_rect(plane, hp_pack):
            plane.hp += HP_INCREMENT
            hp_pack.kill()

        allsprites.update()

        # Draw Everything
        screen.blit(background, (0, 0))
        allsprites.draw(screen)
        pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    main()
