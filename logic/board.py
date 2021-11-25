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



class Board:

    def __init__(self, board_size, bots=[]):
        self.board_size = board_size
        self.board_colors = COLORS
        self.units = {BLACK:[], WHITE:[]}
        self.board = self._gen_board()
        self.turn_count = 0
        self.game_over = False
        self.bots = Board._gen_bots(bots)
        self.last_moved_color = None
        self.player_color = False if self.game_mode == 0 else not self.bots[0].bot_color

    @property
    def game_mode(self):
        return len(self.bots)

    def get_turn(self):
        return False if self.turn_count % 2 == 0 else True

    def get_turn_count(self):
        return self.turn_count

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

    @staticmethod
    def _gen_bots(bots):
        new_bots = []
        for player_color, bot_class, bot_args in bots:
            if bot_args:
                new_bots.append(bot_class(bot_color=player_color, *bot_args))
            else:
                new_bots.append(bot_class(bot_color=player_color))
        print(f"bots: {new_bots}")
        return new_bots

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
        if self.game_over:
            return []
        moves = []
        for unit in self.units[self.get_turn()]:
            if self.last_moved_color is None or self.last_moved_color == unit.color_index:
                moves.append(self.calc_moves(unit.location))
        return moves

    def calc_amount_of_moves(self):
        return sum([len(element[0]) for element in self.calc_all_moves()])

    #for gui_nerd in office:?
    def all_legal_moves(self):
        return {k: v for v, k in self.calc_all_moves()}

    def legal_moves(self,origin):
        moves = self.all_legal_moves()
        if origin in moves:
            return moves[origin]
        return []

    def origins_with_legal_moves(self):
        return list(self.all_legal_moves().keys())

    def _move_validation(self, unit, dest):
        #check turn, lastmovedcolor and possible move
        if self.get_turn() == unit.player:
            #print(f"Turn {PLAYER_NAME(self.get_turn())}")
            if self.last_moved_color is None or unit.color_index == self.last_moved_color:
                return dest in self.calc_moves(unit.location)[0]
        return False

    def move(self, unit=None, dest=None):

        if self.game_over:
            return False

        #skips turn if unit stuck
        if self.calc_amount_of_moves() == 0:
            unit = [u for u in self.units[self.get_turn()] if u.color_index == self.last_moved_color][0]
            self.last_moved_color = self.board[unit.location].color_index
            self.turn_count += 1

        if self._move_validation(unit, dest):
            self.board[dest].unit = unit
            self.board[unit.location].unit = None
            unit.location = dest
            self.last_moved_color = self.board[dest].color_index

            #print(f"unit location: {dest[0]}")
            #win condition check
            if unit.location[0] == 0 or unit.location[0] == self.board_size[0]-1:

                self.game_over = True
                #print(f"{PLAYER_NAME(self.turn)} WINS!!!")
            if not self.game_over:
                self.turn_count += 1
            return True
        return False

    def move_logic(self, unit=None, dest=None):
        bot_units = self.units[self.get_turn()]
        if self.last_moved_color is None:
            unit_to_move = None
        else:
            unit_to_move = [u for u in bot_units if u.color_index == self.last_moved_color][0]
        if self.game_mode == 1 and not self.player_color == self.get_turn():
            self.bots[0].bot_turn(self.units, unit_to_move, self)
        elif self.game_mode == 2:
            [bot for bot in self.bots if bot.bot_color == self.get_turn()][0].bot_turn(self.units, unit_to_move, self)
            return True
        else:
            return self.move(unit, dest)

    # returns (BlackName, WhiteName)
    def player_names(self):
        players = ["Player", "Player"]
        for bot in self.bots:
            players[int(bot.bot_color)] = type(bot).__name__
        return tuple(players)

    #refactor this function its shit
    def bot_move(self):
        bot_units = self.units[self.get_turn()]
        if self.last_moved_color is None:
            unit_to_move = None
        else:
            unit_to_move = [u for u in bot_units if u.color_index == self.last_moved_color][0]
        if self.game_mode == 1 and not self.player_color == self.get_turn():
            self.bots[0].bot_turn(self.units, unit_to_move, self)
            return True
        elif self.game_mode == 2:
            [bot for bot in self.bots if bot.bot_color == self.get_turn()][0].bot_turn(self.units, unit_to_move, self)
            return True

        return False

    #returns true if passed else false
    def pass_turn(self):
        if self.calc_amount_of_moves() > 0:
            return False
        self.move()
        return True

    #returns isGameOver, who won the game
    def is_game_over(self):
        return self.game_over, self.get_turn() if self.game_over else None


class Cell:
    def __init__(self, color_index, unit=None):
        self.color_index = color_index
        self.unit = unit

    @property
    def hex_color(self):
        return COLORS[self.color_index]

    @property
    def color_name(self):
        return list(COLOR_NAMES.keys())[self.color_index]

    def __repr__(self):
        return f"[Color:{self.color_index},Unit:{self.unit if self.unit is not None else ''}]"


class Unit:
    def __init__(self, player, color_index, location):
        self.player = player
        self.color_index = color_index
        self.location = location

    @property
    def hex_color(self):
        return COLORS[self.color_index]

    @property
    def color_name(self):
        return list(COLOR_NAMES.keys())[self.color_index]

    def __repr__(self):
        return f"[Player:{PLAYER_NAME(self.player)},Color:{self.color_index}]"


if __name__ == "__main__":
    game_board = Board(BOARD_SIZE)
