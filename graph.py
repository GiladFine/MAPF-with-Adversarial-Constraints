import networkx as nx
import matplotlib.pyplot as plt
import json
from math import inf

# This class represents a graph of locations in the world
# The graph has 2 possible representations: edges & transitions
# Edges - a list of the edges in the graph
# Transitions - a dictionaty where the keys are the graph nodes and the values are list of location describing the neighbors of the key node
class Graph:
    def __init__(self, edges):
        self.set_edges(edges)

        # This is a constant that holds a value for the distance between two non-connected location
        self.UNREACHABLE = self.network.number_of_nodes() * 100000


    # This function builds the graph from the given edges 
    def set_edges(self, edges):
        self.network = nx.Graph()
        self.network.add_edges_from(edges)

        # Keep only the largest connected component, so the graph will be consist of one component only
        self.network = self.network.subgraph(max(nx.connected_components(self.network), key=len))
        self.edges = self.network.edges()

        # Create the transition function
        self.edges_to_transitions()

    
    # This function creates a transition representation of the graph and convert it to edges representation
    def set_transitions(self, transitions):
        self.transitions = transitions
        self.transitions_to_edges()

    
    # This function returns a list of all the nodes in the graph
    def get_vertices_list(self):
        vertices_list = []
        for item in self.edges:
            if item[0] not in vertices_list:
                vertices_list.append(item[0])
            if item[1] not in vertices_list:
                vertices_list.append(item[1])

        return vertices_list


    # This function converts the current edges representation to the transitions representation
    def edges_to_transitions(self):
        self.transitions = {}
        for item in self.edges:
            if item[0] in self.transitions:
                if not item[1] in self.transitions[item[0]]: # New transition to existing list
                    self.transitions[item[0]].append(item[1])
            else:
                self.transitions[item[0]] = [item[1]] # First transition in the list

            if item[1] in self.transitions:
                if not item[0] in self.transitions[item[1]]:
                    self.transitions[item[1]].append(item[0])
            else:
                self.transitions[item[1]] = [item[0]]


    # This function converts the current transitions representation to the edges representation
    def transitions_to_edges(self):
        tmp_edges = []

        # Create all edges with duplications
        for src in self.transitions:
            for dst in self.transitions[src]:
                self.edges.append([src, dst])

        # Remove duplicates
        self.edges = []
        for item in tmp_edges:
            if item not in self.edges:
                self.edges.append(item)


    # This function calculates the distance between two locations in the graph
    def calc_node_distance(self, src, dst):
        try:
            return nx.shortest_path_length(self.network, src, dst)
        except:
            return self.UNREACHABLE # The constant distance between two non-connected nodes


    # This function returns the list of transitions for a given node
    def get_next_move(self, vertex):
        return self.transitions[vertex] if vertex in self.transitions else []


    # This function displays the graph
    def visualize(self):
        nx.draw_networkx(self.network)
        plt.show()


    # This function prints the graph as a transitions dict
    def print(self):
        print(json.dumps(self.transitions, indent=1, sort_keys=True))

