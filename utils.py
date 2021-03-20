OBSTACLE_FREQUENCY = 0.35
GRID_SIZE = 8
TEAMS_SIZE = 4

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
EXAMPLE_GRAPH = [['v1', 'v2'], ['v3', 'v4'], ['v2', 'v6'], ['v3', 'v7'], ['v4', 'v8'],
                 ['v5', 'v6'], ['v6', 'v7'], ['v5', 'v9'], ['v7', 'v10'], ['v8', 'v11'],
                 ['v9', 'v10'], ['v11', 'v12'], ['v10', 'v14'], ['v12', 'v14'], ['v12', 'v20'],
                 ['v13', 'v14'], ['v14', 'v15'], ['v15', 'v16'], ['v14', 'v17'], ['v14', 'v19'],
                 ['v16', 'v19'], ['v18', 'v19']]


# Team - a dictionary mapping each agent to its location in the graph
EXAMPLE_TEAM_A = {
    'a1' : 'v10',
    'a2' : 'v4', 
    'a3' : 'v9'
}

EXAMPLE_TEAM_B = {
    'b1' : 'v11',
    'b2' : 'v16',
    'b3' : 'v1'
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

# Goals - a list of nodes representing B team's goals
EXAMPLE_GOALS = {'v7', 'v20', 'v17'}

# Simple Network Test
NETWORK_TEST_GRAPH = [['1', '5'], ['2', '5'], ['3', '6'], 
                      ['4', '6'], ['5', '7'], ['5', '8'],
                      ['6', '8'], ['6', '9'], ['8', '9'],
                      ['7', '10'], ['9', '13'], ['8', '10'],
                      ['8', '11'], ['8', '12'], ['8', '13']]

NETWORK_TEST_TEAM = {
    'a1' : '1',
    'a2' : '2',
    'a3' : '3',
    'a4' : '4'
}
NETWORK_TEST_GOALS = {
    'g1' : '10',
    'g2' : '11', 
    'g3' : '12',
    'g4' : '13'
}
