OBSTACLE_FREQUENCY = 0.3
GRID_SIZE = 8
TEAMS_SIZE = 10

# Grid - size * size boolean array - grid[i] == False only if grid[i] is a part of an obstacle, else True
EXAMPLE_GRID = [[True, True, True, True, True, True, True, True],
                [True, True, False, False, True, True, True, True],
                [False, True, False, False, True, True, True, True], 
                [False, False, True, True, True, True, True, True], 
                [False, True, True, True, True, True, True, True], 
                [True, True, False, True, False, False, True, True], 
                [True, True, False, True, True, True, True, True], 
                [True, True, True, True, True, True, True, True]]


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


# Strategy - a dictionary mapping each agent to a path, represented by a list of vertices
EXAMPLE_TEAM_STRATEGY = {
    'a1' : ['v1', 'v1', 'v2'],
    'a2' : ['v3', 'v2', 'v6'],
    'a3' : ['v5', 'v4', 'v4']
}