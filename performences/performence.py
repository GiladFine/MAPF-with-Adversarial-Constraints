import sys
from random import randint, uniform
from munkres import Munkres
from env_generator import Environment
from strategies import ConstraintsStrategy
from time import time
from pydantic import BaseModel
from typing import Any, List, Union, Dict, Tuple

import json

from strategies.munkres_strategy import MunkresStrategy
from performences.config import get_config, ConfigType


class Config(BaseModel):
    grid_sizes_index: int
    team_sizes_index: int
    obstacle_frequencies_index: int


class DataRecord(BaseModel):
    map_name: str
    network_mode: str
    grid_size: int
    obstacle_frequency: float
    teams_size: int
    number_of_sat_solutions: int
    overall_sat_time: float
    overall_sat_time_solver: float
    overall_non_sat_time: float
    overall_non_sat_time_solver: float
    overall_paths_sizes_generally_sat: int
    overall_flow_values: int
    number_of_runs: int    


# CONFIGS

CONFIG_TYPE = ConfigType(sys.argv[1])
CONFIG = get_config(
    config_type=CONFIG_TYPE,
    number_of_runs=int(sys.argv[2]),
    index=int(sys.argv[3]),
)
MAP_NAME = CONFIG.MAP_NAME
NUM_OF_RUNS = CONFIG.number_of_runs
NETWORK_MODES = CONFIG.NETWORK_MODES
GOAL_LOCATIONS = CONFIG.GOAL_LOCATIONS
NUMBER_OF_GOALS_LIST = CONFIG.NUMBER_OF_GOALS_LIST

def goal_locations(num_of_goals: int) -> List[str]:
    return GOAL_LOCATIONS[:num_of_goals]

def log_data_record(
    results: Dict[str, Any],
    env: Environment,
) -> None:
    file_name = f"performences/results/{CONFIG_TYPE.value}/{CONFIG.index}_performence_results.json"
    with open(file_name, 'r') as results_file:
        results_dict = json.load(results_file)

    for network_mode, info in results.items():
        results_dict[MAP_NAME][network_mode].update(
            {
                str(env.teams_size): {
                    "number_of_sat_solutions": info["number_of_valid_solutions"],
                    "overall_sat_time": info["overall_sat_time"],
                    "overall_sat_time_solver": info["overall_sat_time_solver"],
                    "overall_non_sat_time": info["overall_non_sat_time"],
                    "overall_non_sat_time_solver": info["overall_non_sat_time_solver"],
                    "overall_paths_sizes_generally_sat": info["overall_paths_sizes_generally_sat"],
                    "overall_flow_values": info["overall_flow_values"]
                }
            }
        )
        print(results_dict[MAP_NAME][network_mode])
        with open(file_name, 'w') as results_file:
            results_file.write(json.dumps(results_dict, indent=4))

def generate_constraints(env: Environment, num_of_goals: int, ext_factor: int = 0) -> Dict[str, int]:
    constraints = {}
    for goal_location in goal_locations(num_of_goals=num_of_goals):
        distances = [
            env.graph.calc_node_distance(agent_location, goal_location)
            for agent_location in env.team_a.get_locations_list()
        ]
        max_d = max(distances)
        min_d = min(distances)
        factor = (240 - num_of_goals) / 240
        constraints[goal_location] = max(
            int(randint(min(min_d + ext_factor, max_d), max_d) * min(uniform(factor, factor + 0.1), 1)),
            min_d
        )
        
    return constraints
        

def calc_strategy(environment: Environment, network_mode: str, constraints: Dict[str, int]) -> Union[ConstraintsStrategy, Tuple[int, float]]:
    try:
        return ConstraintsStrategy(
            environment,
            b_type="MUNKRES",
            network_mode=network_mode,
            constraints=constraints,
        )
    except ValueError as err:
        return int(err.args[1]), float(err.args[2])

def generate_team_a(env: Environment, num_of_goals: int) -> Dict[str, str]:
    generated_locations = env.grid.random_free_locations(num_of_locations=num_of_goals)
    return {
        f"a{i}": loc
        for i, loc in enumerate(generated_locations)
    }

