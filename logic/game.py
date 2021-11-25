from logic import board
from logic import base_bot
from bots import simple_bot
import random


class Game:
    Known_bots = {
        "simple_bot": simple_bot.Simplebot,
        #"base_bot": base_bot.Basebot
                  }

    @staticmethod
    def _gen_board(bots=(), random_bot_count=0):

        for i in range(random_bot_count):
            if len(bots) == 0:
                player_color = random.choice((True, False))
            else:
                player_color = not bots[0][0]
            bots.append((player_color, random.choice(list(Game.Known_bots.values())), None))

        new_board = board.Board(board.BOARD_SIZE, bots=bots)

        return new_board

    @staticmethod
    def new_board(black_bot_name=None, black_bot_args=(), white_bot_name=None, white_bot_args=(), random_bots=0):
        bots = []
        if black_bot_name and black_bot_name != "Player":
            bots.append((False, Game.Known_bots[black_bot_name], black_bot_args))
        if white_bot_name and white_bot_name != "Player":
            bots.append((True, Game.Known_bots[white_bot_name], white_bot_args))
        return Game._gen_board(bots, random_bot_count=random_bots)

    @staticmethod
    def gen_PvP_board():
        return Game._gen_board()

    @staticmethod
    def gen_PvE_board():
        return Game._gen_board(random_bot_count=1)

    @staticmethod
    def gen_EvE_board():
        return Game._gen_board(random_bot_count=2)

    @staticmethod
    def all_bot_names():
        return list(Game.Known_bots.keys())





