import pygame
import random
import copy

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

block_size = 50
left_margin = 100
upper_margin = 80

size = (left_margin+30*block_size, upper_margin+15*block_size)

pygame.init()

screen = pygame.display.set_mode(size)
pygame.display.set_caption("Morskoy Boy")

font_size = int(block_size / 1.5)

font = pygame.font.SysFont('notosans', font_size)
computer_available_to_fire_set = set((a, b)
                                     for a in range(1, 11) for b in range(1, 11))
around_last_computer_hit_set = set()
hit_blocks = set()
dotted_set = set()
dotted_set_for_computer_to_shoot = set()
hit_blocks_for_computer_to_shoot = set()
last_hits_list = []
destroyed_ships_list = []


class ShipsOnGrid:
    def __init__(self):
        self.available_blocks = set((a, b)
                                    for a in range(1, 11) for b in range(1, 11))
        self.ships_set = set()
        self.ships = self.populate_grid()

    def create_start_block(self, available_blocks):
        x_or_y = random.randint(0, 1)
        str_rev = random.choice((-1, 1))
        x, y = random.choice(tuple(available_blocks))
        return x, y, x_or_y, str_rev

    def create_ship(self, number_of_blocks, available_blocks):
        ship_coordinates = []
        x, y, x_or_y, str_rev = self.create_start_block(available_blocks)
        for _ in range(number_of_blocks):
            ship_coordinates.append((x, y))
            if not x_or_y:
                str_rev, x = self.add_block_to_ship(
                    x, str_rev, x_or_y, ship_coordinates)
            else:
                str_rev, y = self.add_block_to_ship(
                    y, str_rev, x_or_y, ship_coordinates)
        if self.is_ship_valid(ship_coordinates):
            return ship_coordinates
        return self.create_ship(number_of_blocks, available_blocks)

    def add_block_to_ship(self, coor, str_rev, x_or_y, ship_coordinates):
        if (coor <= 1 and str_rev == -1) or (coor >= 10 and str_rev == 1):
            str_rev *= -1
            return str_rev, ship_coordinates[0][x_or_y] + str_rev
        else:
            return str_rev, ship_coordinates[-1][x_or_y] + str_rev

    def is_ship_valid(self, new_ship):
        ship = set(new_ship)
        return ship.issubset(self.available_blocks)

    def add_new_ship_to_set(self, new_ship):
        for elem in new_ship:
            self.ships_set.add(elem)

    def update_available_blocks_for_creating_ships(self, new_ship):
        for elem in new_ship:
            for k in range(-1, 2):
                for m in range(-1, 2):
                    if 0 < (elem[0]+k) < 11 and 0 < (elem[1]+m) < 11:
                        self.available_blocks.discard((elem[0]+k, elem[1]+m))

    def populate_grid(self):
        ships_coordinates_list = []
        for number_of_blocks in range(4, 0, -1):
            for _ in range(5-number_of_blocks):
                new_ship = self.create_ship(
                    number_of_blocks, self.available_blocks)
                ships_coordinates_list.append(new_ship)
                self.add_new_ship_to_set(new_ship)
                self.update_available_blocks_for_creating_ships(new_ship)
        return ships_coordinates_list


computer = ShipsOnGrid()
human = ShipsOnGrid()
computer_ships_working = copy.deepcopy(computer.ships)
human_ships_working = copy.deepcopy(human.ships)


