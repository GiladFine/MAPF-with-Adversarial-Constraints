from network import Network
from strategies import Strategy


class ExperimentStrategy(Strategy):
    def __init__(self, environment, b_type = "MUNKRES"):
        self.a_type = "EXPERIMENT"
        super().__init__(environment=environment, b_type=b_type)
        self.disturbances = {}
        self.calc_disturbances()
        self.calc_team_a_strategy()
        
    def calc_disturbances(self):
        pass

    def calc_team_a_strategy(self):
        self.team_a_distance_matrix