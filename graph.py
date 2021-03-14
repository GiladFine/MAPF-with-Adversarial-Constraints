import networkx as nx
import matplotlib.pyplot as plt
import json
from math import inf

class Graph:
    def __init__(self, edges):
        self.set_edges(edges)
        self.network = nx.Graph()
        self.network.add_edges_from(self.edges)
        self.UNREACHABLE = self.network.number_of_nodes() * 100000

    def set_edges(self, edges):
        self.edges = edges
        self.edges_to_transitions()

    
    def set_transitions(self, transitions):
        self.transitions = transitions
        self.transitions_to_edges()

    
    def get_vertices_list(self):
        vertices_list = []
        for item in self.edges:
            if item[0] not in vertices_list:
                vertices_list.append(item[0])
            if item[1] not in vertices_list:
                vertices_list.append(item[1])

        return vertices_list


    def edges_to_transitions(self):
        self.transitions = {}
        for item in self.edges:
            if item[0] in self.transitions:
                if not item[1] in self.transitions[item[0]]:
                    self.transitions[item[0]].append(item[1])
            else:
                self.transitions[item[0]] = [item[1]]

            if item[1] in self.transitions:
                if not item[0] in self.transitions[item[1]]:
                    self.transitions[item[1]].append(item[0])
            else:
                self.transitions[item[1]] = [item[0]]


    def transitions_to_edges(self):
        tmp_edges = []
        for src in self.transitions:
            for dst in self.transitions[src]:
                self.edges.append([src, dst])

        self.edges = []
        for item in tmp_edges:
            if item not in self.edges:
                self.edges.append(item)


    def calc_node_distance(self, src, dst):
        try:
            return nx.shortest_path_length(self.network, src, dst)
        except:
            return self.UNREACHABLE


    def get_next_move(self, vertex):
        return self.transitions[vertex] if vertex in self.transitions else []


    def visualize(self):
        nx.draw_networkx(self.network)
        plt.show()


    def print(self):
        print(json.dumps(self.transitions, indent=1, sort_keys=True))

