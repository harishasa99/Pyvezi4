import random
from game.models.state import State

class Agent:
    ident = 0

    def __init__(self):
        self.id = Agent.ident
        Agent.ident += 1

    def get_chosen_column(self, state, max_depth):
        pass

    @staticmethod
    def easy_heuristic(state):
        """
        Simple heuristic: Counts potential wins for the current player.
        """
        current_player = state.get_next_on_move()
        opponent = State.YEL if current_player == State.RED else State.RED
        player_potential = sum(1 for mask in state.win_masks if (mask & state.get_checkers(opponent)) == 0)
        return player_potential

    @staticmethod
    def medium_heuristic(state):
        """
        Medium heuristic: Considers both players' potential wins.
        """
        current_player = state.get_next_on_move()
        opponent = State.YEL if current_player == State.RED else State.RED
        player_potential = sum(1 for mask in state.win_masks if (mask & state.get_checkers(opponent)) == 0)
        opponent_potential = sum(1 for mask in state.win_masks if (mask & state.get_checkers(current_player)) == 0)
        return player_potential - 2 * opponent_potential

    @staticmethod
    def hard_heuristic(state):
        """
        Advanced heuristic: Weighs potential wins and penalizes critical positions.
        """
        current_player = state.get_next_on_move()
        opponent = State.YEL if current_player == State.RED else State.RED
        player_score = 0
        opponent_score = 0

        for mask in state.win_masks:
            player_match = state.get_checkers(current_player) & mask
            opponent_match = state.get_checkers(opponent) & mask

            if player_match == 0:
                player_score += 5 - bin(mask).count("1")  # Less tokens = higher score
            if opponent_match == 0:
                opponent_score += 5 - bin(mask).count("1")

        return player_score - opponent_score

class MinimaxABAgent(Agent):
    """
    Minimax agent with Alpha-Beta pruning.
    """

    def get_chosen_column(self, state, max_depth):
        _, column = self.minimax(state, max_depth, True, float('-inf'), float('inf'))
        return column

    def minimax(self, state, depth, maximizing_player, alpha, beta):
        if depth == 0 or state.get_state_status() is not None:
            return self.evaluate(state), None

        if maximizing_player:
            max_eval = float('-inf')
            best_column = None
            for column in self.sorted_columns(state):
                new_state = state.generate_successor_state(column)
                eval, _ = self.minimax(new_state, depth - 1, False, alpha, beta)
                if eval > max_eval:
                    max_eval = eval
                    best_column = column
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_column
        else:
            min_eval = float('inf')
            best_column = None
            for column in self.sorted_columns(state):
                new_state = state.generate_successor_state(column)
                eval, _ = self.minimax(new_state, depth - 1, True, alpha, beta)
                if eval < min_eval:
                    min_eval = eval
                    best_column = column
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_column

    def evaluate(self, state):
        if state.get_state_status() == State.RED:
            return 1000  # Red wins
        if state.get_state_status() == State.YEL:
            return -1000  # Yellow wins

        # Choose heuristic based on difficulty level
        if self.id == 0:  # Example: EASY
            return self.easy_heuristic(state)
        elif self.id == 1:  # Example: MEDIUM
            return self.medium_heuristic(state)
        else:  # HARD
            return self.hard_heuristic(state)

    def sorted_columns(self, state):
        columns = state.get_possible_columns()
        center_order = [3, 2, 4, 1, 5, 0, 6]
        return sorted(columns, key=lambda col: center_order.index(col))

class NegascoutAgent(Agent):
    """
    Negascout algorithm agent.
    """

    def get_chosen_column(self, state, max_depth):
        _, column = self.negascout(state, max_depth, True, float('-inf'), float('inf'))
        return column

    def negascout(self, state, depth, maximizing_player, alpha, beta):
        if depth == 0 or state.get_state_status() is not None:
            return self.evaluate(state), None

        best_value = float('-inf')
        best_column = None
        b = beta

        for i, column in enumerate(self.sorted_columns(state)):
            new_state = state.generate_successor_state(column)
            value, _ = self.negascout(new_state, depth - 1, not maximizing_player, -b, -alpha)
            value = -value

            if value > best_value:
                best_value = value
                best_column = column

            if value > alpha:
                alpha = value

            if alpha >= beta:
                break

            if i > 0:
                b = alpha + 1

        return best_value, best_column

    def evaluate(self, state):
        if state.get_state_status() == State.RED:
            return 1000  
        if state.get_state_status() == State.YEL:
            return -1000  

        
        if self.id == 0:  
            return self.easy_heuristic(state)
        elif self.id == 1:  
            return self.medium_heuristic(state)
        else:  
            return self.hard_heuristic(state)

    def sorted_columns(self, state):
        columns = state.get_possible_columns()
        center_order = [3, 2, 4, 1, 5, 0, 6]
        return sorted(columns, key=lambda col: center_order.index(col))

class CompetitiveAgent(Agent):
    """
    Competitive agent for advanced strategies.
    """

    def __init__(self):
        self.minimax_agent = MinimaxABAgent()
        self.negascout_agent = NegascoutAgent()

    def get_chosen_column(self, state, max_depth):
        if max_depth % 2 == 0:
            return self.negascout_agent.get_chosen_column(state, max_depth)
        else:
            return self.minimax_agent.get_chosen_column(state, max_depth)

    def evaluate(self, state):
        return self.negascout_agent.evaluate(state)
