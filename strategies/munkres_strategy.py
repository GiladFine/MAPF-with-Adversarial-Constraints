from strategies import Strategy


class MunkresStrategy(Strategy):
    def __init__(self, environment, b_type = "MUNKRES"):
        self.a_type = "MUNKRES"
        super().__init__(environment=environment, b_type=b_type)
        self.calc_team_a_strategy()

    def calc_team_a_strategy(self):
        self.team_a_strategy = self.cost_optimal_strategy(self.team_a, self.team_a_distance_matrix)
