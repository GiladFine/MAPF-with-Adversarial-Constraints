from random import randint
from grid import Grid
from graph import Graph
from team import Team
from utils import *

class Environment:
    def __init__(self, grid_size=GRID_SIZE, teams_size=TEAMS_SIZE, obstacle_frequency=OBSTACLE_FREQUENCY):
        # Generate random grid and convert it to graph
        self.grid = Grid(self.random_grid(grid_size))
        self.graph = Graph(self.grid.convert_to_graph())

        # Generate team A
        self.graph_available_vertices = self.graph.get_vertices_list()
        self.team_a = Team(self.random_team('a', teams_size, self.graph_available_vertices))

        # Remove all vertices occupied by team A
        self.graph_available_vertices = [vertex for vertex in self.graph_available_vertices if vertex not in self.team_a.get_locations_list()]
        
        # Generate team B
        self.team_b = Team(self.random_team('b', teams_size, self.graph_available_vertices))
        self.graph_available_vertices = [vertex for vertex in self.graph_available_vertices if vertex not in self.team_b.get_locations_list()]

        # Generate target goals G
        self.goals = Team(self.random_team('g', teams_size, self.graph_available_vertices))


    # Generate random grid by randomly assign obastacles until their frequency is meating the parameter
    def random_grid(self, size):
        grid = [[True for i in range(size)] for j in range(size)]
        num_of_obastacle = 0
        while (num_of_obastacle / (size * size)) < OBSTACLE_FREQUENCY:
            row_location, col_location = randint(0, size - 1), randint(0, size - 1)
            if grid[row_location][col_location]:
                num_of_obastacle += 1
                grid[row_location][col_location] = False
        return grid


    # Generate random graph by randomly adding edges
    def random_graph(self, v_size, e_size):
        vertices = range(1, v_size + 1)
        edges = []
        num_of_edges = 0
        while num_of_edges < e_size:
            v1, v2 = randint(1, v_size + 1), randint(1, v_size + 1)
            if v1 == v2: # If the same vertex was selected, skip
                continue
            if [v1, v2] not in edges and [v2, v1] not in edges: # If edge allready exists, skip
                num_of_edges += 1
                edges.append([v1, v2])
        
        return edges


    # Generate random team by randomly selecting locations for each agent
    def random_team(self, letter, size, vertices_list):
        team = {}
        for i in range(1, size + 1):
            agent = letter + str(i)
            rand_vertex = vertices_list[randint(0, len(vertices_list) - 1)]
            vertices_list.remove(rand_vertex) # Remove from possible locations for future agents
            team[agent] = rand_vertex

        return team