
from pathlib import Path
import random
import pygame
import sprites


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

    background, _ = load_image('background1.png', scale=(480, 640))
    background1_rect = pygame.Rect(0, 0, 480, 640)
    background2_rect = pygame.Rect(0, 0, 480, 640)


    score = 0
    score_font = pygame.font.SysFont('arial', 25)

    again_button = sprites.Button('game_again.png', 'game_again_down.png', (240, 390))
    leave_button = sprites.Button('leave_game.png', 'leave_game_down.png', (240, 480))
    gameover_image, _ = load_image('gameover.png', scale=(400, 150))

    plane = sprites.Plane()
    allsprites = pygame.sprite.RenderPlain((plane))
    # Create 10 missiles and store them in the class variable pool
    sprites.Missile.pool = pygame.sprite.Group([sprites.Missile() for _ in range(10)])
    sprites.Missile.allsprites = allsprites
    sprites.FallingItem.allsprites = allsprites

    sprites.Enemy_Missile.pool = pygame.sprite.Group([sprites.Enemy_Missile() for _ in range(10)])
    sprites.Enemy_Missile.allsprites = allsprites
    enemies = pygame.sprite.Group()
    sprites.ExplosionEnemy.allsprites = allsprites
    sprites.ExplosionBoss.allsprites = allsprites
    sprites.Enemy.all_images = [load_image('enemy{}.png'.format(i),
                                         colorkey=-1,
                                         scale=(32, 34))[0] for i in range(1, 6)]

    # Add boss group
    bosses = pygame.sprite.Group()
    sprites.Boss.all_images = [load_image('boss{}.png'.format(i),
                                        colorkey=-1,
                                        scale=(96, 102))[0] for i in range(1, 6)]

    hp_pack = sprites.HpPack()
    powerup = sprites.PowerUp()
    hp_bar = sprites.HpBar(plane)
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

        pygame.mouse.set_visible(True)

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
                new_enemy = sprites.Enemy()
                new_enemy.number_appear = boss_number_appear % 5
                new_enemy.appearnce() # determine the image it appears

                if mark: # enemy's hp increases since player has entered next level
                    new_enemy.revival()
                    mark = False
                new_enemy.add(allsprites, enemies)


        # Enemy fires missile
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
            new_boss = sprites.Boss()
            new_boss.number_appear = boss_number_appear % 5
            new_boss.appearnce() # determine the image it appears

            if not initial_boss_appear: # Boss has already appeared more than 1 time
                new_boss.revival() # boss' hp increases
            new_boss.add(allsprites, bosses)

        # Boss fires missile
        if not frame % boss_fire_period:
            for a_boss in bosses:
                a_boss.fire()

        # Check if enemy collide with our plane
        for a_enemy in enemies:
            if pygame.sprite.collide_circle(plane, a_enemy):
                plane.hp -= COLLIDE_HP_DROP
                plane.remove_powerup()
                a_enemy.kill()


        # Check if enemy's missile hit our plane
        for missile in sprites.Enemy_Missile.active:
            if pygame.sprite.collide_circle(plane, missile):
                missile.recycle()
                plane.hp -= HIT_HP_DROP
                plane.remove_powerup()

        # Check if our plane's missile hit enemy
        for missile in sprites.Missile.active:
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
        for missile in sprites.Missile.active:
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
            screen.blit(gameover_image, (40, 150))
            again_button.render(screen)
            leave_button.render(screen)
            if again_button.status == True :
                main()
            if leave_button.status == True :
                break
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
