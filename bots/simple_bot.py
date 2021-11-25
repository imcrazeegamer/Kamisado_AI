from logic import base_bot


class Simplebot(base_bot.Basebot):

    def __init__(self, bot_color, depth=4):
        super().__init__(bot_color)
        self.last_moved_color = None
        self.depth = depth

    # called every time its the bots turn to move
    def bot_turn(self, units, unit_to_move, board):
        print(f'MinMax Turn: {self.bot_color}')
        score, move = self.minimax(board, self.depth, float('-inf'), float('inf'), maximizingPlayer=self.bot_color)
        #score, move = self.minimax(board, self.depth, float('-inf'), float('inf'), maximizingPlayer=True)
        print(f"MiniMax = {score,move}")
        if move is None:
            board.move()
            return
        board.move(board.board[move[0]].unit, move[1])
        return

    # returns score,next_move
    def minimax(self, board, depth, alpha, beta, maximizingPlayer=True):
        if board.game_over:
            print(f"Gameover in {self.depth - depth} turns, bot: {'White' if self.bot_color else 'Black'},Score {1 if not maximizingPlayer else -1}{'max' if self.bot_color else 'min'}")
            return 1 if not maximizingPlayer else -1, None
        if depth == 0:
            return 0, None

        if maximizingPlayer:
            maxEval = float('-inf')
            best_move = None
            #for each possible move
            for unit_options in self.get_all_legal_moves(board):
                for move in unit_options[0]:
                    new_board = self.simulate_move(unit_options[1], move, board)
                    eeval, _ = self.minimax(new_board, depth-1, alpha, beta, False)
                    maxEval = max(maxEval, eeval)
                    if eeval == maxEval:
                        best_move = (unit_options[1], move)
                    alpha = max(alpha, eeval)
                    if maxEval >= beta:
                        return maxEval, best_move
            return maxEval, best_move

        else:
            minEval = float('inf')
            worst_move = None
            # for each possible move
            for unit_options in self.get_all_legal_moves(board):
                for move in unit_options[0]:
                    new_board = self.simulate_move(unit_options[1], move, board)
                    eeval, _ = self.minimax(new_board, depth - 1, alpha, beta, True)
                    minEval = min(minEval, eeval)
                    if minEval == eeval:
                        worst_move = (unit_options[1], move)
                    beta = min(beta, eeval)
                    if minEval <= alpha:
                        return minEval, worst_move
            return minEval, worst_move
