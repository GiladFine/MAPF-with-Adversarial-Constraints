from enum import Enum


# Miscs
OBSTACLE_FREQUENCY = 0.25
GRID_SIZE = 8
TEAMS_SIZE = 4


# Possible objectives for the minimizer
OBJECTIVE_TYPES = ["MAKESPAN", "TOTAL_DISTANCE", "CONSTRAINTS"]


# Possible strategies
STRATEGY_TYPES = ["MUNKRES", "NETWORK_MAKSPAN", "NETWORK_TOTAL_DISTANCE"]


# Grid - size * size boolean array - grid[i] == 0 only if grid[i] is a part of an obstacle, else 1
EXAMPLE_GRID = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 0, 0, 1, 1, 1, 1],
                [0, 1, 0, 0, 1, 1, 1, 1], 
                [0, 0, 1, 1, 1, 1, 1, 1], 
                [0, 1, 1, 1, 1, 1, 1, 1], 
                [1, 1, 0, 1, 0, 0, 1, 1], 
                [1, 1, 0, 1, 1, 1, 1, 1], 
                [1, 1, 1, 1, 1, 1, 1, 1]]


SIMPLE_GRID = [[1, 0, 1, 1],
               [1, 1, 1, 0],
               [1, 1, 0, 1],
               [1, 0, 1, 1],]


# Graph - a list of edges, each edge is a list of 2 vertices
EXAMPLE_GRAPH = [['v1', 'v2'], ['v3', 'v4'], ['v2', 'v6'], ['v3', 'v7'], ['v4', 'v8'],
                 ['v5', 'v6'], ['v6', 'v7'], ['v5', 'v9'], ['v7', 'v10'], ['v8', 'v11'],
                 ['v9', 'v10'], ['v11', 'v12'], ['v10', 'v14'], ['v12', 'v14'], ['v12', 'v20'],
                 ['v13', 'v14'], ['v14', 'v15'], ['v15', 'v16'], ['v14', 'v17'], ['v14', 'v19'],
                 ['v16', 'v19'], ['v18', 'v19']]


# Team - a dictionary mapping each agent to its location in the graph
# EXAMPLE_TEAM_A = {
#     'a1' : '26',
#     'a2' : '27',
#     'a3' : '45'
# }

# EXAMPLE_TEAM_B = {
#     'b1' : '63',
#     'b2' : '6',
#     'b3' : '2'
# }

# EXAMPLE_GOALS = {
#     'g1' : '31',
#     'g2' : '32',
#     'g3' : '21'
# }
EXAMPLE_TEAM_A = {
    "a1": "23",
    "a2": "59",
    "a3": "3",
    "a4": "51"
}

EXAMPLE_TEAM_B = {
    "b1": "33",
    "b2": "30",
    "b3": "34",
    "b4": "63"
}

EXAMPLE_GOALS = {
    "g1": "35",
    "g2": "43",
    "g3": "9",
    "g4": "16"
}



# Strategy - a dictionary mapping each agent to a path, represented by a list of vertices
EXAMPLE_TEAM_A_STRATEGY = {
    'a1' : ['v10', 'v14', 'v17'],
    'a2' : ['v4', 'v8', 'v11', 'v12', 'v20'],
    'a3' : ['v9', 'v10', 'v7']
}

EXAMPLE_TEAM_B_STRATEGY = {
    'b1' : ['v11', 'v12', 'v20'],
    'b2' : ['v16', 'v15', 'v14', 'v17'],
    'b3' : ['v1', 'v2', 'v6', 'v7']
}

# Simple Network Test
NETWORK_TEST_GRAPH = [['1', '3'], ['2', '3'], ['3', '4']]

NETWORK_TEST_TEAM = {
    'a1' : '1',
    'a2' : '2'
}

NETWORK_TEST_GOALS = {
    'g1' : '3', 
    'g2' : '4'
}

# Reach Constraints Example - This means for example that an agent must be in location '3' by timestep 1,
# so the entire branch of '3' from timestep 1 and forward is trimmed from the time-expanded graph
EXAMPLE_REACH_CONSTRAINTS = {
    '3' : 1,
    '4' : 2
}


# Hole Constraints Example - This means that the location '2' in the original graph is not available in timestep 3
# and 7, but for example in timesteps 5, 9 it is free
EXAMPLE_HOLE_CONSTRAINTS = {
    '2': [3, 6],
    '5': [1, 3, 4]
}