from env_generator import Environment
from game import Game
from strategy import Strategy
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

    # environment.team_a, environment.team_b = EXAMPLE_TEAM_A, EXAMPLE_TEAM_B
    # environment.graph, environment.goals = EXAMPLE_GRAPH, EXAMPLE_GOALS
    game = Game(environment, strategy.team_a_strategy, strategy.team_b_strategy)
    game.run()

    

if __name__ == "__main__":
    main()