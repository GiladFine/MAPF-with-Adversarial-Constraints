from copy import deepcopy
from network import Network
from strategies import Strategy


class ConstraintsStrategy(Strategy):
    def __init__(self, environment, b_type = "MUNKRES", constraints = None, network_mode = "disappearing"):
        self.a_type = "CONSTRAINTS"
        self.network_mode = network_mode
        super().__init__(environment=environment, b_type=b_type)
        if constraints:
            self.goals_constraints = constraints
        self.calc_team_a_strategy()

    def calc_team_a_strategy(self):
        # Calculate team A constraints based on team B's strategy
        team_a, goals = deepcopy(self.team_a), deepcopy(self.goals)
        # print("Network")
        self.constrains_network_a = Network(
            graph=self.graph,
            team=team_a,
            goals=goals,
            reach_constraints=self.goals_constraints,
            objective="CONSTRAINTS",
            network_mode=self.network_mode,
        )        
        self.team_a_strategy = self.constrains_network_a.strategy
