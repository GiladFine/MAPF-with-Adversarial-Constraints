from random import choices, randint
from grid import Grid
from graph import Graph
from team import Team

OBSTACLE_FREQUENCY = 0.3

# Grid - size * size boolean array - grid[i] == False only if grid[i] is a part of an obstacle, else True
EXAMPLE_GRID = [[True, True, True, True, True, True, True, True ],
                [True, True, False, False, True, True, True, True ],
                [False, True, False, False, True, True, True, True ], 
                [False, False, True, True, True, True, True, True ], 
                [False, True, True, True, True, True, True, True ], 
                [True, True, False, True, False, False, True, True ], 
                [True, True, False, True, True, True, True, True ], 
                [True, True, True, True, True, True, True, True ]]


SIMPLE_GRID = [[True, False, True, True],
               [True, True, True, False],
               [True, True, False, True],
               [True, False, True, True],]


# Graph - a list of edges, each edge is a list of 2 vertices
EXAMPLE_GRAPH = [['v1', 'v2'], ['v2', 'v3'], ['v3', 'v4'], ['v4', 'v5'], ['v1', 'v3'], ['v2', 'v6'], ['v4', 'v6'], ['v3', 'v5']]


# Team - a dictionary mapping each agent to its location in the graph
EXAMPLE_TEAM = {
    'a1' : 'v1',
    'a2' : 'v3',
    'a3' : 'v5'
}


# Generate random grid by randomly assign obastacles until their frequency is meating the parameter
def random_grid(size):
    grid = [[True for i in range(size)] for j in range(size)]
    num_of_obastacle = 0
    while (num_of_obastacle / (size * size)) < OBSTACLE_FREQUENCY:
        row_location, col_location = randint(0, size - 1), randint(0, size - 1)
        if grid[row_location][col_location]:
            num_of_obastacle += 1
            grid[row_location][col_location] = False
    return grid


# Generate random graph by randomly adding edges
def random_graph(v_size, e_size):
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
def random_team(letter, size, vertices_list):
    team = {}
    for i in range(1, size + 1):
        agent = letter + str(i)
        rand_vertex = vertices_list[randint(0, len(vertices_list) - 1)]
        vertices_list.remove(rand_vertex) # Remove from possible locations for future agents
        team[agent] = rand_vertex

    return team


def main():
    # Generate a grid of size X
    grid = Grid(random_grid(8))
    grid.print()

    print("-------------------------------------------")

    # Convert grid to graph
    graph = Graph(grid.convert_to_graph())
    graph.print()
    graph.visualize()

    print("-------------------------------------------")

    # Generate team A
    graph_available_vertices = graph.get_vertices_list()
    team_a = Team(random_team('a', 10, graph_available_vertices))

    # Remove all vertices occupied by team A
    graph_available_vertices = [vertex for vertex in graph_available_vertices if vertex not in team_a.get_locations_list()]
    
    # Generate team B
    team_b = Team(random_team('b', 10, graph_available_vertices))
    team_a.print()
    team_b.print()


if __name__ == "__main__":
    main()