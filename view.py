# 創建遊戲主窗口
# 背景
import pygame
from enemy import *
from rocket import *

pygame.init()

screen = pygame.display.set_mode((480, 700))
background = pygame.image.load("C:/Users/user/Desktop/skybackground.jpg")
background = pygame.transform.scale(background, (480, 700))
screen.blit(background, (0, 0))

# rocket
player_rocket = rocketsprite("C:/Users/user/Desktop/rocket.png", 8)
player_rocket_group = pygame.sprite.Group(player_rocket)

# 血條 
barW = 160
barH = 15
bloodx = 5 
bloody = 680
pygame.display.update()

# 背景移動
background1_rect = pygame.Rect(0, 0, 480, 700)
background2_rect = pygame.Rect(0, 0, 480, 700)

# 創建敵機的精靈
enemy = GameSprite("C:/Users/user/Desktop/airplane.png")
# 創建敵機的精靈組
enemy_group = pygame.sprite.Group(enemy)


clock = pygame.time.Clock()
run = True
while run :
  # 防止cpu佔用過高
  pygame.time.delay(20)
  for event in pygame.event.get() :
    if event.type == pygame.QUIT :
      run = False
  # 可以指定循環體內部的代碼執行的頻率
  clock.tick(60)
  # 更新背景1
  background1_rect.y += 1
  # 如果背景移出屏幕，則將背景1移動到屏幕頂部
  if background2_rect.y + background1_rect.y > 700 :
    background1_rect.y = 0 
  # 背景2的尾要接在背景1的頭上
  background2_rect.bottom = background1_rect.y
  # 繪製背景圖片
  screen.blit(background, (0, background1_rect.y))
  screen.blit(background, (0, background2_rect.y))
  # 戰鬥機
  player_rocket.update()
  player_rocket_group.draw(screen)
  # 繪製血條
  pygame.draw.rect(screen, (0, 0, 150), [bloodx - 3 , bloody - 3, barW + 6, barH + 6])
  pygame.draw.rect(screen, (130, 0, 0), [bloodx , bloody, barW, barH])
  pygame.draw.rect(screen, (200, 0, 0), [bloodx , bloody, barW, barH])
  # 讓精靈組調用兩個方法
  # update - 讓組中的所有精靈更新位置
  enemy_group.update()
  # draw - 在screen上繪製所有的精靈
  enemy_group.draw(screen)
  
  pygame.display.update()

pygame.quit()
