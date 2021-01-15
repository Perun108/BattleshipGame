import pygame
import random
import copy

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

block_size = 50
left_margin = 100
upper_margin = 80

size = (left_margin+30*block_size, upper_margin+15*block_size)
LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

pygame.init()

screen = pygame.display.set_mode(size)
pygame.display.set_caption("Morskoy Boy")

font_size = int(block_size / 1.5)

font = pygame.font.SysFont('notosans', font_size)
computer_available_to_fire_set = {(x, y) for x in range(16, 25) for y in range(1, 11)}
around_last_computer_hit_set = set()
hit_blocks = set()
dotted_set = set()
dotted_set_for_computer_not_to_shoot = set()
hit_blocks_for_computer_not_to_shoot = set()
last_hits_list = []
destroyed_ships_list = []


class Grid:
    def __init__(self, title, offset):
        self.title = title
        self.offset = offset
        self.draw_grid()
        self.sign_grid()
        self.add_nums_letters_to_grid()

    def draw_grid(self):
        for i in range(11):
            # Horizontal lines
            pygame.draw.line(screen, BLACK, (left_margin+self.offset, upper_margin+i*block_size),
                             (left_margin+10*block_size+self.offset, upper_margin+i*block_size), 1)
            # Vertical lines
            pygame.draw.line(screen, BLACK, (left_margin+i*block_size+self.offset, upper_margin),
                             (left_margin+i*block_size+self.offset, upper_margin+10*block_size), 1)

    def add_nums_letters_to_grid(self):
        for i in range(10):
            num_ver = font.render(str(i+1), True, BLACK)
            letters_hor = font.render(LETTERS[i], True, BLACK)
            num_ver_width = num_ver.get_width()
            num_ver_height = num_ver.get_height()
            letters_hor_width = letters_hor.get_width()

            # Ver num grid1
            screen.blit(num_ver, (left_margin - (block_size//2+num_ver_width//2)+self.offset,
                                  upper_margin + i*block_size + (block_size//2 - num_ver_height//2)))
            # Hor letters grid1
            screen.blit(letters_hor, (left_margin + i*block_size + (block_size //
                                                                    2 - letters_hor_width//2)+self.offset, upper_margin + 10*block_size))

    def sign_grid(self):
        player = font.render(self.title, True, BLACK)
        sign_width = player.get_width()
        screen.blit(player, (left_margin + 5*block_size - sign_width //
                             2+self.offset, upper_margin - block_size//2 - font_size))


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


def draw_ships(ships_coordinates_list):
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



def computer_shoots(set_to_shoot_from):
    pygame.time.delay(500)
    computer_fired_block = random.choice(tuple(set_to_shoot_from))
    computer_available_to_fire_set.discard(computer_fired_block)
    return computer_fired_block


def check_hit_or_miss(fired_block, opponents_ships_list, computer_turn, opponents_ships_list_original_copy, opponents_ships_set):
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
                    destroyed_ships_list.append(computer.ships[ind])
            return True
    add_missed_block_to_dotted_set(fired_block)
    if computer_turn:
        update_around_last_computer_hit(fired_block, False)
    return False


def add_missed_block_to_dotted_set(fired_block):
    dotted_set.add(fired_block)
    dotted_set_for_computer_not_to_shoot.add(fired_block)


def update_destroyed_ships(ind, computer_turn, opponents_ships_list_original_copy):
    ship = sorted(opponents_ships_list_original_copy[ind])
    for i in range(-1, 1):
        update_dotted_and_hit_sets(ship[i], computer_turn, False)


def update_around_last_computer_hit(fired_block, computer_hits=True):
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
    xhit, yhit = fired_block
    if 16 < xhit:
        around_last_computer_hit_set.add((xhit-1, yhit))
    if xhit < 25:
        around_last_computer_hit_set.add((xhit+1, yhit))
    if 1 < yhit:
        around_last_computer_hit_set.add((xhit, yhit-1))
    if yhit < 10:
        around_last_computer_hit_set.add((xhit, yhit+1))


def computer_hits_twice():
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
            if 16 < x1:
                new_around_last_hit_set.add((x1 - 1, y1))
            if x2 < 25:
                new_around_last_hit_set.add((x2 + 1, y1))
    return new_around_last_hit_set


def update_dotted_and_hit_sets(fired_block, computer_turn, diagonal_only=True):
    global dotted_set
    x, y = fired_block
    a, b = 0, 11
    if computer_turn:
        a += 15
        b += 15
        hit_blocks_for_computer_not_to_shoot.add(fired_block)
    hit_blocks.add((x, y))
    for i in range(-1, 2):
        for j in range(-1, 2):
            if diagonal_only:
                if i != 0 and j != 0 and a < x + i < b and 0 < y + j < 11:
                    dotted_set.add((x+i, y+j))
                    if computer_turn:
                        dotted_set_for_computer_not_to_shoot.add(
                            (fired_block[0]+i, y+j))
            else:
                if a < x + i < b and 0 < y + j < 11:
                    dotted_set.add((x+i, y+j))
                    if computer_turn:
                        dotted_set_for_computer_not_to_shoot.add((
                            fired_block[0]+i, y+j))
    dotted_set -= hit_blocks


def draw_from_dotted_set(dotted_set):
    for elem in dotted_set:
        pygame.draw.circle(screen, BLACK, (block_size*(
            elem[0]-0.5)+left_margin, block_size*(elem[1]-0.5)+upper_margin), block_size//6)


def draw_hit_blocks(hit_blocks):
    for block in hit_blocks:
        x1 = block_size * (block[0]-1) + left_margin
        y1 = block_size * (block[1]-1) + upper_margin
        pygame.draw.line(screen, BLACK, (x1, y1),
                         (x1+block_size, y1+block_size), block_size//6)
        pygame.draw.line(screen, BLACK, (x1, y1+block_size),
                         (x1+block_size, y1), block_size//6)


computer = AutoShips(0)
human = AutoShips(15)
computer_ships_working = copy.deepcopy(computer.ships)
human_ships_working = copy.deepcopy(human.ships)


def main():
    game_over = False
    computer_turn = False

    screen.fill(WHITE)
    computer_grid = Grid("COMPUTER", 0)
    human_grid = Grid("HUMAN", 15*block_size)
    # draw_ships(computer.ships)
    draw_ships(human.ships)
    pygame.display.update()

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif not computer_turn and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if (left_margin <= x <= left_margin + 10*block_size) and (upper_margin <= y <= upper_margin + 10*block_size):
                    fired_block = ((x - left_margin) // block_size + 1,
                                   (y - upper_margin) // block_size + 1)
                computer_turn = not check_hit_or_miss(fired_block, computer_ships_working, False, computer.ships, computer.ships_set)

        if computer_turn:
            set_to_shoot_from = computer_available_to_fire_set
            if around_last_computer_hit_set:
                set_to_shoot_from = around_last_computer_hit_set
            fired_block = computer_shoots(set_to_shoot_from)
            computer_turn = check_hit_or_miss(fired_block, human_ships_working, True, human.ships, human.ships_set)
            

        draw_from_dotted_set(dotted_set)
        draw_hit_blocks(hit_blocks)
        draw_ships(destroyed_ships_list)
        pygame.display.update()


main()
pygame.quit()
