from env_generator import Environment
from game import Game
from strategy import Strategy
from network import Network
from team import Team
from graph import Graph
from utils import *
import copy

def main():
    environment = Environment()
    environment.grid.print()
    print("-------------------------------------------")
    environment.graph.print()
    print("-------------------------------------------")
    environment.team_a.print()
    print("-------------------------------------------")
    environment.team_b.print()
    print("-------------------------------------------")
    environment.goals.print()
    #environment.graph.visualize()

    strategy = Strategy(environment)

    tmp_env = copy.deepcopy(environment)
    tmp_strategy = copy.deepcopy(strategy)
    game = Game(tmp_env, tmp_strategy.team_a_strategy, tmp_strategy.team_b_strategy)
    game.run()

    my_network = Network(environment.graph, environment.team_a, environment.goals)
    # my_network = Network(Graph(NETWORK_TEST_GRAPH), Team(NETWORK_TEST_TEAM), Team(NETWORK_TEST_GOALS))
    return
    


if __name__ == "__main__":
    main()