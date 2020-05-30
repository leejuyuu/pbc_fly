"""
This module handles all battle mechanisms.
"""
from pathlib import Path
import pygame

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
    clock = pygame.time.Clock()

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

        plane.key_pressed()

        allsprites.update()

        # Draw Everything
        screen.blit(background, (0, 0))
        allsprites.draw(screen)
        pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    main()
