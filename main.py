from env_generator import Environment
from game import Game
from strategies import MunkresStrategy, ConstraintsStrategy
from network import Network
from team import Team
from graph import Graph
from utils import *
from animation import Animation
import copy

def main():
    environment = Environment(map_file_name='check.map')
    # environment.grid.visualize()
    print("-------------------------------------------")
    environment.graph.print()
    print("-------------------------------------------")
    environment.team_a.agents = EXAMPLE_TEAM_A
    environment.team_a.print()
    print("-------------------------------------------")
    environment.team_b.agents = EXAMPLE_TEAM_B
    environment.team_b.print()
    print("-------------------------------------------")
    environment.goals.agents = EXAMPLE_GOALS
    environment.goals.print()
    environment.print()
    # environment.visualize()

    # munkres_strategy = MunkresStrategy(environment, b_type="MUNKRES")
    makespan_network_strategy = ConstraintsStrategy(
        environment,
        b_type="MUNKRES", 
        network_mode="hot_swapping-0",
        constraints={
            '9': 3,
            '35': 2,
            '43': 1,
            '16': 6,
        },
    )
    # makespan_network_strategy.makespan_network_a.visualize_flow()
    # makespan_network_strategy.makespan_network_b.visualize_flow()
    print("A Straregy: ")
    print(makespan_network_strategy.team_a_strategy)
    print("B Straregy: ")
    print(makespan_network_strategy.team_b_strategy)
    

    tmp_env = copy.deepcopy(environment)
    tmp_strategy = copy.deepcopy(makespan_network_strategy)
    game = Game(tmp_env, tmp_strategy.team_a_strategy, tmp_strategy.team_b_strategy)
    game.run()

    # anim = Animation(environment, makespan_network_strategy.team_a_strategy, makespan_network_strategy.team_b_strategy, game.lost_goals)
    # anim.plot()

if __name__ == "__main__":
    main()