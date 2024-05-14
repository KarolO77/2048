from settings import *
from game import Game
import os

class Main:
    def __init__(self):

        # general
        pygame.init()
        pygame.display.set_caption("2048")
        self.display_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        # components
        self.game = Game()

    def run(self):
        while True:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            # game
            self.game.run()

            # updating the game
            self.clock.tick(60)
            pygame.display.update()


if __name__ == "__main__":
    main = Main()
    main.run()