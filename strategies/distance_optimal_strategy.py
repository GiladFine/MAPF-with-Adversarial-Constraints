from network import Network
from strategies import Strategy


class DistanceOptimalStrategy(Strategy):
    def __init__(self, environment, b_type = "MUNKRES"):
        self.a_type = "TOTAL_DISTANCE"
        super().__init__(environment=environment, b_type=b_type)
        self.calc_team_a_strategy()

    def calc_team_a_strategy(self):
        self.distance_network_a = Network(
            graph=self.graph,
            team=self.team_a,
            goals=self.goals,
            objective="TOTAL_DISTANCE",
        )
        self.team_a_strategy = self.distance_network_a.strategy

