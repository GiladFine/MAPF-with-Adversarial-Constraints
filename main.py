from env_generator import Environment
from game import Game
from strategy import Strategy
from network import Network
from team import Team
from graph import Graph
from utils import *

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
    environment.graph.visualize()

    strategy = Strategy(environment)

    game = Game(environment, strategy.team_a_strategy, strategy.team_b_strategy)
    game.run()

    my_network = Network(environment.graph, environment.team_a, environment.goals)


if __name__ == "__main__":
    main()