from env_generator import Environment
from game import Game
from strategy import Strategy
from network import Network
from team import Team
from graph import Graph
from utils import *
from animation import Animation
import copy

def main():
    for i in range(100):
        environment = Environment()
        environment.print()
        print("-------------------------------------------")
        environment.team_a.print()
        print("-------------------------------------------")
        environment.team_b.print()
        print("-------------------------------------------")
        environment.goals.print()

        munkres_strategy = Strategy(environment, "MUNKRES")
        print("A Straregy: ")
        print(munkres_strategy.team_a_strategy)
        print("B Straregy: ")
        print(munkres_strategy.team_b_strategy)

        tmp_env = copy.deepcopy(environment)
        tmp_strategy = copy.deepcopy(munkres_strategy)
        game = Game(tmp_env, tmp_strategy.team_a_strategy, tmp_strategy.team_b_strategy)
        game.run()
        if game.coverage_percentage == 100:
            print("WIN")
        print("-------------------------------------------")


    
    return
    


if __name__ == "__main__":
    main()