import networkx as nx
import matplotlib.pyplot as plt

# This class represents the time-expanded-graph reduction described by Yu & LaValle in order to solve Anonymous-MAPF polynomially
class Network:
    def __init__(self, graph, team, goals, reach_constraints = None, hole_constraints = None, objective = "MAKESPAN"):
        self.objective = objective
        self.reach_constraints = reach_constraints
        self.hole_constraints = hole_constraints
        self.original_graph = graph
        self.team = team
        self.goals = goals
        self.strategy = {}
        self.time_expanded_graph = nx.DiGraph()
        self.propagation_const = self.get_max_distance() + self.original_graph.network.number_of_nodes() + 1
        self.flow_dict = {}
        self.flow_cost = 0
        self.flow_value = 0
        self.build_network()


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

        if self.hole_constraints and node in self.hole_constraints and index in self.hole_constraints[node]:
            return True

        return False
        


    # This function returns a list of edges consist with a subgraph of the i-th propagation of the original graph
    def create_subgraph(self, index):
        tmp_edges_list = []
        nodes_visited = []
        for base_node in self.original_graph.network.nodes():

            if self._is_constrainted(base_node, index):
                continue

            b_node_src = str(index) + "\'," + base_node
            b_node_dst = str(index + 1) + "," + base_node
            b_node_dst_tag = str(index + 1) + "\'," + base_node
            # Create horizontal edges in the graph (blue & green in the Yu & LaValle example)
            tmp_edges_list.extend([
                (b_node_src, b_node_dst, {"capacity": 1, "weight": 0 if self.objective == "TOTAL_DISTANCE" else 1}), # Green edge
                (b_node_dst, b_node_dst_tag, {"capacity": 1, "weight": 0}) # Blue edge
            ])

            # Connect src to initial locations on the first subgraph
            if index == 0 and base_node in self.team.get_locations_list():
                tmp_edges_list.append(("src", b_node_src, {"capacity": 1, "weight": 0}))

            # Connect the dst nodes to the goals nodes
            if base_node in self.goals.get_locations_list():
                tmp_edges_list.append((b_node_dst_tag, base_node + "-dst", {"capacity": 1, "weight": 1}))
                tmp_edges_list.append((base_node + "-dst", "dst", {"capacity": 1, "weight": 0}))  

            # Create the X-gadget for every possible move from current base_node
            for connected_node in self.original_graph.network.neighbors(base_node):
                if self._is_constrainted(base_node, index):
                    continue
                if connected_node in nodes_visited:
                    continue
                c_node_src = str(index) + "\'," + connected_node
                c_node_dst = str(index + 1) + "," + connected_node
                tmp_src = b_node_src + "-" + connected_node 
                tmp_dst = b_node_dst + "-" + connected_node
                tmp_edges_list.extend([
                    (b_node_src, tmp_src, {"capacity": 1, "weight": 0}),
                    (c_node_src, tmp_src, {"capacity": 1, "weight": 0}),
                    (tmp_src, tmp_dst, {"capacity": 1, "weight": 1}), # Horizontal edge
                    (tmp_dst, b_node_dst, {"capacity": 1, "weight": 0}),
                    (tmp_dst, c_node_dst, {"capacity": 1, "weight": 0}), 
                ])
            
            nodes_visited.append(base_node)

        # Remove duplicates
        edges_list = []
        [edges_list.append(item) for item in tmp_edges_list if item not in edges_list]
        return edges_list    
        

    # This function creates the time-expanded-graph by gradually creating & connecting subgraphs until all goals are reached by the flow
    def build_network(self):        
        for i in range(self.propagation_const):
            edges_list = []
            edges_list.extend(self.create_subgraph(i))
            self.time_expanded_graph.add_edges_from(edges_list)
            self.calc_flow_and_cost()

            # This means that all the max-flow was reached, indicating a solution for the Path-Finding problem
            if self.flow_value == len(self.goals.get_locations_list()):
                break

        try:
            self.calc_strategy()
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


    # This function calculates the flow on the time-expanded-graph
    def calc_flow_and_cost(self):
        try:
            self.flow_dict = nx.max_flow_min_cost(self.time_expanded_graph, "src", "dst")
            self.flow_cost = nx.cost_of_flow(self.time_expanded_graph, self.flow_dict)
            self.flow_value = sum((self.flow_dict[u]["dst"] for u in self.time_expanded_graph.predecessors("dst"))) - sum((self.flow_dict["dst"][v] for v in self.time_expanded_graph.successors("dst")))
        except:
            self.flow_dict={}
            self.flow_cost=0
            self.flow_value=0


    # This function derrive a Makespan-optimal strategy from the flow_dict
    def calc_strategy(self):
        for base_node in self.flow_dict["src"].keys():
            path_list = [base_node.split(",")[1]] # Add initial location to path
            
            if self.flow_dict["src"][base_node] == 0: # Ignore nodes that has no flow
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
                curr_round = splitted_curr[0][:-1]
                next_round = str(int(curr_round) + 1)

                # If we have reached dst the path if completed
                if "dst" in splitted_next[0]:
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

