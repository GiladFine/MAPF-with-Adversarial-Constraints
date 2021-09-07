import networkx as nx
from munkres import Munkres, DISALLOWED
from math import inf
from copy import deepcopy
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
        self.calc_team_b_strategy() # This must be done first because team A may relay on team B strategy as constraints
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

            # Calculate team A constraints based on team B's strategy
            a_constraints = {}
            for item in self.team_b_strategy:
                curr_goal = self.team_b_strategy[item][-1]
                a_constraints[curr_goal] = len(self.team_b_strategy[item]) - 1

            # The main idea here is to calculate a Network-Flow based solution, them 'delete' the found goals
            # and re-calculate for the unachieved goals until convergence. This helps us calculate the final paths
            # for the entire problem in the final step, while addressing the 'hot-swapping' problem.
            is_improving = True
            team_a, goals = deepcopy(self.team_a), deepcopy(self.goals)
            hot_swaps_locations = []
            while is_improving and team_a.agents != {} and goals.agents != {}:
                self.constrains_network_a = Network(self.graph, team_a, goals, a_constraints, objective="CONSTRAINTS")
                is_improving = False
                for agent in team_a.get_agents_list():
                    self.team_a_strategy[agent] = self.constrains_network_a.strategy[agent] # Update strategy for agent
                    for loc in hot_swaps_locations:
                        if loc in self.team_a_strategy[agent]:
                            self.team_a_strategy[agent].remove(loc) # Remove from strategy path the locations where it collides with other agents in a 'hot-swap' 
                    if len(self.constrains_network_a.strategy[agent]) > 1: # Meaning the agent now have a solution
                        is_improving = True
                        del team_a.agents[agent] # Remove from team for next iteration of the main loop
                        if self.team_a_strategy[agent][-1] in a_constraints: # If this path's goal has a constraint
                            del a_constraints[self.team_a_strategy[agent][-1]] # Remove constraint
                            hot_swaps_locations.append(self.team_a_strategy[agent][-1]) # Add goal to hot-swapping locations
                        for item in a_constraints:
                            a_constraints[item] += 1 # Increase the constraint by 1, to compensate for the 'jump' that happens when hot-swapping
                        del goals.agents[goals.get_agent_by_location(self.constrains_network_a.strategy[agent][-1])] # Remove goal
            print("------- Strategy ---------")
            print(self.team_a_strategy)

            # In this goal we process the paths generated from the previous code to official paths, fixing the gaps
            # left by the hot-swapping procedure

            # Go through each index in the longest strategy (skip 0 as it is the starting location)
            for i in range(1, max([len(self.team_a_strategy[item]) for item in self.team_a_strategy])):
                for agent1 in self.team_a_strategy: # Go through each agent in strategy
                    if len(self.team_a_strategy[agent1]) <= i: 
                        continue # If current path shorter then i

                    # Calculate max, min, diff in the path's i - 1 and i locations
                    max_loc = max(int(self.team_a_strategy[agent1][i]), int(self.team_a_strategy[agent1][i - 1]))
                    min_loc = min(int(self.team_a_strategy[agent1][i]), int(self.team_a_strategy[agent1][i - 1]))
                    diff = max_loc - min_loc
                    if abs(diff) in [1, 8]:
                        continue # If Diff is 1 or 8 that means single horizontal/vertical steps, while every other result means a gap needs fixing 
                    for agent2 in self.team_a_strategy: # Go each other agent in strategy
                        if len(self.team_a_strategy[agent2]) <= i - 1 or agent1 == agent2:
                            continue # If current path shorter then i - 1 or the same as the path we are fixing
                        if int(self.team_a_strategy[agent2][i - 1]) in range(min_loc + 1, max_loc): # If current path has the location we need to fix the gap
                            sub_path1 = self.team_a_strategy[agent1][i:]
                            sub_path2 = self.team_a_strategy[agent2][i - 1:]
                            self.team_a_strategy[agent1] = self.team_a_strategy[agent1][:i] + sub_path2
                            self.team_a_strategy[agent2] = self.team_a_strategy[agent2][:i] + sub_path1
                            break

            print("------- Strategy ---------")
            print(self.team_a_strategy)
    

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
            



