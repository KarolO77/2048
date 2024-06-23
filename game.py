from settings import *
from timer import Timer
from button import Button
from random import randrange, choice
import math

# ctrl k, ctrl j - unfold all
# ctrl k, ctrl m - fold 2


class Game:
    def __init__(self) -> None:

        # general
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.display_surface = pygame.display.get_surface()

        # game status
        self.finished = False
        self.won = False

        # tiles
        self.tiles = {
            pos: Tile(2, pos) for pos in [self.get_random_pos() for _ in range(2)]
        }

        # "try again" button
        self.try_again_img = pygame.image.load("tryagain.jpg")
        self.try_again_bttn = Button(
            pos=(SCREEN_WIDTH//2, SCREEN_HEIGHT*0.6),
            image=self.try_again_img,
            text="TRY AGAIN"
        )
        self.bttn_txt_surface = BUTTON_FONT.render(
                self.try_again_bttn.text,
                True,
                TEXT_COLOR
            )
        self.bttn_txt_rect = self.bttn_txt_surface.get_rect(center=self.try_again_bttn.pos)

        # timer
        self.key_timer = Timer(KEY_WAIT_TIME)
        self.mouse_timer = Timer(MOUSE_WAIT_TIME)

    # mouse
    def get_mouse_pos(self):
        self.mouse_pos = pygame.mouse.get_pos()

    # draw things
    def draw_grid(self):
        pygame.draw.rect(
            self.surface,
            OUTLINE_COLOR,
            (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT),
            OUTLINE_THICKNESS,
        )  # frame

        for col in range(1, COLUMNS):  # columns
            x = col * FIELD_WIDTH
            pygame.draw.line(
                self.surface,
                OUTLINE_COLOR,
                (x, 0),
                (x, self.surface.get_height()),
                OUTLINE_THICKNESS,
            )

        for row in range(1, ROWS):  # rows
            y = row * FIELD_HEIGHT
            pygame.draw.line(
                self.surface,
                OUTLINE_COLOR,
                (0, y),
                (self.surface.get_width(), y),
                OUTLINE_THICKNESS,
            )

    def draw_fields(self):
        for tile in self.tiles.values():
            tile.draw(self.surface)

    def draw_end(self):

        # menu
        pygame.draw.rect(
            self.surface,
            BACKGROUND_COLOR,
            (SCREEN_WIDTH//8, SCREEN_HEIGHT//5, SCREEN_WIDTH*0.75, SCREEN_HEIGHT*0.6)
        )
        pygame.draw.rect(
            self.surface,
            END_OUTLINE_COLOR,
            (SCREEN_WIDTH//8, SCREEN_HEIGHT//5, SCREEN_WIDTH*0.75, SCREEN_HEIGHT*0.6),
            OUTLINE_THICKNESS
        )

        # text
        if self.won:
            message = "Congratulations!"
        else: message = "YOU LOST!"

        text = MENU_FONT.render(message, 1, TEXT_COLOR)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT*0.4))
        self.surface.blit(text, text_rect)

        # button + text
        self.surface.blit(
            self.try_again_bttn.image,
            self.try_again_bttn.rect
            )
        
        self.surface.blit(
            self.bttn_txt_surface,
            self.bttn_txt_rect
            )

    # tiles
    def get_random_pos(self):
        while True:
            row = randrange(0, ROWS)
            col = randrange(0, COLUMNS)

            try:
                if (col, row) not in self.tiles:
                    break
            except AttributeError:
                break

        return (col, row)

    def set_credentials(self, direction):

        if direction == "left":
            self.ceil = True
            self.delta = (-MOVE_VEL, 0)

            self.reverse = False
            self.sort_func = lambda x: x.col

            self.boundary_check = lambda tile: tile.col == 0
            self.get_next_tile = lambda tile: self.tiles.get((tile.col - 1, tile.row))

            self.merge_check = lambda tile, next_tile: tile.x > next_tile.x + MOVE_VEL
            self.move_check = (
                lambda tile, next_tile: tile.x > next_tile.x + FIELD_WIDTH + MOVE_VEL
            )

        elif direction == "right":
            self.ceil = False
            self.delta = (MOVE_VEL, 0)

            self.reverse = True
            self.sort_func = lambda x: x.col

            self.boundary_check = lambda tile: tile.col == COLUMNS - 1
            self.get_next_tile = lambda tile: self.tiles.get((tile.col + 1, tile.row))

            self.merge_check = lambda tile, next_tile: tile.x < next_tile.x - MOVE_VEL
            self.move_check = (
                lambda tile, next_tile: tile.x + FIELD_WIDTH + MOVE_VEL < next_tile.x
            )

        elif direction == "up":
            self.ceil = True
            self.delta = (0, -MOVE_VEL)

            self.reverse = False
            self.sort_func = lambda x: x.row

            self.boundary_check = lambda tile: tile.row == 0
            self.get_next_tile = lambda tile: self.tiles.get((tile.col, tile.row - 1))

            self.merge_check = lambda tile, next_tile: tile.y > next_tile.y + MOVE_VEL
            self.move_check = (
                lambda tile, next_tile: tile.y > next_tile.y + FIELD_HEIGHT + MOVE_VEL
            )

        elif direction == "down":
            self.ceil = False
            self.delta = (0, MOVE_VEL)

            self.reverse = True
            self.sort_func = lambda x: x.row

            self.boundary_check = lambda tile: tile.row == ROWS - 1
            self.get_next_tile = lambda tile: self.tiles.get((tile.col, tile.row + 1))

            self.merge_check = lambda tile, next_tile: tile.y > next_tile.y - MOVE_VEL
            self.move_check = (
                lambda tile, next_tile: tile.y + FIELD_HEIGHT + MOVE_VEL < next_tile.y
            )

        self.move_tiles()

    # move them
    def move_tiles(self):
        updated = True
        merged_tiles = set()
        sorted_tiles = sorted(self.tiles.values(), key=self.sort_func, reverse=self.reverse)

        while updated:
            updated = False

            for indx, tile in enumerate(sorted_tiles):
                self.update_tiles(sorted_tiles)
                if self.boundary_check(tile):
                    continue

                next_tile = self.get_next_tile(tile)
                if not next_tile:
                    tile.move(self.delta)
                elif (
                    (tile.value == next_tile.value)
                    and (tile not in merged_tiles)
                    and (next_tile not in merged_tiles)
                ):
                    if self.merge_check(tile, next_tile):
                        tile.move(self.delta)
                    else:
                        next_tile.value *= 2
                        sorted_tiles.pop(indx) 
                        merged_tiles.add(next_tile)
                elif self.move_check(tile, next_tile):
                    tile.move(self.delta)
                else:
                    continue # when next tile's value is diiferent

                tile.set_pos(self.ceil)
                updated = True

            self.update_tiles(sorted_tiles)  # gives new updated grid

        self.end_move()

    def end_move(self):
        # check loss and win
        if len(self.tiles) == 16:
            self.finished = True
            return "lost"
        
        for tile in self.tiles.values():
            if tile.value == 2048:
                self.finished = True
                self.won = True
                return "lost"

        pos = self.get_random_pos()
        self.tiles[pos] = Tile(choice([2, 4]), pos)
        return "continue"

    def update_tiles(self, sorted_tiles):
        self.tiles.clear()

        for tile in sorted_tiles:
            self.tiles[(tile.col, tile.row)] = tile

        self.draw_fields()

    # keys
    def check_keys(self):
        if not self.finished:
            keys = pygame.key.get_pressed()

            if not self.key_timer.active:
                if keys[pygame.K_LEFT]:
                    self.set_credentials("left")
                    self.key_timer.activate()
                elif keys[pygame.K_RIGHT]:
                    self.set_credentials("right")
                    self.key_timer.activate()
                elif keys[pygame.K_UP]:
                    self.set_credentials("up")
                    self.key_timer.activate()
                elif keys[pygame.K_DOWN]:
                    self.set_credentials("down")
                    self.key_timer.activate()

    def check_endbutton(self):
        if not self.mouse_timer.active:
            
            # restart game
            if self.try_again_bttn.clicked(self.mouse_pos):
                self.tiles.clear()
                self.tiles = {
                    pos: Tile(2, pos) for pos in [self.get_random_pos() for _ in range(2)]
                }

                self.won = False
                self.finished = False
                self.mouse_timer.activate()

    # run Forest, run!
    def run(self):

        # some
        self.key_timer.update()

        # thing
        self.surface.fill(BACKGROUND_COLOR)

        # check
        self.check_keys()

        # draw
        self.draw_fields()
        self.draw_grid()

        # end
        if self.finished:
            self.draw_end()
            self.get_mouse_pos()
            self.mouse_timer.update()
            self.check_endbutton()
        self.display_surface.blit(self.surface, (0, 0))


class Tile:
    def __init__(self, value, pos) -> None:
        self.value = value
        self.col, self.row = pos
        self.x = self.col * FIELD_WIDTH
        self.y = self.row * FIELD_HEIGHT

    def get_colors(self):
        index = int(math.log2(self.value)) - 1

        tc = NEXT_NUMBERS_COLORS[index]
        if self.value > 8:
            vc = (250,250,250)
        else:
            vc = VALUES_COLORS[index]

        return (tc, vc)
        
    def draw(self, surface):
        tile_color, value_color = self.get_colors()

        # draw tile
        pygame.draw.rect(surface, tile_color, (self.x, self.y, FIELD_WIDTH, FIELD_HEIGHT))

        # draw value
        text = GAME_FONT.render(f"{self.value}", 1, value_color)
        surface.blit(
            text,
            (
                self.x + FIELD_WIDTH // 2 - text.get_width() // 2,
                self.y + FIELD_HEIGHT // 2 - text.get_height() // 2,
            ),
        )

    def set_pos(self, ceil=False):
        if ceil:
            self.row = math.ceil(self.y / FIELD_HEIGHT)
            self.col = math.ceil(self.x / FIELD_WIDTH)
        else:
            self.row = math.floor(self.y / FIELD_HEIGHT)
            self.col = math.floor(self.x / FIELD_WIDTH)

    def move(self, delta):
        self.x += delta[0]
        self.y += delta[1]
