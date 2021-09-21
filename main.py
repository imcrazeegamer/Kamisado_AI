from gui.app import App
from logic import board
from logic import base_bot
from bots import simple_bot

#new_board = board.Board(board.BOARD_SIZE, [base_bot.Basebot(True), base_bot.Basebot(False)])
new_board = board.Board(board.BOARD_SIZE, [simple_bot.Simplebot(True,depth=2), simple_bot.Simplebot(False,depth=2)])
App(new_board).run()