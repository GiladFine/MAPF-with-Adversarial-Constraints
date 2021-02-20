from random import choices, randint
from grid import Grid
from graph import Graph

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
EXAMPLE_GRAPH = [[1, 2], [2, 3], [3, 4], [4, 5], [1, 3], [2, 6], [4, 6], [3, 5]]


def randomGrid(size):
    grid = [[True for i in range(size)] for j in range(size)]
    num_of_obastacle = 0
    while (num_of_obastacle / (size * size)) < OBSTACLE_FREQUENCY:
        row_location, col_location = randint(0, size - 1), randint(0, size - 1)
        if grid[row_location][col_location]:
            num_of_obastacle += 1
            grid[row_location][col_location] = False
    return grid


def random_graph(v_size, e_size):
    vertices = range(1, v_size + 1)
    edges = []
    num_of_edges = 0
    while num_of_edges < e_size:
        v1, v2 = randint(1, v_size + 1), randint(1, v_size + 1)
        if v1 == v2:
            continue
        if [v1, v2] not in edges and [v2, v1] not in edges:
            num_of_edges += 1
            edges.append([v1, v2])
    
    return edges


def main():
    grid = Grid(randomGrid(10))
    grid.print()

    print("-------------------------------------------")

    graph = Graph(grid.convert_to_graph())
    graph.print()
    graph.visualize()


if __name__ == "__main__":
    main()