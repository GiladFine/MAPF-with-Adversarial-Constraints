from random import randint
from munkres import Munkres
from env_generator import Environment
from strategies import ConstraintsStrategy
from statistics import median
from time import time
from pydantic import BaseModel
from typing import Any, List, Optional, Dict

import json

from strategies.munkres_strategy import MunkresStrategy


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
    overall_non_sat_time: float
    overall_paths_sizes_generally_sat: int
    number_of_runs: int    
    

MAP_NAME = "room-32.map"
NUM_OF_RUNS = 100
NETWORK_MODES = ["stays", "disappearing", "demands"]
GOALS_LOCATIONS_ROOM = [
    "325",
    "323",
    "289",
    "263",
    "390",
    "394",
    "365",
    "271",
    "305",
    "275",
    "403",
]
GOALS_LOCATIONS_MAZE = [
    "416",
    "351",
    "510",
    "573",
    "637",
    "664",
    "727",
    "789",
    "725",
    "783",
    "750",
]
GOAL_LOCATIONS = GOALS_LOCATIONS_ROOM

def goal_locations(num_of_goals: int) -> List[str]:
    return GOAL_LOCATIONS[:num_of_goals]

def log_data_record(
    results: Dict[str, Any],
    env: Environment,
) -> None:
    for network_mode, info in results.items():
        data_record = DataRecord(
            map_name=MAP_NAME,
            network_mode=network_mode,
            grid_size=env.grid_size,
            teams_size=env.teams_size,
            obstacle_frequency=env.obstacle_frequency,
            number_of_runs=NUM_OF_RUNS,
            number_of_sat_solutions=info["number_of_valid_solutions"],
            overall_sat_time=info["overall_sat_time"],
            overall_non_sat_time=info["overall_non_sat_time"],
            overall_paths_sizes_generally_sat=info["overall_paths_sizes_generally_sat"],
        )
        print(data_record.dict())
        with open("performences/performence_results.txt", 'a') as results_file:
            results_file.write(json.dumps(data_record.dict(), indent=4))
            results_file.write("\n------------------------\n")

def generate_constraints(env: Environment, factor: int, num_of_goals: int) -> Dict[str, int]:
    constraints = {}
    for goal_location in goal_locations(num_of_goals=num_of_goals):
        distances = [
            env.graph.calc_node_distance(agent_location, goal_location)
            for agent_location in env.team_a.get_locations_list()
        ]
        max_d = max(distances)
        min_d = min(distances)
        constraints[goal_location] = randint(
            min(min_d + factor, max_d),
            max_d,
        )
    
    return constraints
        

def calc_strategy(environment: Environment, network_mode: str, constraints: Dict[str, int]) -> Optional[ConstraintsStrategy]:
    try:
        return ConstraintsStrategy(
            environment,
            b_type="MUNKRES",
            network_mode=network_mode,
            constraints=constraints,
        )
    except:
        return None

def generate_team_a(env: Environment, num_of_goals: int) -> Dict[str, str]:
    generated_locations = env.grid.random_free_locations(num_of_locations=num_of_goals)
    return {
        f"a{i}": loc
        for i, loc in enumerate(generated_locations)
    }

def check_munkres(env: Environment, constraints: Dict[str, int]) -> bool:
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
                if distance <= constraints_list[j]
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

    factor = 0
    constraints = generate_constraints(env=environment, factor=factor, num_of_goals=num_of_goals)
    while not check_munkres(env=environment, constraints=constraints):
        # factor += 1
        constraints = generate_constraints(env=environment, factor=factor, num_of_goals=num_of_goals)

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
        path_sums[agent] = path_sum           
    return path_sums  
        
def main():
    for num_of_goals in [5, 7, 9, 11]:
        results = {
            network_mode: {
                'overall_sat_time': 0.0,
                'overall_non_sat_time': 0.0,
                'number_of_valid_solutions': 0,
                'overall_paths_sizes_generally_sat': 0,
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
                    False
                    if constraiant_strategy is None
                    else True
                )
                path_sizes_dict = {}
                if solution_found:
                    results[network_mode]['number_of_valid_solutions'] += 1
                    results[network_mode]['overall_sat_time'] += overall_time
                    path_sizes_dict = calc_strategy_paths_size(strategy=constraiant_strategy)
                    if all_solutions_found:
                        results[network_mode]['overall_paths_sizes_generally_sat'] += sum(path_sizes_dict.values())
                else:
                    all_solutions_found = False
                    results[network_mode]['overall_non_sat_time'] += overall_time

                log_str = f"{MAP_NAME}, {network_mode}, {num_of_goals}, {i + 1}, {solution_found}, {overall_time}, {path_sizes_dict}"
                print(log_str)

                with open("performences/log.txt", 'a') as log_file:
                    log_file.write(log_str + "\n")
                
            print(f"\nResults for {num_of_goals} agents - \n{json.dumps(results, indent=4)}\n")        
        
        log_data_record(
            results=results,
            env=environment,
        )


if __name__ == "__main__":
    main()