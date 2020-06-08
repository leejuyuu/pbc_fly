"""
This module handles all battle mechanisms.
"""
from pathlib import Path
import random
from typing import Tuple
import pygame
import enemy


INITIAL_HP = 160
HP_INCREMENT = 10
HP_PACK_PROB = 0.001
POWER_UP_PROB = 0.001
HIT_HP_DROP = 10
COLLIDE_HP_DROP = 20
IMG_DIR = Path(__file__).resolve().parent / 'img'

# functions to create our resources
def load_image(name, colorkey=None, scale=None):
    path = IMG_DIR / name
    try:
        image = pygame.image.load(str(path))
    except pygame.error:
        print("Cannot load image:", path)
        raise SystemExit(str(pygame.compat.geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)
    if scale is not None:
        image = pygame.transform.scale(image, scale)
    return image, image.get_rect()

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
        self.speed = 1
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
    """Sprite for falling powerup items. See base class."""
    def __init__(self):
        super().__init__()
        self.image, self.rect = load_image('powerup.png', colorkey=-1, scale=(25, 25))


class HpPack(FallingItem):
    """Sprite for falling HP packs. See base class."""
    def __init__(self):
        super().__init__()
        self.image, self.rect = load_image('hp_pack.png', colorkey=-1, scale=(25, 25))


def main():
    """This is the main function."""
    pygame.init()
    screen = pygame.display.set_mode((480, 640))
    pygame.display.set_caption('pbc fly')
    pygame.mouse.set_visible(0)

    background, _ = load_image('skybackground.jpg', scale=(480, 640))
    background1_rect = pygame.Rect(0, 0, 480, 640)
    background2_rect = pygame.Rect(0, 0, 480, 640)

    barW = 160
    barH = 15
    bloodx = 5
    bloody = 620

    score = 0
    score_font = pygame.font.SysFont('arial', 25)

    plane = Plane()
    allsprites = pygame.sprite.RenderPlain((plane))
    # Create 10 missiles and store them in the class variable pool
    Missile.pool = pygame.sprite.Group([Missile() for _ in range(10)])
    Missile.allsprites = allsprites
    FallingItem.allsprites = allsprites

    enemy.Enemy_Missile.pool = pygame.sprite.Group([enemy.Enemy_Missile() for _ in range(10)])
    enemy.Enemy_Missile.allsprites = allsprites
    enemies = pygame.sprite.Group()

    # Add boss group
    enemy.Boss_Missile.pool = pygame.sprite.Group([enemy.Boss_Missile() for _ in range(10)])
    enemy.Boss_Missile.allsprites = allsprites
    bosses = pygame.sprite.Group()

    hp_pack = HpPack()
    powerup = PowerUp()
    fire_period = 20
    enemy_fire_period = 120
    fire_wait = 20
    clock = pygame.time.Clock()

    frame = 0
    while True:
        frame += 1  # Loop counter
        clock.tick(60)  # Max FPS = 60

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

        score += 1/30
        background1_rect.y += 1
        if background2_rect.y + background1_rect.y > 640:
            background1_rect.y = 0
        background2_rect.bottom = background1_rect.y

        plane.key_pressed()

        # The plane fires every constant period (frames)
        if not frame % fire_period:
            plane.fire()

        # Randomly put a powerup item on the top of the screen if it is not
        # already on the screen
        if powerup not in allsprites and random.random() <= POWER_UP_PROB:
            powerup.appear()

        # Randomly put a HP pack item on the top of the screen if it is not
        # already on the screen
        if hp_pack not in allsprites and random.random() <= HP_PACK_PROB:
            hp_pack.appear()

        # Enemy's apperance
        if not frame % 100:
            new_enemy = enemy.Enemy()
            new_enemy.add(allsprites, enemies)

        # Enemy fires missile
        if not frame % enemy_fire_period:
            for a_enemy in enemies:
                if not a_enemy.missile_number:
                    a_enemy.missile_number = 3

        if not frame % fire_wait:
            for a_enemy in enemies:
                if a_enemy.missile_number:
                    a_enemy.missile_number -= 1
                    enemy.Enemy_Missile.position(a_enemy.rect.midbottom)

        # Increase missiles fired at once if collided with powerup item
        if powerup in allsprites and pygame.sprite.collide_rect(plane, powerup):
            plane.powerup()
            powerup.kill()

        # Recover HP if collided with HP pack item
        if hp_pack in allsprites and pygame.sprite.collide_rect(plane, hp_pack):
            plane.hp += HP_INCREMENT
            hp_pack.kill()

        # Boss' apperance 
        if frame == 100:
            new_boss = enemy.Boss()
            new_boss.add(allsprites, bosses)

        # Boss fires missile
        if not frame % enemy_fire_period:
            for a_boss in bosses:
                enemy.Boss_Missile.position(a_boss.rect.midbottom, 5)
    
        # Check if enemy collide with our plane
        for a_enemy in enemies:
            if pygame.sprite.collide_circle(plane, a_enemy):
                plane.hp -= COLLIDE_HP_DROP
                plane.remove_powerup()
                a_enemy.kill()


        # Check if enemy's missile hit our plane
        for missile in enemy.Enemy_Missile.active:
            if pygame.sprite.collide_circle(plane, missile):
                missile.recycle()
                plane.hp -= HIT_HP_DROP
                plane.remove_powerup()

 
        # Check if our plane's missile hit enemy 
        for missile in Missile.active:
            for a_enemy in enemies:
                if pygame.sprite.collide_circle(a_enemy, missile):
                    missile.recycle()
                    a_enemy.hp -= HIT_HP_DROP
                if a_enemy.hp <= 0:
                     a_enemy.kill()
                   

        # # Check if boss collide with our plane
        # for a_boss in bosses:
        #     if pygame.sprite.collide_circle(plane, a_boss):
        #         plane.hp -= COLLIDE_HP_DROP
        #         plane.remove_powerup()
        #         a_boss.kill()


        # Check if our plane's missile hit boss 
        for missile in Missile.active:
            for a_boss in bosses:
                if pygame.sprite.collide_circle(a_boss, missile):
                    missile.recycle()
                    a_boss.hp -= HIT_HP_DROP
                if a_boss.hp <= 0:
                     a_boss.kill()
                    
        # End the game if the HP goes to 0
        if plane.hp <= 0:
            break

        allsprites.update()
        score_text = score_font.render('Score : %s' % str(score), True, (225, 225, 225))

        # Draw Everything
        screen.blit(background, (0, background1_rect.y))
        screen.blit(background, (0, background2_rect.y))
        pygame.draw.rect(screen, (0, 0, 150), [bloodx - 3, bloody - 3, INITIAL_HP + 6, barH + 6])
        pygame.draw.rect(screen, (130, 0, 0), [bloodx, bloody, INITIAL_HP, barH])
        pygame.draw.rect(screen, (200, 0, 0), [bloodx, bloody, plane.hp, barH])
        screen.blit(score_text, (10, 5))
        allsprites.draw(screen)
        pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    main()
