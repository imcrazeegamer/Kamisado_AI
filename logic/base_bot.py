import random
import copy

class Basebot:

    def __init__(self, bot_color):
        self.bot_color = bot_color

    #called every time its the bots turn to move
    def bot_turn(self, units, unit_to_move, board):
        my_units = units[self.bot_color]
        my_unit = unit_to_move
        # if unit_to_move is None: then you can move any unit else only that unit
        #print(board.calc_all_moves())
        all_moves = board.calc_all_moves()
        if all_moves:
            dests, origin = random.choice(all_moves)
        else:
            board.move(None, None)
            return
        if len(dests) == 0:
            board.move(my_unit, (0, 0))
        #print(dests, origin)
        dest = random.choice(dests)
        unit = board.board[origin].unit
        board.move(unit, dest)
        return

    #returns copy of board class after moved
    def simulate_move(self,origin,destination,board):
        new_board = copy.deepcopy(board)
        new_board.move(new_board.board[origin].unit, destination)
        return new_board

    # returns [[dest_list,origin],...]
    def get_all_legal_moves(self, board):
        return board.calc_all_moves()

    # check move win condition
    def check_move_win(self, dest, board_size=8):
        return dest[0] == 0 or dest[0] == board_size-1