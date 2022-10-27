from time import time
import networkx as nx
from munkres import Munkres
from network import Network
import json

class Strategy:
    def __init__(self, environment, b_type = "MUNKRES"):
        self.a_type = None
        self.b_type = b_type
        self.team_a = environment.team_a
        self.team_b = environment.team_b
        self.goals = environment.goals
        self.graph = environment.graph
        self.team_a_strategy = {}
        self.team_b_strategy = {}
        self.goals_constraints = {}
        self.team_a_distance_matrix = self.calc_distance_matrix(self.team_a.get_locations_list())
        self.team_b_distance_matrix = self.calc_distance_matrix(self.team_b.get_locations_list())
        self.calc_team_b_strategy() # This must be done first because team A may relay on team B strategy as constraints
        self.calc_goal_constraints()
        
    def calc_goal_constraints(self):
        for item in self.team_b_strategy:
            curr_goal = self.team_b_strategy[item][-1]
            self.goals_constraints[curr_goal] = len(self.team_b_strategy[item]) - 1

    
    def save(self, name):
        with open("results/" + name + ".stg", "w") as savefile:
            matrix_str = ""
            for row in self.team_a_distance_matrix:
                for item in row:
                    matrix_str += str(item) + " "
                matrix_str += "\n"
            savefile.writelines([
                "--------------- A --------------\n\n",
                json.dumps(self.team_a_strategy, indent=4, sort_keys=True),
                "\n\n--------------- B --------------\n\n",
                json.dumps(self.team_b_strategy, indent=4, sort_keys=True),
                "\n\n--------------- goal_constraints --------------\n\n",
                json.dumps(self.goals_constraints, indent=4, sort_keys=True),
                "\n\n--------------- a_matrix --------------\n\n",
                matrix_str,
            ])

    def calc_team_a_strategy(self):
        pass

    def calc_team_b_strategy(self):
        if self.b_type == "MUNKRES":
            before_time = time()
            self.team_b_strategy = self.cost_optimal_strategy(self.team_b, self.team_b_distance_matrix)
            after_time = time()
            self.munkres_b_total_time = after_time - before_time
            return
        elif self.b_type == "NETWORK_MAKESPAN" or self.b_type == "CONSTRAINTS":
            objective = "MAKESPAN"
        elif self.b_type == "NETWORK_TOTAL_DISTANCE":
            objective = "TOTAL_DISTANCE"
        else:
            objective = "MAKESPAN"
            
        self.makespan_network_b = Network(
            graph=self.graph, 
            team=self.team_b,
            goals=self.goals, 
            objective=objective,
        )
        self.team_b_strategy = self.makespan_network_b.strategy
          

    def calc_distance_matrix(self, team_locations):
        goals_locations_list = self.goals.get_locations_list()
        distance_matrix = [[-1 for goal in goals_locations_list] for location in team_locations]
        for i in range(len(team_locations)):
            for j in range(len(goals_locations_list)):
                distance_matrix[i][j] = self.graph.calc_node_distance(team_locations[i], goals_locations_list[j])

        return distance_matrix
    
    def cost_optimal_strategy(self, team, distance_matrix):
        strategy = {}
        m = Munkres()
        assignment = m.compute(distance_matrix)
        team_goals = [(row, self.goals.get_locations_list()[column]) for row, column in assignment]
        for agent_index, goal in team_goals:
            if distance_matrix[agent_index][self.goals.get_locations_list().index(goal)] == self.graph.UNREACHABLE:
                strategy[team.get_agents_list()[agent_index]] = [team.get_locations_list()[agent_index]]
                continue
            strategy[team.get_agents_list()[agent_index]] = nx.shortest_path(self.graph.network, team.get_locations_list()[agent_index], goal)
        return strategy
