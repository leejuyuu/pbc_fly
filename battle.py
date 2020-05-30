"""
This module handles all battle mechanisms.
"""
import pygame


class Plane(pygame.sprite.Sprite):
    pass



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
            # elif event.type == MOUSEBUTTONDOWN:
            #     if fist.punch(chimp):
            #         punch_sound.play()  # punch
            #         chimp.punched()
            #     else:
            #         whiff_sound.play()  # miss
            # elif event.type == MOUSEBUTTONUP:
            #     fist.unpunch()

            # allsprites.update()

            # Draw Everything
            screen.blit(background, (0, 0))
            # allsprites.draw(screen)
            pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    main()
