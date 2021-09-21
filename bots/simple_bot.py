from logic import base_bot


class Simplebot(base_bot.Basebot):

    def __init__(self, bot_color, depth=3):
        super().__init__(bot_color)
        self.last_moved_color = None
        self.depth = depth

    # called every time its the bots turn to move
    def bot_turn(self, units, unit_to_move, board):
        score, move = self.minimax(board, self.depth, float('-inf'), float('inf'), maximizingPlayer=self.bot_color)
        print(f"MiniMax = {score,move}")
        if move is None:
            board.move(None, None)
            return
        board.move(board.board[move[0]].unit, move[1])
        return

    # returns score,next_move
    def minimax(self, board, depth, alpha, beta, maximizingPlayer=True, game_over=False):
        if game_over:
            print(f"Gameover at depth: {depth}, player: {maximizingPlayer} won")
            return 1 if not maximizingPlayer else -1, None
        elif depth == 0:
            return 0, None

        if maximizingPlayer:
            maxEval = float('-inf')
            best_move = None
            #for each possible move
            for unit_options in self.get_all_legal_moves(board):
                for move in unit_options[0]:
                    new_board = self.simulate_move(unit_options[1], move, board)
                    game_over = new_board.game_over
                    eeval, n_move = self.minimax(new_board, depth-1, alpha, beta, False, game_over)
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
                    #print(f"move! {move}")
                    new_board = self.simulate_move(unit_options[1], move, board)
                    game_over = new_board.game_over
                    eeval, n_move = self.minimax(new_board, depth - 1, alpha, beta, True, game_over)
                    minEval = min(minEval, eeval)
                    if minEval == eeval:
                        worst_move = (unit_options[1], move)
                    beta = min(beta, eeval)
                    if minEval <= alpha:
                        return minEval, worst_move
            return minEval, worst_move

    def board_to_miniboard(self, board):
        miniboard = {}
        for pos, cell in board.items():
            if cell.unit:
                val = 'W' if cell.unit.player else 'B'
                val += cell.unit.color_index
            else:
                val = "XX"

            miniboard[pos] = (val, cell.color_index)
        return miniboard

    def move_miniboard(self, origin, dest, board):
        nb = board.copy()
        val = nb[origin]
        nb[dest] = (val, nb[dest][1])
        nb[origin] = ("XX", nb[origin][1])
        return nb
