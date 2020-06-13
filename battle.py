
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
IMG_DIR = Path(__file__).resolve().parent / 'img'
SOUND_DIR = Path(__file__).resolve().parent / 'sound'


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

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer:
        return NoneSound()
    path = SOUND_DIR / name
    try:
        sound = pygame.mixer.Sound(str(path))
    except pygame.error as message:
        print('Cannot load sound:', name)
        raise SystemExit(message)
    return sound

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
  def __init__(self, image1, image2,position):
    self.imageUp, ___ = load_image(image1)
    self.imageDown, ____ = load_image(image2)
    #self.imageUp = pygame.transform.scale(init_image1, (210, 70))
    #self.imageDown =  pygame.transform.scale(init_image2, (210, 70))
    self.position = position
  
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
        screen.blit(self.imageDown, (x-w/2,y-h/2))
    else:
        screen.blit(self.imageUp, (x-w/2, y-h/2))


def main():
    """This is the main function."""
    pygame.init()
    if not pygame.mixer:
        print('Warning: Sound disabled')
    music = load_sound('Africa.wav')
    music.set_volume(0.05)
    screen = pygame.display.set_mode((480, 640))
    pygame.display.set_caption('pbc fly')
    pygame.mouse.set_visible(0)

    background, _ = load_image('skybackground.jpg', scale=(480, 640))
    background1_rect = pygame.Rect(0, 0, 480, 640)
    background2_rect = pygame.Rect(0, 0, 480, 640)


    score = 0
    score_font = pygame.font.SysFont('arial', 25)

    again_button = Button('game_again.png', 'game_again_down.png', (240, 390))
    leave_button = Button('leave_game.png', 'leave_game_down.png', (240, 480))

    plane = Plane()
    allsprites = pygame.sprite.RenderPlain((plane))
    # Create 10 missiles and store them in the class variable pool
    Missile.pool = pygame.sprite.Group([Missile() for _ in range(10)])
    Missile.allsprites = allsprites
    FallingItem.allsprites = allsprites

    enemy.Enemy_Missile.pool = pygame.sprite.Group([enemy.Enemy_Missile() for _ in range(10)])
    enemy.Enemy_Missile.allsprites = allsprites
    enemies = pygame.sprite.Group()
    enemy.ExplosionEnemy.allsprites = allsprites
    enemy.ExplosionBoss.allsprites = allsprites
    enemy.Enemy.all_images = [load_image('enemy{}.png'.format(i),
                                         colorkey=-1,
                                         scale=(32, 34))[0] for i in range(1, 6)]

    # Add boss group
    bosses = pygame.sprite.Group()
   

    hp_pack = HpPack()
    powerup = PowerUp()
    hp_bar = HpBar(plane)
    fire_period = 20
    enemy_fire_period = 120
    boss_fire_period = 70
    fire_wait = 25


    mark = False # to identify whether enemy adds hp after 1 boss is defeated (enemy level up)
    initial_boss_appear = True # to identify the first appearance of boss
    boss_number_appear = 1 # the number of boss that has appeared including this one

    frame_record = int()


    clock = pygame.time.Clock()
    frame = 0

    while True:
        music.play(loops=-1)
        frame += 1  # Loop counter
        score += 1/30
        clock.tick(60)  # Max FPS = 60

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

        background1_rect.y += SCROLLING_SPEED
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


        # Enemy's appearnce
        if not frame % 100:
            if len(bosses) == 0:
                new_enemy = enemy.Enemy()
                new_enemy.number_appear = boss_number_appear % 5
                new_enemy.appearnce() # determine the image it appears

                if mark: # enemy's hp increases since player has entered next level
                    new_enemy.revival()
                    mark = False
                new_enemy.add(allsprites, enemies)


        # Enemy fires missile
        if not frame % enemy_fire_period:
            for a_enemy in enemies:
                a_enemy.fire()

        # Increase missiles fired at once if collided with powerup item
        if powerup in allsprites and pygame.sprite.collide_rect(plane, powerup):
            plane.powerup()
            powerup.kill()

        # Recover HP if collided with HP pack item
        if hp_pack in allsprites and pygame.sprite.collide_rect(plane, hp_pack):
            plane.hp += HP_INCREMENT
            hp_pack.kill()

        # Another boss appears 25 seconds after the previous one is defeated
        if frame == frame_record + 1500:
            new_boss = enemy.Boss()
            new_boss.number_appear = boss_number_appear
            new_boss.appearnce() # determine the image it appears

            if not initial_boss_appear: # Boss has already appeared more than 1 time
                new_boss.revival() # boss' hp increases
            new_boss.add(allsprites, bosses)

        # Boss fires missile
        if not frame % boss_fire_period:
            for a_boss in bosses:
                enemy.Enemy_Missile.position(a_boss.rect.midbottom, 3)

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
                    score += 40


        # Check if boss collide with our plane
        for a_boss in bosses:
            if pygame.sprite.collide_circle(plane, a_boss):
                plane.hp -= COLLIDE_HP_DROP
                plane.remove_powerup()


        # Check if our plane's missile hit boss
        for missile in Missile.active:
            for a_boss in bosses:
                if pygame.sprite.collide_circle(a_boss, missile):
                    missile.recycle()
                    a_boss.hp -= HIT_HP_DROP
                if a_boss.hp <= 0:
                    score += 200
                    a_boss.die()
                    mark = True # player entering next level
                    initial_boss_appear = False # launch revival method every time a new boss appears
                    boss_number_appear += 1
                    frame_record = frame # to record the number of frames when a boss is defeated


        # End the game if the HP goes to 0
        if plane.hp <= 0:
            screen.blit(background, (0, background1_rect.y))
            screen.blit(background, (0, background2_rect.y))
            again_button.render(screen)
            leave_button.render(screen)
            pygame.display.update()

        allsprites.update()
        score_text = score_font.render('Score : %6d' % score, True, (225, 225, 225))

        # Draw Everything
        if plane.hp > 0 :
           screen.blit(background, (0, background1_rect.y))
           screen.blit(background, (0, background2_rect.y))
           hp_bar.draw()
           screen.blit(score_text, (10, 5))
           allsprites.draw(screen)
           pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    main()