def draw_ships(ships_coordinates_list):
    for elem in ships_coordinates_list:
        ship = sorted(elem)
        x_start = ship[0][0]
        y_start = ship[0][1]
        # Vert
        if len(ship) > 1 and ship[0][0] == ship[1][0]:
            ship_width = block_size
            ship_height = block_size * len(ship)
        # Hor and 1block
        else:
            ship_width = block_size * len(ship)
            ship_height = block_size
        x = block_size * (x_start - 1) + left_margin
        y = block_size * (y_start - 1) + upper_margin
        if ships_coordinates_list == human.ships:
            x += 15 * block_size
        pygame.draw.rect(
            screen, BLACK, ((x, y), (ship_width, ship_height)), width=block_size//10)


def draw_grid():
    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    for i in range(11):
        # Hor grid1
        pygame.draw.line(screen, BLACK, (left_margin, upper_margin+i*block_size),
                         (left_margin+10*block_size, upper_margin+i*block_size), 1)
        # Vert grid1
        pygame.draw.line(screen, BLACK, (left_margin+i*block_size, upper_margin),
                         (left_margin+i*block_size, upper_margin+10*block_size), 1)
        # Hor grid2
        pygame.draw.line(screen, BLACK, (left_margin+15*block_size, upper_margin +
                                         i*block_size), (left_margin+25*block_size, upper_margin+i*block_size), 1)
        # Vert grid2
        pygame.draw.line(screen, BLACK, (left_margin+(i+15)*block_size, upper_margin),
                         (left_margin+(i+15)*block_size, upper_margin+10*block_size), 1)

        if i < 10:
            num_ver = font.render(str(i+1), True, BLACK)
            letters_hor = font.render(letters[i], True, BLACK)

            num_ver_width = num_ver.get_width()
            num_ver_height = num_ver.get_height()
            letters_hor_width = letters_hor.get_width()

            # Ver num grid1
            screen.blit(num_ver, (left_margin - (block_size//2+num_ver_width//2),
                                  upper_margin + i*block_size + (block_size//2 - num_ver_height//2)))
            # Hor letters grid1
            screen.blit(letters_hor, (left_margin + i*block_size + (block_size //
                                                                    2 - letters_hor_width//2), upper_margin + 10*block_size))
            # Ver num grid2
            screen.blit(num_ver, (left_margin - (block_size//2+num_ver_width//2) + 15 *
                                  block_size, upper_margin + i*block_size + (block_size//2 - num_ver_height//2)))
            # Hor letters grid2
            screen.blit(letters_hor, (left_margin + i*block_size + (block_size//2 -
                                                                    letters_hor_width//2) + 15*block_size, upper_margin + 10*block_size))


def sign_grids():
    player1 = font.render("COMPUTER", True, BLACK)
    player2 = font.render("HUMAN", True, BLACK)
    sign1_width = player1.get_width()
    sign2_width = player2.get_width()
    screen.blit(player1, (left_margin + 5*block_size - sign1_width //
                          2, upper_margin - block_size//2 - font_size))
    screen.blit(player2, (left_margin + 20*block_size - sign2_width //
                          2, upper_margin - block_size//2 - font_size))


def computer_shoots(set_to_shoot_from):
    pygame.time.delay(500)
    computer_fired_block = random.choice(tuple(set_to_shoot_from))
    computer_available_to_fire_set.discard(computer_fired_block)
    return check_hit_or_miss(computer_fired_block, human_ships_working, True)


def check_hit_or_miss(fired_block, opponents_ships_list, computer_turn, diagonal_only=True):
    for elem in opponents_ships_list:
        if fired_block in elem:
            update_dotted_and_hit_sets(
                fired_block, computer_turn, diagonal_only=True)
            ind = opponents_ships_list.index(elem)

            if len(elem) == 1:
                update_dotted_and_hit_sets(
                    fired_block, computer_turn, diagonal_only=False)

            elem.remove(fired_block)

            if computer_turn:
                last_hits_list.append(fired_block)
                human.ships_set.discard(fired_block)
                update_around_last_computer_hit(fired_block)
            else:
                computer.ships_set.discard(fired_block)

            if not elem:
                draw_destroyed_ships(ind, opponents_ships_list, computer_turn)
                if computer_turn:
                    last_hits_list.clear()
                    around_last_computer_hit_set.clear()
                else:
                    destroyed_ships_list.append(computer.ships[ind])

            return True
    put_dot_on_missed_block(fired_block, computer_turn)
    if computer_turn:
        update_around_last_computer_hit(fired_block, False)
    return False


def put_dot_on_missed_block(fired_block, computer_turn=False):
    if not computer_turn:
        dotted_set.add(fired_block)
    else:
        dotted_set.add((fired_block[0] + 15, fired_block[1]))
        dotted_set_for_computer_to_shoot.add(fired_block)


def draw_destroyed_ships(ind, opponents_ships_list, computer_turn, diagonal_only=False):
    if opponents_ships_list == computer_ships_working:
        ships_list = computer.ships
    elif opponents_ships_list == human_ships_working:
        ships_list = human.ships
    ship = sorted(ships_list[ind])
    for i in range(-1, 1):
        update_dotted_and_hit_sets(ship[i], computer_turn, diagonal_only)


def update_around_last_computer_hit(fired_block, computer_hits=True):
    global around_last_computer_hit_set, computer_available_to_fire_set
    if computer_hits and fired_block in around_last_computer_hit_set:
        new_around_last_hit_set = set()
        for i in range(len(last_hits_list)-1):
            if last_hits_list[i][0] == last_hits_list[i+1][0]:
                if 1 < last_hits_list[i][1]:
                    new_around_last_hit_set.add(
                        (last_hits_list[i][0], last_hits_list[i][1] - 1))
                if 1 < last_hits_list[i+1][1]:
                    new_around_last_hit_set.add(
                        (last_hits_list[i][0], last_hits_list[i+1][1] - 1))
                if last_hits_list[i][1] < 10:
                    new_around_last_hit_set.add(
                        (last_hits_list[i][0], last_hits_list[i][1] + 1))
                if last_hits_list[i+1][1] < 10:
                    new_around_last_hit_set.add(
                        (last_hits_list[i][0], last_hits_list[i+1][1] + 1))

            elif last_hits_list[i][1] == last_hits_list[i+1][1]:
                if 1 < last_hits_list[i][0]:
                    new_around_last_hit_set.add(
                        (last_hits_list[i][0] - 1, last_hits_list[i][1]))
                if 1 < last_hits_list[i+1][0]:
                    new_around_last_hit_set.add(
                        (last_hits_list[i+1][0] - 1, last_hits_list[i][1]))
                if last_hits_list[i][0] < 10:
                    new_around_last_hit_set.add(
                        (last_hits_list[i][0] + 1, last_hits_list[i][1]))
                if last_hits_list[i+1][0] < 10:
                    new_around_last_hit_set.add(
                        (last_hits_list[i+1][0] + 1, last_hits_list[i][1]))

        around_last_computer_hit_set = new_around_last_hit_set

    elif computer_hits and fired_block not in around_last_computer_hit_set:
        xhit, yhit = fired_block
        if 1 < xhit:
            around_last_computer_hit_set.add((xhit-1, yhit))
        if 1 < yhit:
            around_last_computer_hit_set.add((xhit, yhit-1))
        if xhit < 10:
            around_last_computer_hit_set.add((xhit+1, yhit))
        if yhit < 10:
            around_last_computer_hit_set.add((xhit, yhit+1))

    elif not computer_hits:
        around_last_computer_hit_set.discard(fired_block)

    around_last_computer_hit_set -= dotted_set_for_computer_to_shoot
    around_last_computer_hit_set -= hit_blocks_for_computer_to_shoot
    computer_available_to_fire_set -= around_last_computer_hit_set
    computer_available_to_fire_set -= dotted_set_for_computer_to_shoot


def update_dotted_and_hit_sets(fired_block, computer_turn, diagonal_only=True):
    global dotted_set
    x, y = fired_block
    a, b = 0, 11
    if computer_turn:
        x += 15
        a += 15
        b += 15
        hit_blocks_for_computer_to_shoot.add(fired_block)
    hit_blocks.add((x, y))
    for i in range(-1, 2):
        for j in range(-1, 2):
            if diagonal_only:
                if i != 0 and j != 0 and a < x + i < b and 0 < y + j < 11:
                    dotted_set.add((x+i, y+j))
                    if computer_turn:
                        dotted_set_for_computer_to_shoot.add(
                            (fired_block[0]+i, y+j))
            else:
                if a < x + i < b and 0 < y + j < 11:
                    dotted_set.add((x+i, y+j))
                    if computer_turn:
                        dotted_set_for_computer_to_shoot.add((
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


def main():
    game_over = False
    computer_turn = False

    screen.fill(WHITE)
    draw_grid()
    sign_grids()
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
                computer_turn = not check_hit_or_miss(
                    fired_block, computer_ships_working, computer_turn)

        if computer_turn:
            if around_last_computer_hit_set:
                computer_turn = computer_shoots(around_last_computer_hit_set)
            else:
                computer_turn = computer_shoots(computer_available_to_fire_set)

        draw_from_dotted_set(dotted_set)
        draw_hit_blocks(hit_blocks)
        draw_ships(destroyed_ships_list)
        pygame.display.update()


main()
pygame.quit()
