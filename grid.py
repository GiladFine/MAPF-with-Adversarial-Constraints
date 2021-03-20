from colorama import Style, Fore

# This class represents a world grid with obstacles
class Grid:
    def __init__(self, grid):
        self.grid = grid


    # This function prints the grid to the console
    def print(self):
        for row in self.grid:
            print_row = ' '.join([f'{Fore.GREEN}O{Style.RESET_ALL}' if item == True else f'{Fore.RED}X{Style.RESET_ALL}' for item in row])
            print(print_row)


    # This function converts the grid to a graph (edges representation)
    def convert_to_graph(self):
        edges = []
        i_size = len(self.grid)
        for i in range(i_size):
            row = self.grid[i]
            j_size = len(row)
            for j in range(j_size):
                if j + 1 < j_size and row[j] == row[j + 1] == True:
                    edges.append([str(i * i_size + j + 1), str(i * i_size + j + 2)])
                if i + 1 < i_size and row[j] == self.grid[i + 1][j] == True:
                    edges.append([str(i * i_size + j + 1), str((i + 1) * i_size + j + 1)])
        return edges
    
