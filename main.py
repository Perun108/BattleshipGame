import copy
import logging
import sys

import pygame

logging.basicConfig(
    filename="battleship.log", filemode="w", format="%(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.warning("This will get logged to a file")

from drawings import Grid
from drawings.button import Button
from drawings.drawing import (
    draw_from_dotted_set,
    draw_hit_blocks,
    draw_ships,
    show_message_at_rect_center,
)
from drawings.manual_ships import manually_create_new_ship
from game_elements.constants import (
    AUTO_BUTTON_PLACE,
    BLACK,
    BLOCK_SIZE,
    FONT_SIZE,
    GAME_OVER_FONT_SIZE,
    HOW_TO_CREATE_SHIPS_MESSAGE,
    LEFT_MARGIN,
    LETTERS,
    LIGHT_GRAY,
    MANUAL_BUTTON_PLACE,
    MESSAGE_RECT_COMPUTER,
    MESSAGE_RECT_HUMAN,
    PLAY_AGAIN_BUTTON_PLACE,
    PLAY_AGAIN_MESSAGE,
    RECT_FOR_GRIDS,
    RECT_FOR_MESSAGES_AND_BUTTONS,
    SIZE,
    UNDO_BUTTON_PLACE,
    UPPER_MARGIN,
    WHITE,
)
from game_elements.random_ships import AutoShips
from game_logic.game_logic import check_hit_or_miss, computer_shoots, update_used_blocks

pygame.init()

screen = pygame.display.set_mode(SIZE)
font = pygame.font.SysFont("notosans", FONT_SIZE)
game_over_font = pygame.font.SysFont("notosans", GAME_OVER_FONT_SIZE)

### COMPUTER DATA ###
computer_available_to_fire_set = {(x, y) for x in range(16, 26) for y in range(1, 11)}
around_last_computer_hit_set = set()
dotted_set_for_computer_not_to_shoot = set()
hit_blocks_for_computer_not_to_shoot = set()
last_hits_list = []
###################

hit_blocks = set()
dotted_set = set()
destroyed_computer_ships = []


# Create computer ships
computer = AutoShips(0)
computer_ships_working = copy.deepcopy(computer.ships)

# Create AUTO and MANUAL buttons and explanatory message for them
auto_button = Button(AUTO_BUTTON_PLACE, "AUTO", HOW_TO_CREATE_SHIPS_MESSAGE, font)
manual_button = Button(MANUAL_BUTTON_PLACE, "MANUAL", HOW_TO_CREATE_SHIPS_MESSAGE, font)

# Create UNDO message and button
undo_button = Button(UNDO_BUTTON_PLACE, "UNDO LAST SHIP", "", font)

# Create PLAY AGAIN and QUIT buttons and message for them
play_again_button = Button(PLAY_AGAIN_BUTTON_PLACE, "PLAY AGAIN", PLAY_AGAIN_MESSAGE, font)
quit_game_button = Button(MANUAL_BUTTON_PLACE, "QUIT", PLAY_AGAIN_MESSAGE, font)


def main():
    ships_creation_not_decided = True
    ships_not_created = True
    drawing = False
    game_over = False
    computer_turn = False
    start = (0, 0)
    ship_size = (0, 0)

    human_ships_to_draw = []
    human_ships_set = set()
    used_blocks_for_manual_drawing = set()
    num_ships_list = [0, 0, 0, 0]

    screen.fill(WHITE)
    Grid(title="COMPUTER", offset=0, font=font, letters=LETTERS, line_color=BLACK, text_color=BLACK)
    Grid(title="HUMAN", offset=15, font=font, letters=LETTERS, line_color=BLACK, text_color=BLACK)

    while ships_creation_not_decided:
        auto_button.draw()
        manual_button.draw()
        auto_button.change_color_on_hover()
        manual_button.change_color_on_hover()
        auto_button.print_message()

        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # If AUTO button is pressed - create human ships automatically
            elif event.type == pygame.MOUSEBUTTONDOWN and auto_button.rect.collidepoint(mouse):
                human = AutoShips(15)
                human_ships_to_draw = human.ships
                human_ships_working = copy.deepcopy(human.ships)
                human_ships_set = human.ships_set
                ships_creation_not_decided = False
                ships_not_created = False
            elif event.type == pygame.MOUSEBUTTONDOWN and manual_button.rect.collidepoint(mouse):
                ships_creation_not_decided = False

        pygame.display.update()
        screen.fill(WHITE, RECT_FOR_MESSAGES_AND_BUTTONS)

    while ships_not_created:
        screen.fill(WHITE, RECT_FOR_GRIDS)
        Grid(title="COMPUTER", offset=0, font=font, letters=LETTERS, line_color=BLACK, text_color=BLACK)
        Grid(title="HUMAN", offset=15, font=font, letters=LETTERS, line_color=BLACK, text_color=BLACK)
        undo_button.draw()
        undo_button.print_message()
        undo_button.change_color_on_hover()
        mouse = pygame.mouse.get_pos()
        if not human_ships_to_draw:
            undo_button.draw(LIGHT_GRAY)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif undo_button.rect.collidepoint(mouse) and event.type == pygame.MOUSEBUTTONDOWN:
                if human_ships_to_draw:
                    screen.fill(WHITE, RECT_FOR_MESSAGES_AND_BUTTONS)
                    deleted_ship = human_ships_to_draw.pop()
                    num_ships_list[len(deleted_ship) - 1] -= 1
                    update_used_blocks(ship=deleted_ship, method=used_blocks_for_manual_drawing.discard)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                drawing = True
                x_start, y_start = event.pos
                start = x_start, y_start
                ship_size = (0, 0)
            elif drawing and event.type == pygame.MOUSEMOTION:
                x_end, y_end = event.pos
                end = x_end, y_end
                ship_size = x_end - x_start, y_end - y_start
            elif drawing and event.type == pygame.MOUSEBUTTONUP:
                x_end, y_end = event.pos
                drawing = False
                ship_size = (0, 0)
                manually_create_new_ship(
                    human_ships_to_draw=human_ships_to_draw,
                    human_ships_set=human_ships_set,
                    used_blocks_for_manual_drawing=used_blocks_for_manual_drawing,
                    num_ships_list=num_ships_list,
                    x_start=x_start,
                    y_start=y_start,
                    x_end=x_end,
                    y_end=y_end,
                )
            if len(human_ships_to_draw) == 10:
                ships_not_created = False
                human_ships_working = copy.deepcopy(human_ships_to_draw)
                screen.fill(WHITE, RECT_FOR_MESSAGES_AND_BUTTONS)
        pygame.draw.rect(screen, BLACK, (start, ship_size), 3)
        draw_ships(human_ships_to_draw)
        pygame.display.update()

    while not game_over:
        draw_ships(destroyed_computer_ships)
        draw_ships(human_ships_to_draw)
        if not (dotted_set | hit_blocks):
            show_message_at_rect_center("GAME STARTED! YOUR MOVE!", MESSAGE_RECT_COMPUTER)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif not computer_turn and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if (LEFT_MARGIN < x < LEFT_MARGIN + 10 * BLOCK_SIZE) and (
                    UPPER_MARGIN < y < UPPER_MARGIN + 10 * BLOCK_SIZE
                ):
                    fired_block = ((x - LEFT_MARGIN) // BLOCK_SIZE + 1, (y - UPPER_MARGIN) // BLOCK_SIZE + 1)
                    logging.info(f"Human shot at {LETTERS[fired_block[0]-1] + str(fired_block[1])}")
                    computer_turn = not check_hit_or_miss(
                        fired_block=fired_block,
                        opponents_ships_list=computer_ships_working,
                        computer_turn=False,
                        opponents_ships_list_original_copy=computer.ships,
                        opponents_ships_set=computer.ships_set,
                        destroyed_computer_ships=destroyed_computer_ships,
                        computer=computer,
                        last_hits_list=last_hits_list,
                        around_last_computer_hit_set=around_last_computer_hit_set,
                        hit_blocks_for_computer_not_to_shoot=hit_blocks_for_computer_not_to_shoot,
                        hit_blocks=hit_blocks,
                        computer_available_to_fire_set=computer_available_to_fire_set,
                        dotted_set_for_computer_not_to_shoot=dotted_set_for_computer_not_to_shoot,
                        dotted_set=dotted_set,
                    )
                    logging.info(f"Dotted set is {dotted_set}")
                    logging.info(f"Hit blocks are {hit_blocks}")
                    logging.info(f"last_hits_list is {last_hits_list}")
                    logging.info(f"around_last_computer_hit_set is {around_last_computer_hit_set}")
                    logging.info(f"hit_blocks_for_computer_not_to_shoot is {hit_blocks_for_computer_not_to_shoot}")
                    logging.info(f"computer_available_to_fire_set are {computer_available_to_fire_set}")
                    logging.info(f"dotted_set_for_computer_not_to_shoot is {dotted_set_for_computer_not_to_shoot}")
                    logging.info("-------------------------")

                    draw_from_dotted_set(dotted_set)
                    draw_hit_blocks(hit_blocks)
                    screen.fill(WHITE, MESSAGE_RECT_COMPUTER)
                    show_message_at_rect_center(
                        f"Your last shot: {LETTERS[fired_block[0]-1] + str(fired_block[1])}",
                        MESSAGE_RECT_COMPUTER,
                    )
                else:
                    show_message_at_rect_center("Your shot is outside of grid! Try again", MESSAGE_RECT_COMPUTER)
        if computer_turn:
            set_to_shoot_from = computer_available_to_fire_set
            if around_last_computer_hit_set:
                set_to_shoot_from = around_last_computer_hit_set
            fired_block = computer_shoots(
                set_to_shoot_from=set_to_shoot_from, computer_available_to_fire_set=computer_available_to_fire_set
            )
            logging.info(f"Computer shot at {LETTERS[fired_block[0] - 16] + str(fired_block[1])}")
            computer_turn = check_hit_or_miss(
                fired_block=fired_block,
                opponents_ships_list=human_ships_working,
                computer_turn=True,
                opponents_ships_list_original_copy=human_ships_to_draw,
                opponents_ships_set=human_ships_set,
                last_hits_list=last_hits_list,
                destroyed_computer_ships=destroyed_computer_ships,
                computer=computer,
                around_last_computer_hit_set=around_last_computer_hit_set,
                hit_blocks_for_computer_not_to_shoot=hit_blocks_for_computer_not_to_shoot,
                hit_blocks=hit_blocks,
                computer_available_to_fire_set=computer_available_to_fire_set,
                dotted_set_for_computer_not_to_shoot=dotted_set_for_computer_not_to_shoot,
                dotted_set=dotted_set,
            )
            logging.info(f"Dotted set is {dotted_set}")
            logging.info(f"Hit blocks are {hit_blocks}")
            logging.info(f"Dotted set is {dotted_set}")
            logging.info(f"Hit blocks are {hit_blocks}")
            logging.info(f"last_hits_list is {last_hits_list}")
            logging.info(f"set_to_shoot_from is {set_to_shoot_from}")
            logging.info(f"hit_blocks_for_computer_not_to_shoot is {hit_blocks_for_computer_not_to_shoot}")
            logging.info(f"computer_available_to_fire_set are {computer_available_to_fire_set}")
            logging.info(f"dotted_set_for_computer_not_to_shoot is {dotted_set_for_computer_not_to_shoot}")
            logging.info("-------------------------")

            draw_from_dotted_set(dotted_set)
            draw_hit_blocks(hit_blocks)
            screen.fill(WHITE, MESSAGE_RECT_HUMAN)
            show_message_at_rect_center(
                f"Computer's last shot: {LETTERS[fired_block[0] - 16] + str(fired_block[1])}",
                MESSAGE_RECT_HUMAN,
            )
        if not computer.ships_set:
            show_message_at_rect_center("YOU WON!", (0, 0, SIZE[0], SIZE[1]), game_over_font)
            game_over = True
        if not human_ships_set:
            show_message_at_rect_center("YOU LOST!", (0, 0, SIZE[0], SIZE[1]), game_over_font)
            game_over = True
        pygame.display.update()

    while game_over:
        screen.fill(WHITE, RECT_FOR_MESSAGES_AND_BUTTONS)
        play_again_button.draw()
        play_again_button.print_message()
        play_again_button.change_color_on_hover()
        quit_game_button.draw()
        quit_game_button.change_color_on_hover()

        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and play_again_button.rect.collidepoint(mouse):
                main()
            elif event.type == pygame.MOUSEBUTTONDOWN and quit_game_button.rect.collidepoint(mouse):
                pygame.quit()
                sys.exit()
        pygame.display.update()


if __name__ == "__main__":
    main()
