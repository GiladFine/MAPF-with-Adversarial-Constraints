import networkx as nx
import matplotlib.pyplot as plt


class Network:
    def __init__(self, graph, team, goals):
        self.original_graph = graph
        self.team = team
        self.goals = goals
        self.strategy = {}
        self.time_expended_graph = None
        self.propagation_const = 0
        self.flow_dict = {}
        self.flow_cost = 0
        self.flow_value = 0
        self.build_network()


    def get_max_distance(self):
        max_distance = 0
        for agent_location in self.team.get_locations_list():
            for goal_location in self.goals.get_locations_list():
                cur_distance = self.original_graph.calc_node_distance(agent_location, goal_location)
                if cur_distance > max_distance and cur_distance < self.original_graph.UNREACHABLE:
                    max_distance = cur_distance

        return max_distance


    def create_subgraph(self, index):
        tmp_edges_list = []
        nodes_visited = []
        for base_node in self.original_graph.network.nodes():
            b_node_src = str(index) + "\'," + base_node
            b_node_dst = str(index + 1) + "," + base_node
            b_node_dst_tag = str(index + 1) + "\'," + base_node
            tmp_edges_list.extend([
                (b_node_src, b_node_dst, {"capacity": 1, "weight": 1}),
                (b_node_dst, b_node_dst_tag, {"capacity": 1, "weight": 0})
            ])

            if index == 0 and base_node in self.team.get_locations_list():
                tmp_edges_list.append(("src", b_node_src, {"capacity": 1, "weight": 0}))

            if base_node in self.goals.get_locations_list():
                tmp_edges_list.append((b_node_dst_tag, "dst", {"capacity": 1, "weight": 0}))

            for connected_node in self.original_graph.network.neighbors(base_node):
                if connected_node in nodes_visited:
                    continue
                c_node_src = str(index) + "\'," + connected_node
                c_node_dst = str(index + 1) + "," + connected_node
                tmp_src = b_node_src + "-" + connected_node 
                tmp_dst = b_node_dst + "-" + connected_node
                tmp_edges_list.extend([
                    (b_node_src, tmp_src, {"capacity": 1, "weight": 0}),
                    (c_node_src, tmp_src, {"capacity": 1, "weight": 0}),
                    (tmp_src, tmp_dst, {"capacity": 1, "weight": 1}),
                    (tmp_dst, b_node_dst, {"capacity": 1, "weight": 0}),
                    (tmp_dst, c_node_dst, {"capacity": 1, "weight": 0}), 
                ])
            
            nodes_visited.append(base_node)

        edges_list = []
        [edges_list.append(item) for item in tmp_edges_list if item not in edges_list]
        return edges_list    
        

    def build_network(self):
        self.propagation_const = self.get_max_distance() + self.original_graph.network.number_of_nodes() + 1
        self.time_expended_graph = nx.DiGraph()
        edges_list = []
        for i in range(self.propagation_const):
            edges_list.extend(self.create_subgraph(i))
        
        self.time_expended_graph.add_edges_from(edges_list)
        self.calc_flow_and_cost()
        self.calc_strategy()

        
    def visualize(self):
        nx.draw_networkx(self.time_expended_graph)
        plt.show()


    def calc_flow_and_cost(self):
        self.flow_dict = nx.max_flow_min_cost(self.time_expended_graph, "src", "dst")
        self.flow_cost = nx.cost_of_flow(self.time_expended_graph, self.flow_dict)
        self.flow_value = sum((self.flow_dict[u]["dst"] for u in self.time_expended_graph.predecessors("dst"))) - sum((self.flow_dict["dst"][v] for v in self.time_expended_graph.successors("dst")))


    def calc_strategy(self):
        #TODO
        pass
            
