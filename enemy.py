"""
敵人機制
"""
import pygame 
from typing import Tuple
import battle
import random

INITIAL_HP_ENEMY = 80

class Enemy(pygame.sprite.Sprite):

    def __init__(self):
        super(Enemy, self).__init__()
        self.image, self.rect = battle.load_image('enemy1.png', colorkey=-1, scale=(32, 34))

        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.radius = max(self.rect.width, self.rect.height)
        self.speed = 1
        self.rect.left = random.randrange(self.area.width - self.rect.width)
        self.rect.top = self.area.top
        self.hp = INITIAL_HP_ENEMY


    def update(self):
        self.rect = self.rect.move(0, 1 * self.speed)
        if self.rect.bottom > self.area.bottom:
            self.kill()


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
            print(456)
            missile = cls.pool.sprites()[0]
            missile.add(cls.allsprites, cls.active)
            missile.remove(cls.pool)
            missile.rect.bottom = location[1]
            missile.rect.centerx = int(x + location[0])

    def recycle(self):
        self.add(self.pool)
        self.remove(self.allsprites, self.active)

    def update(self):
        self.rect = self.rect.move(0, 2 * self.speed)
        if self.rect.bottom > self.area.bottom:
            self.recycle()

# class FallingItem(pygame.sprite.Sprite):
#     allsprites = None
#     def __init__(self):
#         super().__init__()
#         screen = pygame.display.get_surface()
#         self.area = screen.get_rect()
#         self.speed = 1

#     def appear(self, position: int = None):
#         self.rect.top = self.area.top
#         if position is None:
#             self.rect.left = random.randrange(self.area.width - 2 * self.rect.width)
#         else:
#             self.rect.x = position
#         self.add(self.allsprites)

#     def update(self):
#         self.rect = self.rect.move(0, 1 * self.speed)
#         if self.rect.bottom > self.area.bottom:
#             self.kill()




# for i in range(60):
# 	enemy = Enemy((random.randrange(0, WIDTH), random.randrange(0,50)))
# 	enemy_sprites.add(enemy)
# 	all_sprites.add(enemy)

# # 子彈擊毀敵艦
# bullet_collide_dic = pygame.sprite.groupcollide(bullet_sprites, enemy_sprites, True, True)
# for bullet in bullet_collide_dic:
#     print(bullet, bullet_collide_dic)


# # 遊戲結束的情形（敵艦撞機）
# self.rect.x = self.bg_size[0]/2
# self.rect.y = self.bg_size[-1]
# self.rect.height

# if pygame.sprite.spritecollideany(plane, enemy_sprites) is not None:
#     print('killed')
#     running = False

# # 批量化出現敵艦
# init_enemy(ENEMY_SIZE)

# # 增加敵艦
# if len(enemy_group) <= ENEMY_MIN_SIZE:
#     init_enemy(ENEMY_SIZE - len(enemy_group))



# pygame.display.update()

# pygame.quit()
 
