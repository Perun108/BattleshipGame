import pygame
import random
import copy

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
LIGHT_GRAY = (192, 192, 192)
GREEN_BLUE = (0, 153, 153)
INK = (39, 64, 139)
VIOLET = (6, 10, 88)

block_size = 50
left_margin = 5*block_size
upper_margin = 2*block_size
# 30 = 2x10 blocks width in two grids + hard-coded 5*blocks gap after each grid!
size = (left_margin+30*block_size, upper_margin+15*block_size)
# LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
LETTERS = "АБВГДЕЖЗИК"

pygame.init()
# clock = pygame.time.Clock()
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Morskoy Boy")
# This ratio is purely for scaling the font according to the block size
font_size = int(block_size / 1.5)
font = pygame.font.SysFont('notosans', font_size)
game_over_font_size = 3*block_size
game_over_font = pygame.font.SysFont('notosans', game_over_font_size)

### COMPUTER DATA ###
computer_available_to_fire_set = {(a, b)
                                  for a in range(16, 26) for b in range(1, 11)}
around_last_computer_hit_set = set()
dotted_set_for_computer_not_to_shoot = set()
hit_blocks_for_computer_not_to_shoot = set()
last_hits_list = []
############

hit_blocks = set()
dotted_set = set()
destroyed_computer_ships = []


