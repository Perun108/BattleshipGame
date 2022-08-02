import pygame

from game_elements.constants import (
    BLACK,
    BLOCK_SIZE,
    FONT_SIZE,
    LEFT_MARGIN,
    RED,
    SIZE,
    UPPER_MARGIN,
    WHITE,
)
from game_logic.game_logic import (
    computer_destroyed_ships_count,
    human_destroyed_ships_count,
)

pygame.init()
screen = pygame.display.set_mode(SIZE)
font = pygame.font.SysFont("notosans", FONT_SIZE)


def draw_ships(ships_coordinates_list, ships_color=BLACK):
    """
    Draws rectangles around the blocks that are occupied by a ship
    Args:
        ships_coordinates_list (list of tuples): a list of ships's coordinates
    """
    for elem in ships_coordinates_list:
        ship = sorted(elem)
        x_start = ship[0][0]
        y_start = ship[0][1]
        # Horizontal and 1block ships
        ship_width = BLOCK_SIZE * len(ship)
        ship_height = BLOCK_SIZE
        # Vertical ships
        if len(ship) > 1 and ship[0][0] == ship[1][0]:
            ship_width, ship_height = ship_height, ship_width
        x = BLOCK_SIZE * (x_start - 1) + LEFT_MARGIN
        y = BLOCK_SIZE * (y_start - 1) + UPPER_MARGIN
        pygame.draw.rect(screen, ships_color, ((x, y), (ship_width, ship_height)), width=BLOCK_SIZE // 10)


def draw_from_dotted_set(dotted_set_to_draw_from, dots_color=BLACK):
    """
    Draws dots in the center of all blocks in the dotted_set
    """
    for elem in dotted_set_to_draw_from:
        pygame.draw.circle(
            screen,
            dots_color,
            (BLOCK_SIZE * (elem[0] - 0.5) + LEFT_MARGIN, BLOCK_SIZE * (elem[1] - 0.5) + UPPER_MARGIN),
            BLOCK_SIZE // 6,
        )


def draw_hit_blocks(hit_blocks_to_draw_from, hit_blocks_color=BLACK):
    """
    Draws 'X' in the blocks that were successfully hit either by computer or by human
    """
    for block in hit_blocks_to_draw_from:
        x1 = BLOCK_SIZE * (block[0] - 1) + LEFT_MARGIN
        y1 = BLOCK_SIZE * (block[1] - 1) + UPPER_MARGIN
        pygame.draw.line(screen, hit_blocks_color, (x1, y1), (x1 + BLOCK_SIZE, y1 + BLOCK_SIZE), BLOCK_SIZE // 6)
        pygame.draw.line(screen, hit_blocks_color, (x1, y1 + BLOCK_SIZE), (x1 + BLOCK_SIZE, y1), BLOCK_SIZE // 6)


def show_message_at_rect_center(message, rect, font=font, message_color=RED, background_color=WHITE):
    """
    Prints message to screen at a given rect's center.
    Args:
        message (str): Message to print
        rect (tuple): rectangle in (x_start, y_start, width, height) format
        font (pygame font object, optional): What font to use to print message. Defaults to font.
        message_color (tuple, optional): Color of the message. Defaults to RED.
    """
    message_width, message_height = font.size(message)
    message_rect = pygame.Rect(rect)
    x_start = message_rect.centerx - message_width / 2
    y_start = message_rect.centery - message_height / 2
    background_rect = pygame.Rect(x_start - BLOCK_SIZE / 2, y_start, message_width + BLOCK_SIZE, message_height)
    message_to_blit = font.render(message, True, message_color)
    screen.fill(background_color, background_rect)
    screen.blit(message_to_blit, (x_start, y_start))


def print_destroyed_ships_count(font):
    for ship, count in human_destroyed_ships_count.items():
        text = font.render(f"{ship}: {count}", True, RED)
        screen.blit(text, (LEFT_MARGIN + 27 * BLOCK_SIZE, UPPER_MARGIN + 2 * BLOCK_SIZE + ship * BLOCK_SIZE))

    for ship, count in computer_destroyed_ships_count.items():
        text = font.render(f"{ship}: {count}", True, RED)
        screen.blit(text, (LEFT_MARGIN - 4 * BLOCK_SIZE, UPPER_MARGIN + 2 * BLOCK_SIZE + ship * BLOCK_SIZE))