def check_munkres(env: Environment, constraints: Dict[str, int], num_of_goals: int) -> bool:
    munkres_strategy = MunkresStrategy(env, b_type="MUNKRES")
    constraints_list = [
        constraints[goal_location]
        for goal_location in env.goals.get_locations_list()
    ]
    reachability_matrix = []
    for row in munkres_strategy.team_a_distance_matrix:
        new_row = []
        for j, distance in enumerate(row):
            new_row.append(
                0
                if distance <= constraints_list[j] + randint(0, 1)
                else 1
            )
        reachability_matrix.append(new_row)

    m = Munkres()
    assignment = m.compute(reachability_matrix)
    reachability_list = [
        reachability_matrix[i][j]
        for i, j in assignment
    ]
    if sum(reachability_list) == 0:
        return True
    return False
  
def create_env_and_constraints(num_of_goals: int) -> Environment:
    environment = Environment(
        map_file_name=MAP_NAME,
        teams_size=num_of_goals,
    )
    environment.goals.agents = {
        f"g{i}": loc
        for i, loc in enumerate(goal_locations(num_of_goals=num_of_goals))
    }

    environment.team_a.agents = generate_team_a(env=environment, num_of_goals=num_of_goals)

    constraints = generate_constraints(env=environment, num_of_goals=num_of_goals)

    if num_of_goals >= 30:
        return cenvironment, constraintsons

    for i in range(3):
        if check_munkres(env=environment, constraints=constraints, num_of_goals=num_of_goals):
            break
        constraints = generate_constraints(env=environment, num_of_goals=num_of_goals, ext_factor=i)

    return environment, constraints

def calc_strategy_paths_size(strategy: ConstraintsStrategy) -> Dict[str, int]:
    path_sums = {}
    for agent, path in strategy.team_a_strategy.items():
        path_sum = 0
        prev_loc = "NONE"
        for loc in path:
           if loc != prev_loc:
               prev_loc = loc
               path_sum += 1  
        path_sums[agent] = path_sum - 1 # First loc does not require a move
    return path_sums


# MAIN
        
for num_of_goals in NUMBER_OF_GOALS_LIST:
    results = {
        network_mode: {
            'overall_sat_time': 0.0,
            'overall_sat_time_solver': 0.0,
            'overall_non_sat_time': 0.0,
            'overall_non_sat_time_solver': 0.0,
            'number_of_valid_solutions': 0,
            'overall_paths_sizes_generally_sat': 0,
            'overall_flow_values': 0,
        }
        for network_mode in NETWORK_MODES
    }
    for i in range(NUM_OF_RUNS):
        print(i + 1)
        environment, constraints = create_env_and_constraints(num_of_goals=num_of_goals)
        all_solutions_found = True
        for network_mode in NETWORK_MODES:
            before_time = time()
            constraiant_strategy = calc_strategy(
                environment=environment,
                network_mode=network_mode,
                constraints=constraints,
            )
            after_time = time()
            overall_time = after_time - before_time

            solution_found = (
                True
                if isinstance(constraiant_strategy, ConstraintsStrategy)
                else False
            )
            solver_time = (
                constraiant_strategy.constrains_network_a.solver_time
                if solution_found
                else constraiant_strategy[1]
            )
            flow_value = (
                constraiant_strategy.constrains_network_a.flow_value
                if solution_found
                else constraiant_strategy[0]
            )
            results[network_mode]['overall_flow_values'] += flow_value
                
            path_sizes_dict = {}
            if solution_found:
                results[network_mode]['number_of_valid_solutions'] += 1
                results[network_mode]['overall_sat_time'] += overall_time
                results[network_mode]['overall_sat_time_solver'] += solver_time
                path_sizes_dict = calc_strategy_paths_size(strategy=constraiant_strategy)
                overall_fuel = sum(path_sizes_dict.values())
                if all_solutions_found:
                    results[network_mode]['overall_paths_sizes_generally_sat'] += overall_fuel
            else:
                overall_fuel = 0
                all_solutions_found = False
                results[network_mode]['overall_non_sat_time'] += overall_time
                results[network_mode]['overall_non_sat_time_solver'] += solver_time

            log_str = f"{MAP_NAME}, {network_mode}, {num_of_goals}, {i + 1}, {solution_found}, {solver_time}, {overall_time}, {path_sizes_dict}, {overall_fuel}, {flow_value}"
            print(log_str)

            with open(f"performences/results/{CONFIG_TYPE.value}/{CONFIG.index}_log.txt", 'a') as log_file:
                log_file.write(log_str + "\n")
            
        print(f"\nResults for {num_of_goals} agents - \n{json.dumps(results, indent=4)}\n")        
    
    log_data_record(
        results=results,
        env=environment,
    )
