import random
#y,x
BOARD_SIZE = (8,8)
COLOR_NAMES = {
    "orange":"#EF8D1F",
    "blue":"#1F35EF",
    "purple":"#A93CF1",
    "pink":"#F13CB6",
    "yellow":"#DFEF0D",
    "red":"#DA100D",
    "green":"#79C10D",
    "brown":"#5E340C",
               }
COLORS = list(COLOR_NAMES.values())
PLAYER_NAME = lambda a: "White" if a else "Black"
BLACK = False
WHITE = True

#gamemode: 0 = PvP,1 = PvE,2 = EvE

#TODO add rule about if peace cant move

class Board:

    def __init__(self, board_size, bots=[]):
        self.board_size = board_size
        self.board_colors = COLORS if max(self.board_size) <= len(COLORS) else color_gen(self.board_size)
        self.units = {BLACK:[], WHITE:[]}
        self.board = self._gen_board()
        self.turn_count = 0
        self.turn = False
        self.game_over = False
        self.bots = bots
        self.game_mode = len(self.bots)
        self.last_moved_color = None
        self.player_color = False if self.game_mode == 0 else not self.bots[0].bot_color
        #self.print()

    def get_units(self):
        return [*self.units[BLACK], *self.units[WHITE]]

    def _gen_board(self):

        board = {}

        for x in range(self.board_size[1]):
            board[(0, x)] = Cell(x)

        for y in range(self.board_size[0]-1):
            for x in range(self.board_size[1]):
                c_index = board[(y, x)].color_index
                board[(y+1,(x+1+(c_index*2))%self.board_size[1])] = Cell(c_index)

        for x in range(self.board_size[1]):
            b_unit = board[(0, x)].unit = Unit(BLACK, board[(0, x)].color_index,(0, x))
            w_unit = board[(self.board_size[0]-1, x)].unit = Unit(WHITE, board[(self.board_size[0]-1, x)].color_index,(self.board_size[0]-1, x))
            self.units[BLACK].append(b_unit)
            self.units[WHITE].append(w_unit)
        return board

    def print(self):
        for y in range(self.board_size[0]):
            s = "["
            for x in range(self.board_size[1]):
                st = "X" if self.board[(y, x)].unit is None else self.board[(y, x)].unit.color_index
                s += f"{st},"
            s += "]"
            print(s)

    def calc_moves(self, origin):
        if self.board[origin].unit is None:
            return [], origin

        #white or black determens the direction of movement
        height, width = self.board_size
        unit = self.board[origin].unit
        start_y, start_x = unit.location
        direction = -1 if unit.player else 1
        moves = []

        #updown
        y_range = range(start_y-1, -1, -1) if unit.player else range(start_y+1, height)
        for y in y_range:
            if self.board[(y, start_x)].unit is not None:
                break
            moves.append((y, start_x))

        #diag_movement
        #y+(i*dir),x+i |y+(i*dir),x-i
        left = True
        right = True
        for i in range(1, width):
            if not right and not left:
                break
            loc_r = (start_y+(i*direction), start_x+i)
            loc_l = (start_y+(i*direction), start_x-i)
            if right and loc_r in self.board:
                if self.board[loc_r].unit is not None:
                    right = False
                else:
                    moves.append(loc_r)
            if left and loc_l in self.board:
                if self.board[loc_l].unit is not None:
                    left = False
                else:
                    moves.append(loc_l)
        #print(f"Move options are {moves}")
        return moves, origin

    def calc_all_moves(self):
        moves = []
        for unit in self.units[self.turn]:
            if self.last_moved_color is None or self.last_moved_color == unit.color_index:
                moves.append(self.calc_moves(unit.location))
        return moves

    def calc_amount_of_moves(self):
        return sum([len(element[0]) for element in self.calc_all_moves()])

    def _move_validation(self, unit, dest):
        #check turn, lastmovedcolor and possible move
        if self.turn == unit.player:
            if self.last_moved_color is None or unit.color_index == self.last_moved_color:
                return dest in self.calc_moves(unit.location)[0]
        return False

    def move(self, unit, dest):
        #print(f"There are {str(self.calc_amount_of_moves())} possible moves")
        if self.calc_amount_of_moves() == 0:
            unit = [u for u in self.units[self.turn] if u.color_index == self.last_moved_color][0]
            self.last_moved_color = self.board[unit.location].color_index
            self.turn = not self.turn
            self.turn_count += 1

        if self._move_validation(unit, dest):
            self.board[dest].unit = unit
            self.board[unit.location].unit = None
            unit.location = dest
            self.last_moved_color = self.board[dest].color_index
            self.turn = not self.turn
            self.turn_count += 1
            print(f"Turn {self.turn_count}: {PLAYER_NAME(self.turn)}")

            #win condition check
            if unit.location[0] == 0 or unit.location[0] == self.board_size[0]-1:
                self.game_over = True
                print(f"{PLAYER_NAME(self.turn)} WINS!!!")
            return True
        return False

    def move_logic(self, unit=None, dest=None):
        bot_units = self.units[self.turn]
        if self.last_moved_color is None:
            unit_to_move = None
        else:
            unit_to_move = [u for u in bot_units if u.color_index == self.last_moved_color][0]
        if self.game_mode == 1 and not self.player_color == self.turn:
            self.bots[0].bot_turn(self.units, unit_to_move, self)
        elif self.game_mode == 2:
            self.bots[int(self.turn)].bot_turn(self.units, unit_to_move, self)
            return True
        else:
            return self.move(unit, dest)


class Cell:
    def __init__(self, color_index, unit=None):
        self.color_index = color_index
        self.unit = unit

    def __repr__(self):
        return f"[Color:{self.color_index},Unit:{self.unit if self.unit is not None else ''}]"


class Unit:
    def __init__(self, player, color_index, location):
        self.player = player
        self.color_index = color_index
        self.location = location

    def __repr__(self):
        return f"[Player:{PLAYER_NAME(self.player)},Color:{self.color_index}]"


def color_gen(board_size):
    Colors = []
    length = max(*board_size)
    for i in range(length):
        Colors.append("#" + str(hex(random.randint(0,16777215))[2:]))
    return Colors


if __name__ == "__main__":
    game_board = Board(BOARD_SIZE)
