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

        allsprites.update()

        # Draw Everything
        screen.blit(background, (0, 0))
        allsprites.draw(screen)
        pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    main()
