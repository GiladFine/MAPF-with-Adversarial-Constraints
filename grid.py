from colorama import Style, Fore

class Grid:
    def __init__(self, grid):
        self.grid = grid


    def print(self):
        for row in self.grid:
            print_row = ' '.join([f'{Fore.GREEN}O{Style.RESET_ALL}' if item == True else f'{Fore.RED}X{Style.RESET_ALL}' for item in row])
            print(print_row)


    def convert_to_graph(self):
        edges = []
        i_size = len(self.grid)
        for i in range(i_size):
            row = self.grid[i]
            j_size = len(row)
            for j in range(j_size):
                if j + 1 < j_size and row[j] == row[j + 1] == True:
                    edges.append([i * i_size + j + 1, i * i_size + j + 2])
                if i + 1 < i_size and row[j] == self.grid[i + 1][j] == True:
                    edges.append([i * i_size + j + 1, (i + 1) * i_size + j + 1])
        return edges
    
