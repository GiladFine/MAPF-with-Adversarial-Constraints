from copy import deepcopy
import datetime
from typing import List
from time import time
from func_timeout import func_set_timeout
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations

from max_flow_min_cost_solver import MaxFlowMinCostSolver

# This class represents the time-expanded-graph reduction described by Yu & LaValle in order to solve Anonymous-MAPF polynomially
class Network:
    def __init__(self, graph, team, goals, network_mode, reach_constraints = None, objective = "MAKESPAN"):
        self.objective = objective
        self.reach_constraints = reach_constraints
        # print(f"reach_constraints:\n{self.reach_constraints}")
        self.original_graph = graph
        self.team = team
        self.goals = goals
        self.network_mode = network_mode
        self.hs_time_delay = 0
        self.strategy = {}
        self.time_expanded_graph = nx.DiGraph()
        self.time_expanded_graph_orig = nx.DiGraph()
        self.propagation_const = max(self.reach_constraints.values())
        self.flow_dict = {}
        self.flow_cost = 0
        self.flow_value = 0
        self.debug = False
        self.solver_time = -1.0
        self.brute_force = True
        if self.network_mode == "stays":
            self.build_network_stays_on_targets()
        elif self.network_mode == "disappearing":
            self.build_network_disappearing()
        elif self.network_mode == "demands":
            self.build_network_with_demands()
        elif "hot_swapping" in self.network_mode:
            self.hs_time_delay = int(self.network_mode.split('-')[1])
            self.network_mode = "hot_swapping"
            self.build_network_hot_swapping()

    # This function returns the maximal distance between any agent to any goal in the graph
    def get_max_distance(self):
        max_distance = 0
        for agent_location in self.team.get_locations_list():
            for goal_location in self.goals.get_locations_list():
                cur_distance = self.original_graph.calc_node_distance(agent_location, goal_location)
                if cur_distance > max_distance and cur_distance < self.original_graph.UNREACHABLE:
                    max_distance = cur_distance

        return max_distance


    def _is_constrainted(self, node, index):
        if self.objective != "CONSTRAINTS":
            return False
                
        if self.reach_constraints and node in self.reach_constraints and self.reach_constraints[node] <= index:
            return True

        return False

    def edge_cost(self, network_mode: str, node: str, index: int, edge_cost: int):
        if network_mode != "hot_swapping":
            return 0
        if (
            node in self.reach_constraints
            and index >= self.reach_constraints.get(node) - 1
        ):
            return 0
        return edge_cost

    # This function returns a list of edges consist with a subgraph of the i-th propagation of the original graph
    def create_subgraph(self, index: int, reached_nodes: List[str], network_mode: str, edge_cost_for_hs: int = 0):
        tmp_edges_list = []
        nodes_visited = []
        all_base_nodes_neighbors = []
        nodes_lower_bounds_total_input = {}
        nodes_lower_bounds_total_output = {}
        
        for goal in sorted(self.goals.get_locations_list()):
            goal_node_dst = str(index + 1) + "," + goal
            goal_node_dst_tag = str(index + 1) + "\'," + goal
            
            if network_mode == "demands":
                if index == max(self.reach_constraints.values()) - 1:  # Connect the dst nodes to the goals nodes
                    tmp_edges_list.append((goal_node_dst_tag, goal + "-dst", {"capacity": 1}))
                    tmp_edges_list.append((goal + "-dst", "dst", {"capacity": 1}))

                if self._is_constrainted(goal, index + 1):  
                    if goal_node_dst in nodes_lower_bounds_total_output:
                        nodes_lower_bounds_total_output[goal_node_dst] += 1
                    else:
                        nodes_lower_bounds_total_output[goal_node_dst] = 1
                        
                    if goal_node_dst_tag in nodes_lower_bounds_total_input:
                        nodes_lower_bounds_total_input[goal_node_dst_tag] += 1
                    else:
                        nodes_lower_bounds_total_input[goal_node_dst_tag] = 1
    
            elif network_mode == "disappearing":
                if index == self.reach_constraints[goal] - 1:  # Connect the dst nodes to the goals nodes
                    tmp_edges_list.append((goal_node_dst_tag, goal + "-dst", {"capacity": 1}))
                    tmp_edges_list.append((goal + "-dst", "dst", {"capacity": 1}))
            elif network_mode == "stays" or network_mode == "hot_swapping":
                if index == max(self.reach_constraints.values()) - 1:  # Connect the dst nodes to the goals nodes
                    tmp_edges_list.append((goal_node_dst_tag, goal + "-dst", {"capacity": 1}))
                    tmp_edges_list.append((goal + "-dst", "dst", {"capacity": 1}))

        for base_node in sorted(reached_nodes):
            current_base_node_neighbors = list(self.original_graph.network.neighbors(base_node))
            all_base_nodes_neighbors.extend(current_base_node_neighbors)
            b_node_src = str(index) + "\'," + base_node
            b_node_dst = str(index + 1) + "," + base_node
            b_node_dst_tag = str(index + 1) + "\'," + base_node
            
            # Create horizontal edges in the graph (blue & green in the Yu & LaValle example)
            tmp_edges_list.extend([
                (b_node_src, b_node_dst, {"capacity": 1}), # Green edge
                (
                    b_node_dst,
                    b_node_dst_tag,
                    {
                        "capacity": 1,
                        "weight": self.edge_cost(
                            network_mode=network_mode,
                            node=base_node,
                            index=index,
                            edge_cost=edge_cost_for_hs,
                        ),
                    }
                ) # Blue edge + cost for HS
            ])
            
            if network_mode == "stays" and self._is_constrainted(base_node, index):
                continue  # Trim network when stays on targets

            # Connect src to initial locations on the first subgraph
            if index == 0 and base_node in self.team.get_locations_list():
                tmp_edges_list.append(("src", b_node_src, {"capacity": 1}))

            # Create the X-gadget for every possible move from current base_node
            for connected_node in sorted(current_base_node_neighbors):
                if network_mode == "stays" and self._is_constrainted(connected_node, index):
                    continue  # Trim network when stays on targets

                if connected_node in nodes_visited:
                    continue
                c_node_src = str(index) + "\'," + connected_node
                c_node_dst = str(index + 1) + "," + connected_node
                c_node_dst_tag = str(index + 1) + "\'," + connected_node
                
                c_node_dst_hs_delayed = (
                    str(index + 1 + self.hs_time_delay) + "," + connected_node
                    if (
                        self.network_mode == "hot_swapping"
                        and connected_node in self.goals.get_locations_list()
                        and self._is_constrainted(connected_node, index)
                        and self.hs_time_delay > 0
                    )
                    else None
                )
                c_node_dst_hs_delayed_edge_cost = (
                    0
                    if c_node_dst_hs_delayed is None
                    else self.hs_time_delay * (1 + edge_cost_for_hs)
                )
            
                b_node_dst_hs_delayed = (
                    str(index + 1 + self.hs_time_delay) + "," + base_node
                    if (
                        self.network_mode == "hot_swapping"
                        and base_node in self.goals.get_locations_list()
                        and self._is_constrainted(base_node, index)
                        and self.hs_time_delay > 0
                    )
                    else None
                )
                b_node_dst_hs_delayed_edge_cost = (
                    0
                    if b_node_dst_hs_delayed is None
                    else self.hs_time_delay * (1 + edge_cost_for_hs)
                )
                
                tmp_src = b_node_src + "-" + connected_node 
                tmp_dst = b_node_dst + "-" + connected_node
                tmp_edges_list.extend([
                    (b_node_src, tmp_src, {"capacity": 1}),
                    (c_node_src, tmp_src, {"capacity": 1}),
                    (tmp_src, tmp_dst, {"capacity": 1, "weight": 1}), # Horizontal edge - weight (cost) value is 1 to messure fuel consumption on move actions
                    (tmp_dst, b_node_dst_hs_delayed or b_node_dst, {
                        "capacity": 1,
                        "weight": b_node_dst_hs_delayed_edge_cost,
                    }),
                    (tmp_dst, c_node_dst_hs_delayed or c_node_dst, {
                        "capacity": 1,
                        "weight": c_node_dst_hs_delayed_edge_cost,
                    }),
                    (c_node_dst, c_node_dst_tag, {
                        "capacity": 1,
                        "weight": self.edge_cost(
                            network_mode=network_mode,
                            node=connected_node,
                            index=index,
                            edge_cost=edge_cost_for_hs,
                        ),
                    }),
                ])

            nodes_visited.append(base_node)
            
        reached_nodes.extend(all_base_nodes_neighbors)
        reached_nodes = list(set(reached_nodes))

        # Remove duplicates
        edges_list = []
        [edges_list.append(item) for item in tmp_edges_list if item not in edges_list]
        return edges_list, nodes_lower_bounds_total_input, nodes_lower_bounds_total_output, reached_nodes
    
    def _get_all_combinations(self, l):
        if not self.brute_force:
            return l
        comb = []
        for i in range(len(l) + 1):
            # Generating sub list
            comb += [list(j) for j in combinations(l, i)]
        # Returning list
        comb.sort(key=len, reverse=True)
        return comb
    
    def _prepare_next_combination(self, comb):
        self.time_expanded_graph = deepcopy(self.time_expanded_graph_orig)
        removed_edges = []
        for goal in list(set(self.goals.get_locations_list()) - set(comb)):
            removed_edges.append((f"{goal}-dst", "dst"))
            removed_edges.extend(
                [
                    edge
                    for edge in self.time_expanded_graph.edges
                    if (
                        edge[0] == "fake_src" and edge[1].split(",")[1] == goal
                    ) or (
                        edge[1] == f"{goal}-dst"
                    ) or (
                        edge[1] == "fake_dst" and edge[0].split(",")[1] == goal
                    )
                ]
            )
        
        self.time_expanded_graph.remove_edges_from(removed_edges)
        return removed_edges

    def build_network_hot_swapping(self):
        number_of_targets = len(self.goals.get_locations_list())
        max_number_of_hs_actions = (number_of_targets * number_of_targets - number_of_targets) / 2
        sum_of_deadlines = sum(self.reach_constraints.values())
        edge_cost = sum_of_deadlines + max_number_of_hs_actions + 1

        reached_nodes = self.team.get_locations_list()       
        for i in range(self.propagation_const):
            edges_list, _, _, reached_nodes = self.create_subgraph(index=i, network_mode="hot_swapping", reached_nodes=reached_nodes, edge_cost_for_hs=edge_cost)
            self.time_expanded_graph.add_edges_from(edges_list)
    
        self.calc_flow_and_cost()
        max_allowd_flow = edge_cost * (sum_of_deadlines - number_of_targets + 1)

        # print(f"flow val - {self.flow_value}, flow cost - {self.flow_cost}, max_allowd_flow_cost - {max_allowd_flow}")
        # This means that all the max-flow was reached, indicating a solution for the Path-Finding problem
        if (
            self.flow_value != len(self.goals.get_locations_list())
            or self.flow_cost >= max_allowd_flow
        ):
            raise ValueError("No Solution!!!", self.flow_value, self.solver_time)

        try:
            if self.hs_time_delay == 0:
                self.calc_strategy()
            else:
                self.hs_calc_strategy_with_time_delays()

        except:
            self.strategy = None
            
    def build_network_with_demands(self):
        reached_nodes = self.team.get_locations_list()
        self.time_expanded_graph.add_node("fake_src")
        self.time_expanded_graph.add_node("fake_dst")
        self.time_expanded_graph.add_edges_from(
            [
                ("src", "dst", {"capacity": 10000}),
                ("dst", "src", {"capacity": 10000}),
            ]
        )
        
        before_time = time()
        for i in range(self.propagation_const):
            edges_list, nodes_lower_bounds_total_input, nodes_lower_bounds_total_output, reached_nodes = self.create_subgraph(index=i, network_mode="demands", reached_nodes=reached_nodes)
            
            self.time_expanded_graph.add_edges_from(edges_list)
            
            extra_edges = []
            extra_edges.extend(
                [
                    ("fake_src", node, {"capacity": nodes_lower_bounds_total_input[node]})
                    for node in self.time_expanded_graph.nodes
                    if node in nodes_lower_bounds_total_input
                ]
            )
            
            extra_edges.extend(
                [
                    (node, "fake_dst", {"capacity": nodes_lower_bounds_total_output[node]})
                    for node in self.time_expanded_graph.nodes
                    if node in nodes_lower_bounds_total_output
                ]
            )
            
            self.time_expanded_graph.add_edges_from(extra_edges)

        after_time = time()
        self.graph_creation_time = after_time - before_time
            
        self.time_expanded_graph_orig = deepcopy(self.time_expanded_graph)
        # goal_combs = self._get_all_combinations(self.goals.get_locations_list())
        goal_combs = [self.goals.get_locations_list()]
        self.solution_found = False
        debug_break = False
        self.comb_times = []
        for comb in goal_combs:
            self._prepare_next_combination(comb)
            
            before_time = time()
            try:
                self.calc_flow_and_cost_auxilary(forceTimeout=(300 - self.graph_creation_time - sum(self.comb_times)))
            except:
                pass
            after_time = time()
            self.comb_times.append(after_time - before_time)
            if self.graph_creation_time + sum(self.comb_times) >= 299: # 5 minutes timeout
                self.solution_size = len(comb)
                self.strategy = None
                return

            # This means that all the max-flow was reached, indicating a solution for the Path-Finding problem
            if self.check_demands_flow_dict_result(comb=comb) or debug_break:
                self.solution_found = True # GOOD!
                self.solution_size = len(comb)
                break
            
        if not self.solution_found:
            raise ValueError("No Solution!!!", self.flow_value, self.solver_time)
        
        try:
            if self.debug == True:
                self.write_flow_file()
                
            self.calc_strategy()
            
        except Exception as e:
            self.strategy = None

    def check_demands_flow_dict_result(self, comb):
        if self.flow_dict["dst"]["src"] < len(comb):
            return False
        for goal in comb:
            constraint = min([int(item.split("'")[0]) for item in self.flow_dict["fake_src"] if f",{goal}" in item])
            if constraint > self.reach_constraints[goal]:
                return False
        return True

    # def calc_simplified_flow_list(self):
    #     self.simplified_flow_list = []
    #     for src, inner_dict in self.flow_dict.items():
    #         if 1 in inner_dict.values():
    #             dsts = []
    #             for dst, val in inner_dict.items():
    #                 if val == 1:
    #                     dsts.append(dst)
    #             self.simplified_flow_list.append(f"{src} -> {dsts}")
                
    #     if "src" in self.flow_dict["dst"]:
    #         dst_to_src_flow_val = self.flow_dict["dst"]["src"]
    #         self.simplified_flow_list.append(f"dst -> src X{dst_to_src_flow_val}")
    
    # def write_flow_file(self):
    #     filename = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
    #     with open(f"./results/{filename}.txt", "w") as fp:
    #         for item in self.simplified_flow_list:
    #             fp.write(f"{item}\n")
        
    # This function creates the time-expanded-graph by gradually creating & connecting subgraphs until all goals are reached by the flow
    def build_network_disappearing(self): 
        reached_nodes = self.team.get_locations_list()       
        for i in range(self.propagation_const):
            edges_list, _, _, reached_nodes = self.create_subgraph(index=i, network_mode="disappearing", reached_nodes=reached_nodes)
            self.time_expanded_graph.add_edges_from(edges_list)
    
        self.calc_flow_and_cost()
        # This means that all the max-flow was reached, indicating a solution for the Path-Finding problem
        if self.flow_value != len(self.goals.get_locations_list()):
            raise ValueError("No Solution!!!", self.flow_value, self.solver_time)

        try:
            self.calc_strategy()

        except:
            self.strategy = None

    def build_network_stays_on_targets(self): 
        reached_nodes = self.team.get_locations_list()       
        for i in range(self.propagation_const):
            edges_list, _, _, reached_nodes = self.create_subgraph(index=i, network_mode="stays", reached_nodes=reached_nodes)
            self.time_expanded_graph.add_edges_from(edges_list)
    
        self.calc_flow_and_cost()
        # This means that all the max-flow was reached, indicating a solution for the Path-Finding problem
        if self.flow_value != len(self.goals.get_locations_list()):
            raise ValueError("No Solution!!!", self.flow_value, self.solver_time)

        try:
            self.calc_strategy()
            pass
        except:
            self.strategy = None

        
    # This function displays the time-expanded-graph
    def visualize(self):
        nx.draw_networkx(self.time_expanded_graph)
        plt.show()


    def visualize_flow(self):
        G = nx.DiGraph()
        labels = {}
        for node_a in self.flow_dict.keys():
            for node_b in self.flow_dict[node_a]:
                if self.flow_dict[node_a][node_b] > 0:
                    G.add_edge(node_a, node_b, weight=self.flow_dict[node_a][node_b])
                    labels[(node_a, node_b)] = self.flow_dict[node_a][node_b]
                    print("{0} -> {1}, val = {2}".format(node_a, node_b, self.flow_dict[node_a][node_b]))

        green_edges = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] == 1]
        blue_edges = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] == 0]
        pos = nx.spring_layout(G)  # positions for all nodes

        # nodes
        nx.draw_networkx_nodes(G, pos, node_size=100)

        # edges
        nx.draw_networkx_edges(G, pos, edgelist=green_edges, width=1, edge_color="g")
        nx.draw_networkx_edges(G, pos, edgelist=blue_edges, width=1, edge_color="b")

        # labels
        nx.draw_networkx_labels(G, pos, font_size=8, font_family="sans-serif")
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=10)


        plt.axis("off")
        plt.show()
    
    @func_set_timeout(timeout=300, allowOverride=True)
    def calc_flow_and_cost_auxilary(self):
        try:
            self.flow_dict = nx.maximum_flow(self.time_expanded_graph, "fake_src", "fake_dst")[1]
            self.flow_cost = nx.cost_of_flow(self.time_expanded_graph, self.flow_dict)
            self.flow_value = sum((self.flow_dict[u]["fake_dst"] for u in self.time_expanded_graph.predecessors("fake_dst"))) - sum((self.flow_dict["fake_dst"][v] for v in self.time_expanded_graph.successors("fake_dst")))
        except:
            self.flow_dict={}
            self.flow_cost=0
            self.flow_value=0
    
    # This function calculates the flow on the time-expanded-graph
    def calc_flow_and_cost(self):
        try:
            before = time()
            print("START")
            solver = MaxFlowMinCostSolver(self.time_expanded_graph)
            self.flow_dict, self.flow_value, self.flow_cost = solver.max_flow_min_cost()
            after = time()
            self.solver_time = after - before
            print(f"FLOW CALC TOOK - {self.solver_time} sec with new solver")
            
            # self.flow_dict = nx.max_flow_min_cost(self.time_expanded_graph, "src", "dst")
            # # self.flow_dict = nx.maximum_flow(self.time_expanded_graph, "src", "dst")[1]
            # self.flow_cost = nx.cost_of_flow(self.time_expanded_graph, self.flow_dict)
            # self.flow_value = sum((self.flow_dict[u]["dst"] for u in self.time_expanded_graph.predecessors("dst"))) - sum((self.flow_dict["dst"][v] for v in self.time_expanded_graph.successors("dst")))            
            # after = time()
            # print(f"FLOW CALC TOOK - {after - before} sec with old solver")
        except:
            self.flow_dict={}
            self.flow_cost=0
            self.flow_value=0

    # This function derrive a Makespan-optimal strategy from the flow_dict
    def calc_strategy(self):
        src_node, dst_node = "src", "dst"
        
        for base_node in self.flow_dict[src_node].keys():
            if base_node == "dst":
                continue
            
            path_list = [base_node.split(",")[1]] # Add initial location to path
            
            if self.flow_dict[src_node][base_node] == 0: # Ignore nodes that has no flow
                self.strategy[self.team.get_agent_by_location(path_list[0])] = path_list
                continue
            
            curr_node = base_node
            while True:
                next_node = None

                # Find the next node the flow is going to
                for v in self.flow_dict[curr_node].keys():
                    if self.flow_dict[curr_node][v] >= 1:
                        next_node = v
                        break
                if next_node == None: # If no next node with flow exist, cut the path with ERROR
                    path_list.append("ERROR")
                    break

                splitted_next = next_node.split(",")
                splitted_curr = curr_node.split(",")
                curr_round = splitted_curr[0]
                if curr_round[-1] == "'":
                    curr_round = curr_round[:-1]
                next_round = str(int(curr_round) + 1)

                # If we have reached dst the path if completed
                if dst_node in splitted_next[0]:
                    break

                # If next node has a '-' it means there is a possibility that in the next round the flow is going to a different node
                if "-" in splitted_next[1]:
                    tmp_split = splitted_next[1].split("-")
                    second = tmp_split[0] if tmp_split[0] != path_list[-1] else tmp_split[1]
                    # This if checks whether it really is moving to a different location, and not returning to the original location from the X-gadget
                    if self.flow_dict[next_round + "," + splitted_next[1]][next_round + "," + second] < 1:
                        second = splitted_curr[1]
                else: # Next location is the same as current location
                    second = splitted_curr[1]
                path_list.append(second)
                curr_node = next_round + "'," + second

            # Add the path to the strategy
            self.strategy[self.team.get_agent_by_location(path_list[0])] = path_list

    def _get_next_node(self, curr_node):
        for v in self.flow_dict[curr_node].keys():
            if self.flow_dict[curr_node][v] >= 1:
                return v
        
        return None

    def hs_calc_strategy_with_time_delays(self):
        src_node, dst_node = "src", "dst"
        
        for base_node in self.flow_dict[src_node].keys():
            if base_node == "dst":
                continue
            
            path_list = [base_node.split(",")[1]] # Add initial location to path
            
            if self.flow_dict[src_node][base_node] == 0: # Ignore nodes that has no flow
                self.strategy[self.team.get_agent_by_location(path_list[0])] = path_list
                continue
            
            curr_node = base_node
            while True:
                next_node = None

                # Find the next node the flow is going to
                next_node = self._get_next_node(curr_node=curr_node)

                if next_node == None: # If no next node with flow exist, cut the path with ERROR
                    path_list.append("ERROR")
                    break

                splitted_next = next_node.split(",")
                splitted_curr = curr_node.split(",")
                curr_round = splitted_curr[0]
                if curr_round[-1] == "'":
                    curr_round = curr_round[:-1]
                next_round = str(int(curr_round) + 1)
                time_delayed_next_round = str(int(curr_round) + 1 + self.hs_time_delay)

                # If we have reached dst the path if completed
                if dst_node in splitted_next[0]:
                    break

                # If next node has a '-' it means there is a possibility that in the next round the flow is going to a different node
                if "-" in splitted_next[1]:
                    tmp_split = splitted_next[1].split("-")
                    second = tmp_split[0] if tmp_split[0] != path_list[-1] else tmp_split[1]
                    # This if checks whether it really is moving to a different location, and not returning to the original location from the X-gadget
                    try:
                        if self.flow_dict[next_round + "," + splitted_next[1]][next_round + "," + second] < 1:
                            second = splitted_curr[1]
                    except:
                        if self.flow_dict[next_round + "," + splitted_next[1]][time_delayed_next_round + "," + second] < 1:
                            second = splitted_curr[1]
                        else:
                            path_list.append(splitted_curr[1])
                            path_list.append(second)
                            curr_node = time_delayed_next_round + "'," + second
                            continue
                else: # Next location is the same as current location
                    second = splitted_curr[1]
                path_list.append(second)
                curr_node = next_round + "'," + second

            # Add the path to the strategy
            self.strategy[self.team.get_agent_by_location(path_list[0])] = path_list
