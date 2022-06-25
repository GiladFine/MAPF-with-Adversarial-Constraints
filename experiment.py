from env_generator import Environment
from game import Game
from strategies import MunkresStrategy, ConstraintsStrategy
from network import Network
from team import Team
from graph import Graph
from utils import *
from animation import Animation
import copy

def save_info(environment, munkres_strategy, constraints_strategy):
    envs_number_file = open("results/next_index.txt", 'r')
    num_of_envs = int(envs_number_file.readline())
    
    env_name, munkres_name, constraints_name = f"env_{num_of_envs}", f"munkres_{num_of_envs}", f"constraints_{num_of_envs}"
    environment.save(env_name=env_name)
    munkres_strategy.save(name=munkres_name)
    constraints_strategy.save(name=constraints_name)
    
    envs_number_file = open("results/next_index.txt", 'w')
    envs_number_file.write(str(num_of_envs + 1))
    
    
def run_strategy(environment, strategy):
    tmp_env = copy.deepcopy(environment)
    tmp_strategy = copy.deepcopy(strategy)
    game = Game(tmp_env, tmp_strategy.team_a_strategy, tmp_strategy.team_b_strategy)
    game.run()
    return game.coverage_percentage



def main():
    for i in range(100000):
        environment = Environment()
        environment.print()
        print("-------------------------------------------")
        environment.team_a.print()
        print("-------------------------------------------")
        environment.team_b.print()
        print("-------------------------------------------")
        environment.goals.print()

        munkres_strategy = MunkresStrategy(environment, b_type="MUNKRES")
        print("A Straregy: ")
        print(munkres_strategy.team_a_strategy)
        print("B Straregy: ")
        print(munkres_strategy.team_b_strategy)

        munkres_result = run_strategy(environment, munkres_strategy)
        if munkres_result == 100:
            constraints_strategy = ConstraintsStrategy(environment, b_type="MUNKRES")
            constraints_result = run_strategy(environment, constraints_strategy)
            if constraints_result < 100:
                save_info(environment, munkres_strategy, constraints_strategy)

        print("-------------------------------------------")
    
    


if __name__ == "__main__":
    main()