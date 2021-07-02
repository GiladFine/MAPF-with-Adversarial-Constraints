import networkx as nx
from munkres import Munkres, DISALLOWED
from math import inf
from collections import Counter
from network import Network

# TODO this class needs a refactor
class Strategy:
    def __init__(self, environment, strategy_type = "MUNKRES"):
        self.type = strategy_type
        self.team_a = environment.team_a
        self.team_b = environment.team_b
        self.goals = environment.goals
        self.graph = environment.graph
        self.team_a_strategy = {}
        self.team_b_strategy = {}
        self.team_a_distance_matrix = self.calc_distance_matrix(self.team_a.get_locations_list())
        self.team_b_distance_matrix = self.calc_distance_matrix(self.team_b.get_locations_list())
        self.calc_team_b_strategy()
        self.calc_team_a_strategy()
        

    
    def calc_team_a_strategy(self):
        if self.type == "MUNKRES":
            self.team_a_strategy = self.cost_optimal_strategy(self.team_a, self.team_a_distance_matrix)
        elif self.type == "NETWORK_MAKESPAN":
            self.makespan_network_a = Network(self.graph, self.team_a, self.goals, objective="MAKESPAN")
            self.team_a_strategy = self.makespan_network_a.strategy
        elif self.type == "NETWORK_TOTAL_DISTANCE":
            self.distance_network_a = Network(self.graph, self.team_a, self.goals, objective="TOTAL_DISTANCE")
            self.team_a_strategy = self.distance_network_a.strategy
        elif self.type == "CONSTRAINTS":
            a_constraints = {}
            for item in self.team_b_strategy:
                curr_goal = self.team_b_strategy[item][-1]
                a_constraints[curr_goal] = len(self.team_b_strategy[item]) - 1

            self.constrains_network_a = Network(self.graph, self.team_a, self.goals, a_constraints, objective="CONSTRAINTS")
            self.team_a_strategy = self.constrains_network_a.strategy
    

    def calc_team_b_strategy(self):
        if self.type == "MUNKRES":
            self.team_b_strategy = self.cost_optimal_strategy(self.team_b, self.team_b_distance_matrix)
        elif self.type == "NETWORK_MAKESPAN" or self.type == "CONSTRAINTS":
            self.makespan_network_b = Network(self.graph, self.team_b, self.goals, objective="MAKESPAN")
            self.team_b_strategy = self.makespan_network_b.strategy
        elif self.type == "NETWORK_TOTAL_DISTANCE":
            self.distance_network_b = Network(self.graph, self.team_b, self.goals, objective="TOTAL_DISTANCE")
            self.team_b_strategy = self.distance_network_b.strategy


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
            