class Grid:
    """Class to draw the grids and add title, numbers and letters to them
    ----------
    Attributes:
        title (str): Players' name to be displayed on the top of his grid
        offset (int): Where the grid starts (in number of blocks)
                (typically 0 for computer and 15 for human)
    ----------
    Methods:
    draw_grid(): Draws two grids for both players
    add_nums_letters_to_grid(): Draws numbers 1-10 along vertical and adds letters below horizontal
        lines for both grids
    sign_grid(): Puts players' names (titles) in the center above the grids
    """
    def __init__(self, title, offset):
        self.title = title
        self.offset = offset
        self.draw_grid()
        self.add_nums_letters_to_grid()
        self.sign_grid()

    def draw_grid(self):
        """Draws two grids for both players
        """
        for i in range(11):
            # Horizontal lines
            pygame.draw.line(screen, BLACK, (left_margin+self.offset*block_size, upper_margin+i*block_size),
                             (left_margin+(10+self.offset)*block_size, upper_margin+i*block_size), 1)
            # Vertical lines
            pygame.draw.line(screen, BLACK, (left_margin+(i+self.offset)*block_size, upper_margin),
                             (left_margin+(i+self.offset)*block_size, upper_margin+10*block_size), 1)

    def add_nums_letters_to_grid(self):
        """Draws numbers 1-10 along vertical and adds letters below horizontal
        lines for both grids
        """
        for i in range(10):
            num_ver = font.render(str(i+1), True, BLACK)
            letters_hor = font.render(LETTERS[i], True, BLACK)
            num_ver_width = num_ver.get_width()
            num_ver_height = num_ver.get_height()
            letters_hor_width = letters_hor.get_width()

            # Numbers (vertical)
            screen.blit(num_ver, (left_margin - (block_size//2+num_ver_width//2)+self.offset*block_size,
                                  upper_margin + i*block_size + (block_size//2 - num_ver_height//2)))
            # Letters (horizontal)
            screen.blit(letters_hor, (left_margin + i*block_size + (block_size //
                                                                    2 - letters_hor_width//2)+self.offset*block_size, upper_margin + 10*block_size))

    def sign_grid(self):
        """Puts players' names (titles) in the center above the grids
        """
        player = font.render(self.title, True, BLACK)
        sign_width = player.get_width()
        screen.blit(player, (left_margin + 5*block_size - sign_width //
                             2+self.offset*block_size, upper_margin - block_size//2 - font_size))


class Button:
    def __init__(self, x_offset, button_title, message_to_show):
        self.title = button_title
        self.title_width, self.title_height = font.size(self.title)
        self.message = message_to_show

        self.button_width = self.title_width + block_size
        self.button_height = self.title_height + block_size

        self.x_start = x_offset
        self.y_start = upper_margin + 10 * block_size + self.button_height

        self.rect_for_draw = self.x_start, self.y_start, self.button_width, self.button_height
        self.rect = pygame.Rect(self.rect_for_draw)

        self.rect_for_button_text = self.x_start + self.button_width / 2 - \
            self.title_width / 2, self.y_start + self.button_height / 2 - self.title_height / 2
        
        self.color = BLACK

    def draw_button(self, color=None):
        """
        Draws button and prints its name (title) within it

        Args:
            color (tuple, optional): Default color will be BLACK as in class constructor
        but we need to also change it when a button is hovered over or disabled. 
        Defaults to None.
        """
        if not color:
            color = self.color
        pygame.draw.rect(screen, color, self.rect_for_draw)
        text_to_blit = font.render(self.title, True, WHITE)
        screen.blit(text_to_blit, self.rect_for_button_text)

    def change_color_on_hover(self):
        """
        Changing color of the button while hovering over with a mouse
        """
        mouse = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse):
            self.draw_button(GREEN_BLUE)

    def print_message_for_button(self):
        """
        Shows explanatory message next to button
        """
        if self.message:
            self.message_width, self.message_height = font.size(self.message)
            self.rect_for_message = self.x_start / 2 - self.message_width / 2, self.y_start + self.button_height / 2 - self.message_height / 2
            text = font.render(self.message, True, BLACK)
            screen.blit(text, self.rect_for_message)


class AutoShips:
    """Randomly create all player's ships on a grid
    ----------
    Attributes:
        offset (int): Where the grid starts (in number of blocks) 
                (typically 0 for computer and 15 for human)
        available_blocks (set of tuples): coordinates of all blocks 
                that are avaiable for creating ships (updated every time a ship is created)
        ships_set (set of tuples): all blocks that are occupied by ships
        ships (list of lists): list of all individual ships (as lists)

    ----------
    Methods:
        create_start_block(available_blocks):
            Randomly chooses a block from which to start creating a ship.
            Randomly chooses horizontal or vertical type of a ship
            Randomly chooses direction (from the start block) - straight or reverse
            Returns three randomly chosen values

        create_ship(number_of_blocks, available_blocks):
            Creates a ship of given length (number_of_blocks) starting from the start block
                returned by the previous method, using type of ship and direction (changing it 
                if going outside of grid) returned by previous method. 
                Checks if the ship is valid (not adjacent to other ships and within the grid) 
                and adds it to the list of ships.
            Returns: a list of tuples with a new ship's coordinates

        get_new_block_for_ship(self, coor, str_rev, x_or_y, ship_coordinates):
            Checks if new individual blocks that are being added to a ship in the previous method 
                are within the grid, otherwise changes the direction.
            Returns: 
                direction (int): straight or reverse
                incremented/decremented coordinate of the last/first block in a ship under construction

        is_ship_valid(new_ship):
            Check if all of a ship's coordinates are within the available blocks set.
            Returns: True or False

        add_new_ship_to_set(new_ship):
            Adds all blocks in a ship's list to the ships_set

        update_available_blocks_for_creating_ships(new_ship):
            Removes all blocks occupied by a ship and around it from the available blocks set

        populate_grid():
            Creates needed number of each type of ships by calling the create_ship method.
                Adds every ship to the ships list, ships_set and updates the available blocks.
            Returns: the list of all ships

    """

    def __init__(self, offset):
        """
        Parameters:
        offset (int): Where the grid starts (in number of blocks) 
                (typically 0 for computer and 15 for human)
        available_blocks (set of tuples): coordinates of all blocks 
                that are avaiable for creating ships (updated every time a ship is created)
        ships_set (set of tuples): all blocks that are occupied by ships
        ships (list of lists): list of all individual ships (as lists)"""

        self.offset = offset
        self.available_blocks = {(x, y) for x in range(1+self.offset, 11+self.offset) for y in range(1, 11)}
        self.ships_set = set()
        self.ships = self.populate_grid()

    def create_start_block(self, available_blocks):
        """
        Randomly chooses a block from which to start creating a ship.
        Randomly chooses horizontal or vertical type of a ship
        Randomly chooses direction (from the start block) - straight or reverse

        Args:
            available_blocks (set of tuples): coordinates of all blocks 
                that are avaiable for creating ships (updated every time a ship is created)

        Returns:
            int: x coordinate of a random block
            int: y coordinate of a random block
            int: 0=horizontal (change x), 1=vertical (change y)
            int: 1=straight, -1=reverse
        """
        x_or_y = random.randint(0, 1)
        # -1 is left or down, 1 is right or up
        str_rev = random.choice((-1, 1))
        x, y = random.choice(tuple(available_blocks))
        return x, y, x_or_y, str_rev

    def create_ship(self, number_of_blocks, available_blocks):
        """Creates a ship of given length (number_of_blocks) starting from the start block
                returned by the previous method, using type of ship and direction (changing it 
                if going outside of grid) returned by previous method. 
                Checks if the ship is valid (not adjacent to other ships and within the grid) 
                and adds it to the list of ships.

        Args:
            number_of_blocks (int): length of a needed ship
            available_blocks (set): free blocks for creating ships

        Returns:
            list: a list of tuples with a new ship's coordinates
        """
        ship_coordinates = []
        x, y, x_or_y, str_rev = self.create_start_block(available_blocks)
        for _ in range(number_of_blocks):
            ship_coordinates.append((x, y))
            if not x_or_y:
                str_rev, x = self.get_new_block_for_ship(
                    x, str_rev, x_or_y, ship_coordinates)
            else:
                str_rev, y = self.get_new_block_for_ship(
                    y, str_rev, x_or_y, ship_coordinates)
        if self.is_ship_valid(ship_coordinates):
            return ship_coordinates
        return self.create_ship(number_of_blocks, available_blocks)

    def get_new_block_for_ship(self, coor, str_rev, x_or_y, ship_coordinates):
        """Checks if new individual blocks that are being added to a ship in the previous method 
                are within the grid, otherwise changes the direction.

        Args:
            coor (int): x or y coordinate to increment/decrement
            str_rev (int): 1 or -1
            x_or_y (int): 0 or 1
            ship_coordinates (list): coordinates of unfinished ship

        Returns:
            direction (int): straight or reverse
            incremented/decremented coordinate of the last/first block in a ship under construction (int)
        """
        if (coor <= 1-self.offset*(x_or_y-1) and str_rev == -1) or (coor >= 10-self.offset*(x_or_y-1) and str_rev == 1):
            str_rev *= -1
            return str_rev, ship_coordinates[0][x_or_y] + str_rev
        else:
            return str_rev, ship_coordinates[-1][x_or_y] + str_rev

    def is_ship_valid(self, new_ship):
        """Check if all of a ship's coordinates are within the available blocks set.

        Args:
            new_ship (list): list of tuples with a newly created ship's coordinates

        Returns:
            bool: True or False
        """
        ship = set(new_ship)
        return ship.issubset(self.available_blocks)

    def add_new_ship_to_set(self, new_ship):
        """Adds all blocks in a ship's list to the ships_set

        Args:
            new_ship (list): list of tuples with a newly created ship's coordinates
        """
        self.ships_set.update(new_ship)

    def update_available_blocks_for_creating_ships(self, new_ship):
        """Removes all blocks occupied by a ship and around it from the available blocks set

        Args:
            new_ship ([type]): list of tuples with a newly created ship's coordinates
        """
        for elem in new_ship:
            for k in range(-1, 2):
                for m in range(-1, 2):
                    if 0+self.offset < (elem[0]+k) < 11+self.offset and 0 < (elem[1]+m) < 11:
                        self.available_blocks.discard((elem[0]+k, elem[1]+m))

    def populate_grid(self):
        """Creates needed number of each type of ships by calling the create_ship method.
                Adds every ship to the ships list, ships_set and updates the available blocks.

        Returns:
            list: the 2d list of all ships
        """
        ships_coordinates_list = []
        for number_of_blocks in range(4, 0, -1):
            for _ in range(5-number_of_blocks):
                new_ship = self.create_ship(
                    number_of_blocks, self.available_blocks)
                ships_coordinates_list.append(new_ship)
                self.add_new_ship_to_set(new_ship)
                self.update_available_blocks_for_creating_ships(new_ship)
        return ships_coordinates_list


# ===========Shooting section==============

def computer_shoots(set_to_shoot_from):
    """Randomly chooses a block from available to shoot from set
    """
    computer_fired_block = random.choice(tuple(set_to_shoot_from))
    computer_available_to_fire_set.discard(computer_fired_block)
    return computer_fired_block


def check_hit_or_miss(fired_block, opponents_ships_list, computer_turn, opponents_ships_list_original_copy, opponents_ships_set):
    # if computer_turn:
    #    pygame.time.delay(500)
    """Checks whether the block that was shot at either by computer or by human is a hit or a miss.
    Updates sets with dots (in missed blocks or in diagonal blocks around hit block) and 'X's
    (in hit blocks).
    Removes destroyed ships from the list of ships.
    """
    for elem in opponents_ships_list:
        diagonal_only = True
        if fired_block in elem:
            ind = opponents_ships_list.index(elem)
            if len(elem) == 1:
                diagonal_only = False
            update_dotted_and_hit_sets(fired_block, computer_turn, diagonal_only)
            elem.remove(fired_block)
            opponents_ships_set.discard(fired_block)
            if computer_turn:
                last_hits_list.append(fired_block)
                update_around_last_computer_hit(fired_block)
            if not elem:
                update_destroyed_ships(ind, computer_turn, opponents_ships_list_original_copy)
                if computer_turn:
                    last_hits_list.clear()
                    around_last_computer_hit_set.clear()
                else:
                    destroyed_computer_ships.append(computer.ships[ind])
            return True
    add_missed_block_to_dotted_set(fired_block)
    if computer_turn:
        update_around_last_computer_hit(fired_block, False)
    return False


def update_destroyed_ships(ind, computer_turn, opponents_ships_list_original_copy):
    """Draws dots around and 'X's within a destroyed ship.
    Draws rectangle around destroyed computer ships on grid1 (that were not visible before destruction)
    """
    ship = sorted(opponents_ships_list_original_copy[ind])
    for i in range(-1, 1):
        update_dotted_and_hit_sets(ship[i], computer_turn, False)


def update_around_last_computer_hit(fired_block, computer_hits=True):
    """Updates around_last_computer_hit_set (which is used to choose for computer to fire from) if it
    hit the ship but not destroyed it). Adds to this set vertical or horizontal blocks around the
    block that was last hit. Then removes those block from that set which were shot at but missed.
    around_last_computer_hit_set makes computer choose the right blocks to quickly destroy the ship
    instead of just randomly shooting at completely random blocks.
    """
    global around_last_computer_hit_set, computer_available_to_fire_set
    if computer_hits and fired_block in around_last_computer_hit_set:
        around_last_computer_hit_set = computer_hits_twice()
    elif computer_hits and fired_block not in around_last_computer_hit_set:
        computer_first_hit(fired_block)
    elif not computer_hits:
        around_last_computer_hit_set.discard(fired_block)

    around_last_computer_hit_set -= dotted_set_for_computer_not_to_shoot
    around_last_computer_hit_set -= hit_blocks_for_computer_not_to_shoot
    computer_available_to_fire_set -= around_last_computer_hit_set
    computer_available_to_fire_set -= dotted_set_for_computer_not_to_shoot


def computer_first_hit(fired_block):
    """Adds blocks above, below, to the right and to the left from the block hit 
    by computer to a temporary set for computer to choose its next shot from.

    Args:
        fired_block (tuple): coordinates of a block hit by computer
    """
    xhit, yhit = fired_block
    if xhit > 16:
        around_last_computer_hit_set.add((xhit-1, yhit))
    if xhit < 25:
        around_last_computer_hit_set.add((xhit+1, yhit))
    if yhit > 1:
        around_last_computer_hit_set.add((xhit, yhit-1))
    if yhit < 10:
        around_last_computer_hit_set.add((xhit, yhit+1))


def computer_hits_twice():
    """Adds blocks before and after two or more blocks of a ship to a temporary list 
    for computer to finish the ship faster.

    Returns:
        set: temporary set of blocks where potentially a human ship should be 
        for computer to shoot from
    """
    last_hits_list.sort()
    new_around_last_hit_set = set()
    for i in range(len(last_hits_list)-1):
        x1 = last_hits_list[i][0]
        x2 = last_hits_list[i+1][0]
        y1 = last_hits_list[i][1]
        y2 = last_hits_list[i+1][1]
        if x1 == x2:
            if y1 > 1:
                new_around_last_hit_set.add((x1, y1 - 1))
            if y2 < 10:
                new_around_last_hit_set.add((x1, y2 + 1))
        elif y1 == y2:
            if x1 > 16:
                new_around_last_hit_set.add((x1 - 1, y1))
            if x2 < 25:
                new_around_last_hit_set.add((x2 + 1, y1))
    return new_around_last_hit_set


def update_dotted_and_hit_sets(fired_block, computer_turn, diagonal_only=True):
    """Puts dots in center of diagonal or all around a block that was hit (either by human or
    by computer). Adds all diagonal blocks or all-around chosen block to a separate set
    block: hit block (tuple)
    """
    global dotted_set
    x, y = fired_block
    a, b = 0, 11
    if computer_turn:
        a += 15
        b += 15
        # Adds a block hit by computer to the set of his hits to later remove
        # them from the set of blocks available for it to shoot from
        hit_blocks_for_computer_not_to_shoot.add(fired_block)
    # Adds hit blocks on either grid1 (x:1-10) or grid2 (x:16-25)
    hit_blocks.add(fired_block)
    # Adds blocks in diagonal or all-around a block to repsective sets
    for i in range(-1, 2):
        for j in range(-1, 2):
            if diagonal_only:
                if i != 0 and j != 0 and a < x + i < b and 0 < y + j < 11:
                    dotted_set.add((x+i, y+j))
                    if computer_turn:
                        dotted_set_for_computer_not_to_shoot.add((x+i, y+j))
            else:
                if a < x + i < b and 0 < y + j < 11:
                    dotted_set.add((x+i, y+j))
                    if computer_turn:
                        dotted_set_for_computer_not_to_shoot.add((x+i, y+j))
    dotted_set -= hit_blocks


def add_missed_block_to_dotted_set(fired_block):
    """Adds a block to the set of missed shots or of those blocks that are on a diagonal line
    from the fired block or all-around destroyed ship. Needed for computer to remove these dotted
    blocks from the set of available blocks for it to shoot from. Not really needed for a human player.
    
    dotted_set: set of all blocks (tuples) that are marked by a dot on both grids (x: 1-10 and 16-25).
    """
    dotted_set.add(fired_block)
    dotted_set_for_computer_not_to_shoot.add(fired_block)


# ===========DRAWING SECTION==============

def draw_ships(ships_coordinates_list):
    """Draws rectangles around the blocks that are occupied by a ship

    Args:
        ships_coordinates_list (list of tuples): a list of ships's coordinates
    """
    for elem in ships_coordinates_list:
        ship = sorted(elem)
        x_start = ship[0][0]
        y_start = ship[0][1]
        # Horizontal and 1block ships
        ship_width = block_size * len(ship)
        ship_height = block_size
        # Vertical ships
        if len(ship) > 1 and ship[0][0] == ship[1][0]:
            ship_width, ship_height = ship_height, ship_width
        x = block_size * (x_start - 1) + left_margin
        y = block_size * (y_start - 1) + upper_margin
        pygame.draw.rect(
            screen, BLACK, ((x, y), (ship_width, ship_height)), width=block_size//10)


def draw_from_dotted_set(dotted_set):
    """Draws dots in the center of all blocks in the dotted_set
    """
    for elem in dotted_set:
        pygame.draw.circle(screen, BLACK, (block_size*(
            elem[0]-0.5)+left_margin, block_size*(elem[1]-0.5)+upper_margin), block_size//6)


def draw_hit_blocks(hit_blocks):
    """Draws 'X' in the blocks that were successfully hit either by computer or by human
    """
    for block in hit_blocks:
        x1 = block_size * (block[0]-1) + left_margin
        y1 = block_size * (block[1]-1) + upper_margin
        pygame.draw.line(screen, BLACK, (x1, y1),
                         (x1+block_size, y1+block_size), block_size//6)
        pygame.draw.line(screen, BLACK, (x1, y1+block_size),
                         (x1+block_size, y1), block_size//6)


def show_messages_at_rect_center(text, rect, which_font=font, color=RED):
    """Blits (prints) given message to the screen at the center of a given rectangle

    Args:
        text (str): text to be printed on the screen
        rect (tuple): 4 values - (x_start, y_start, width, height)
    """
    text_width, text_height = which_font.size(text)
    text_rect = pygame.Rect(rect)

    x_start = text_rect.centerx - text_width / 2
    y_start = text_rect.centery - text_height / 2
    background_rect = pygame.Rect(x_start - block_size / 2, y_start, text_width + block_size, text_height)
    text_to_blit = which_font.render(text, True, color)
    screen.fill(WHITE, background_rect)
    screen.blit(text_to_blit, (x_start, y_start))

# ===========MANUAL SHIPS CREATION SECTION==============


def check_ships_numbers(ship, num_ships_list):
    """ Makes sure that there are certain numbers of certain ships (1-4, 2-3, 3-2, 4-1)
    """
    # This function checks if there is the equality of (5 - len(ship)) == index[len(ship)-1]
    # if yes, then print "This ship is not valid, we already have enough of such ships"
    # We could send a more elaborate message - "We don't need more 4-ships, try creating some more 3-ships..."
    # If not (if equality is false), then add this ship to our ships_to_draw_list
    # and increment the element at the proper index
    return (5 - len(ship)) > num_ships_list[len(ship)-1]


def ship_is_valid(ship_set, blocks_for_manual_drawing):
    """Check if a new ship is not adjacent to any previus ship
    and if yes then calls another function to check if the numbers of ships are valid
    """
    # if the set of all blocks in new ship does not intersect with the set of unavailable blocks for manual drawing
    # (which is updated every time a new ships is drawn - write this function to add all blocks around new ship to such set!)
    # then call check_ships_numbers to see if there are proper numbers of each ship.
    #    return check_ships_numbers(ship)
    return ship_set.isdisjoint(blocks_for_manual_drawing)


def update_used_blocks(ship, used_blocks_set):
    for block in ship:
        for i in range(-1, 2):
            for j in range(-1, 2):
                used_blocks_set.add((block[0]+i, block[1]+j))
    return used_blocks_set


def restore_used_blocks(deleted_ship, used_blocks_set):
    for block in deleted_ship:
        for i in range(-1, 2):
            for j in range(-1, 2):
                used_blocks_set.discard((block[0]+i, block[1]+j))
    return used_blocks_set


computer = AutoShips(0)
computer_ships_working = copy.deepcopy(computer.ships)

message_one = "How do you want to create your ships? Click the button"
undo_message = "To undo the last ship click the button"
auto_button_place = left_margin + 17*block_size
manual_button_place = left_margin + 20*block_size
undo_button_place = left_margin + 12*block_size

auto_button = Button(auto_button_place, "AUTO", message_one)
manual_button = Button(manual_button_place, "MANUAL", None)
undo_button = Button(undo_button_place, "UNDO LAST SHIP", undo_message)
#auto_button_rect = pygame.Rect(auto_button.rect_for_draw)
#manual_button_rect = pygame.Rect(manual_button.rect_for_draw)
#undo_button_rect = pygame.Rect(undo_button.rect_for_draw)


def main():
    # last_rect = ((0, 0), (0, 0))
    ships_creation_not_settled = True
    ships_not_created = True
    drawing = False
    game_over = False
    computer_turn = False

    start = (0, 0)
    ship_size = (0, 0)
    rect_for_grids = (0, 0, size[0], upper_margin+12*block_size)
    rect_for_message_and_buttons = (
        0, upper_margin+11*block_size, size[0], 5*block_size)
    message_rect_drawing_ships = (undo_button.rect_for_draw[0]+undo_button.rect_for_draw[2], upper_margin+11*block_size, size[0]-(
        undo_button.rect_for_draw[0]+undo_button.rect_for_draw[2]), 4*block_size)
    message_rect_computer = (left_margin-2*block_size,
                            upper_margin+11*block_size, 14*block_size, 4*block_size)
    message_rect_human = (left_margin+15*block_size,
                        upper_margin+11*block_size, 10*block_size, 4*block_size)

    human_ships_to_draw = []
    human_ships_set = set()
    used_blocks_for_manual_drawing = set()
    # A list where element at each index will have the number of ships of the length index+1
    # (index 0 - number of one-block ships, index 3 - number of 4-block-ships, etc.).
    # Then update (increment) each respective index when respective ships is created .
    num_ships_list = [0, 0, 0, 0]
    
    screen.fill(WHITE)
    # We draw grids before while loops to optimize the RAM - 
    # no need to redraw grids each time dozens times in a second
    computer_grid = Grid("КОМПЬЮТЕР", 0)
    human_grid = Grid("ЧЕЛОВЕК", 15)
    # draw_ships(computer.ships)

    while ships_creation_not_settled:
        # print("Started ships_creation_not_settled loop")
    
        # Create two buttons to choose how to create ships - auto or manually
        auto_button.draw_button()
        manual_button.draw_button()
        auto_button.change_color_on_hover()
        manual_button.change_color_on_hover()
        auto_button.print_message_for_button()

        # Checking for mouse click
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                ships_creation_not_settled = False
                ships_not_created = False
            # If "AUTO" button is selected - create human ships automatically
            elif event.type == pygame.MOUSEBUTTONDOWN and auto_button.rect.collidepoint(mouse):
                print("Clicked auto!", event.pos)
                human = AutoShips(15)
                human_ships_to_draw = human.ships
                human_ships_working = copy.deepcopy(human.ships)
                human_ships_set = human.ships_set
                ships_not_created = False
                ships_creation_not_settled = False
            # If "MANUAL" button is selected - break the loop and go into the next one
            elif event.type == pygame.MOUSEBUTTONDOWN and manual_button.rect.collidepoint(mouse):
                print("Clicked manual!", event.pos)
                ships_creation_not_settled = False
        pygame.display.update()
        # This screen.fill must be here in the end,
        # otherwise we will have remains of the buttons in the next while loop!
        screen.fill(WHITE, rect_for_message_and_buttons)

    while ships_not_created:
        # These three drawing of grids and screen.fill are needed to draw new ships (rect)
        # and update the screen to get rid of temp rects when we draw neew ship with a mouse!
        screen.fill(WHITE, rect_for_grids)
        computer_grid = Grid("COMPUTER", 0)
        human_grid = Grid("HUMAN", 15)
        undo_button.draw_button()
        undo_button.print_message_for_button()
        # Changing color of the button while hovering over with a mouse
        mouse = pygame.mouse.get_pos()
        undo_button.change_color_on_hover()
        
        # Make Undo button disabled when there are no ships to undo
        if not human_ships_to_draw:
            undo_button.draw_button(LIGHT_GRAY)
        # Start of ships creation section
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ships_not_created = False
                game_over = True
            elif undo_button.rect.collidepoint(mouse) and event.type == pygame.MOUSEBUTTONDOWN:
                print("Undo clicked!")
                if human_ships_to_draw:
                    deleted_ship = human_ships_to_draw.pop()
                    num_ships_list[len(deleted_ship)-1] -= 1
                    used_blocks_for_manual_drawing = restore_used_blocks(
                        deleted_ship, used_blocks_for_manual_drawing)
                print(num_ships_list)
                print(human_ships_to_draw)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                drawing = True
                x_start, y_start = event.pos
                start = x_start, y_start
                ship_size = (0, 0)
                print(f"Button down at {x_start, y_start}!")

            elif drawing and event.type == pygame.MOUSEMOTION:
                print("Started motion")
                x_end, y_end = event.pos
                end = x_end, y_end
                ship_size = x_end - x_start, y_end - y_start

            # drawing is crucial here - otherwise it counts the previouc click up after clicking on MANUAL button!
            elif drawing and event.type == pygame.MOUSEBUTTONUP:
                x_end, y_end = event.pos
                drawing = False
                ship_size = (0, 0)
                print(f"Button up at {x_end, y_end}!")
                start_block = ((x_start - left_margin) // block_size +
                               1, (y_start - upper_margin)//block_size + 1)
                end_block = ((x_end - left_margin) // block_size +
                             1, (y_end - upper_margin)//block_size + 1)
                if start_block > end_block:
                    start_block, end_block = end_block, start_block
                temp_ship = []
                if 15 < start_block[0] < 26 and 0 < start_block[1] < 11 and 15 < end_block[0] < 26 and 0 < end_block[1] < 11:
                    screen.fill(WHITE, message_rect_drawing_ships)
                    if start_block[0] == end_block[0] and (end_block[1] - start_block[1]) < 4:
                        for block in range(start_block[1], end_block[1]+1):
                            temp_ship.append((start_block[0], block))
                    elif start_block[1] == end_block[1] and (end_block[0] - start_block[0]) < 4:
                        for block in range(start_block[0], end_block[0]+1):
                            temp_ship.append((block, start_block[1]))
                    else:
                        show_messages_at_rect_center(
                            "SHIP IS TOO LARGE! Try again!", message_rect_drawing_ships)
                        #print("SHIP IS TOO LARGE! Try again!")
                else:
                    show_messages_at_rect_center(
                        "SHIP IS BEYOND YOUR GRID! Try again!", message_rect_drawing_ships)
                    #print("SHIP IS BEYOND YOUR GRID! Try again!")
                if temp_ship:
                    temp_ship_set = set(temp_ship)
                    if ship_is_valid(temp_ship_set, used_blocks_for_manual_drawing):
                        if check_ships_numbers(temp_ship, num_ships_list):
                            num_ships_list[len(temp_ship)-1] += 1
                            print(num_ships_list)
                            human_ships_to_draw.append(temp_ship)
                            print(human_ships_to_draw)
                            human_ships_set |= temp_ship_set
                            print(human_ships_set)
                            used_blocks_for_manual_drawing = update_used_blocks(
                                temp_ship, used_blocks_for_manual_drawing)
                        else:
                            show_messages_at_rect_center(
                                f"There already are enough of {len(temp_ship)} ships!", message_rect_drawing_ships)
                            #print(f"There already are enough of {len(temp_ship)} ships. Try again with different ship")
                    else:
                        show_messages_at_rect_center(
                            "SHIPS ARE TOUCHING! Try again", message_rect_drawing_ships)
                        #print("SHIPS ARE TOUCHING! Try again")
            if len(human_ships_to_draw) == 10:
                human_ships_working = copy.deepcopy(human_ships_to_draw)
                ships_not_created = False
                screen.fill(WHITE, rect_for_message_and_buttons)
        pygame.draw.rect(screen, INK, (start, ship_size), 3)
        # print("Here are your ships", human_ships_to_draw)
        draw_ships(human_ships_to_draw)
        pygame.display.update()

    while not game_over:
        # print("Started game main loop")
        # computer_grid = Grid("COMPUTER", 0)
        # human_grid = Grid("HUMAN", 15)
        # draw_ships(computer.ships)
        # TODO This should draw only computer destroyed ships.
        # Check if the list contains human ships or not!
        draw_ships(destroyed_computer_ships)
        # print(destroyed_computer_ships)
        draw_ships(human_ships_to_draw)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            # Player shoots and is checked for hit or miss
            elif not computer_turn and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # There should be stict '<' and not <=! Oterwise we will shoot at grid's lines
                # and the dot will be put outside of the grid!
                if (left_margin < x < left_margin + 10*block_size) and (upper_margin < y < upper_margin + 10*block_size):
                    fired_block = ((x - left_margin) // block_size + 1,
                                   (y - upper_margin) // block_size + 1)
                    computer_turn = not check_hit_or_miss(fired_block, computer_ships_working, False, computer.ships, computer.ships_set)
                    draw_from_dotted_set(dotted_set)
                    draw_hit_blocks(hit_blocks)
                    screen.fill(WHITE, message_rect_computer)
                    show_messages_at_rect_center(
                        f"Your last shot: {LETTERS[fired_block[0]-1] + str(fired_block[1])}", message_rect_computer, color=BLACK)
                    # pygame.time.delay(200)
                else:
                    show_messages_at_rect_center(
                        "Your shot is outside of grid! Try again", message_rect_computer)
                # screen.fill((255, 0, 0), last_rect)
        # pygame.time.delay(500)

        if computer_turn:
            # print(human_ships_working)
            set_to_shoot_from = computer_available_to_fire_set
            if around_last_computer_hit_set:
                set_to_shoot_from = around_last_computer_hit_set
            fired_block = computer_shoots(set_to_shoot_from)
            computer_turn = check_hit_or_miss(fired_block, human_ships_working, True, human_ships_to_draw, human_ships_set)
            draw_from_dotted_set(dotted_set)
            draw_hit_blocks(hit_blocks)
            screen.fill(WHITE, message_rect_human)
            show_messages_at_rect_center(
                f"Computer's last shot: {LETTERS[fired_block[0]-16] + str(fired_block[1])}", message_rect_human, color=BLACK)
            # This is just for testing and fun. It's not working as planned.
            last_rect = ((left_margin+15*block_size, upper_margin +
                          12*block_size), (10*block_size, block_size))
            # screen.fill((255, 0, 0), last_rect)
        else:
            last_rect = ((left_margin, upper_margin+12*block_size),
                         (10*block_size, block_size))
            # screen.fill((255, 0, 0), last_rect)

        if not computer.ships_set:
            last_rect = ((0, 0), (0, 0))
            show_messages_at_rect_center(
                "YOU WON!", (0, 0, size[0], size[1]), game_over_font)
            # game_over = True
        if not human_ships_set:
            last_rect = ((0, 0), (0, 0))
            show_messages_at_rect_center(
                "YOU LOST!", (0, 0, size[0], size[1]), game_over_font)
            # game_over = True

        pygame.display.update()


main()
pygame.quit()
