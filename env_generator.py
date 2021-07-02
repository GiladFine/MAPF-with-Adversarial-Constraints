from random import randint
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.animation import FuncAnimation
from grid import Grid
from graph import Graph
from team import Team
from utils import *
from math import floor

# This class randomly generates the environment for the game - world graph, teams, agents
class Environment:
    def __init__(self, map_file_name=None, grid_size=GRID_SIZE, teams_size=TEAMS_SIZE, obstacle_frequency=OBSTACLE_FREQUENCY):
        if map_file_name: # load map
            with open("input/" + map_file_name,"rt") as infile:
                map = [[1 if char == '.' else 0 for char in list(line.strip())] for line in infile.readlines()]
                self.grid = Grid(map)
                self.obstacle_frequency = sum(x.count(0) for x in map)
                self.grid_size = len(map)
        else: # Generate random grid and convert it to graph
            self.obstacle_frequency = obstacle_frequency
            self.grid_size = grid_size
            self.grid = Grid(self.random_grid())

        self.teams_size = teams_size
        self.graph = Graph(self.grid.convert_to_graph())

        # Generate team A
        self.graph_available_vertices = self.graph.get_vertices_list()
        self.team_a = Team(self.random_team('a', self.graph_available_vertices))

        # Remove all vertices occupied by team A
        self.graph_available_vertices = [vertex for vertex in self.graph_available_vertices if vertex not in self.team_a.get_locations_list()]
        
        # Generate team B
        self.team_b = Team(self.random_team('b', self.graph_available_vertices))
        self.graph_available_vertices = [vertex for vertex in self.graph_available_vertices if vertex not in self.team_b.get_locations_list()]

        # Generate target goals G
        self.goals = Team(self.random_team('g', self.graph_available_vertices))
        

    # Generate random grid by randomly assign obastacles until their frequency is meating the parameter
    def random_grid(self):
        grid = [[1 for i in range(self.grid_size)] for j in range(self.grid_size)]
        num_of_obastacle = 0
        while (num_of_obastacle / (self.grid_size * self.grid_size)) < self.obstacle_frequency:
            row_location, col_location = randint(0, self.grid_size - 1), randint(0, self.grid_size - 1)
            if grid[row_location][col_location]:
                num_of_obastacle += 1
                grid[row_location][col_location] = 0
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
    def random_team(self, letter, vertices_list):
        team = {}
        for i in range(1, self.teams_size + 1):
            agent = letter + str(i)
            rand_vertex = vertices_list[randint(0, len(vertices_list) - 1)]
            vertices_list.remove(rand_vertex) # Remove from possible locations for future agents
            team[agent] = rand_vertex

        return team


    def location_to_grid_position(self, location):
        x_pos = 0.5 + (location - 1) % self.grid_size
        y_pos = self.grid_size - floor((location - 1) / self.grid_size) - 0.5
        return x_pos, y_pos


    def visualize(self):
        cmap = colors.ListedColormap(['red','green'])
        plt.pcolor(self.grid.grid[::-1], cmap=cmap, edgecolors='k', linewidths=1)

        for agent in self.team_a.get_agents_list():
            x_pos, y_pos = self.location_to_grid_position(int(self.team_a.get_location_by_agent(agent)))
            plt.text(x_pos, y_pos, agent, size=8,
                ha="center", va="center",
                bbox=dict(boxstyle="circle", color="blue")
                )

        for agent in self.team_b.get_agents_list():
            x_pos, y_pos = self.location_to_grid_position(int(self.team_b.get_location_by_agent(agent)))
            plt.text(x_pos, y_pos, agent, size=8,
                ha="center", va="center",
                bbox=dict(boxstyle="circle", color="purple")
                )

        for goal in self.goals.get_agents_list():
            x_pos, y_pos = self.location_to_grid_position(int(self.goals.get_location_by_agent(goal)))
            plt.text(x_pos, y_pos, goal, size=8,
                ha="center", va="center",
                bbox=dict(boxstyle="circle", color="orange")
                )

        plt.show()

        