from colorama import Style, Fore
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.animation import FuncAnimation
import numpy as np

# This class represents a world grid with obstacles
class Grid:
    def __init__(self, grid):
        self.grid = grid
        self.row_size = len(self.grid)
        self.col_size = len(self.grid[0])


    # This function prints the grid to the console
    def to_string(self, a_team_locations, b_team_locations, goals_locations):
        result = ''
        for i, row in enumerate(self.grid):
            print_row = ''
            for j, item in enumerate(row):
                location_str = str(i * 8 + j + 1)
                if location_str in a_team_locations:
                    print_item = f'{Fore.YELLOW}{a_team_locations.index(location_str) + 1}{Style.RESET_ALL} '
                elif location_str in b_team_locations:
                    print_item = f'{Fore.BLUE}{b_team_locations.index(location_str) + 1}{Style.RESET_ALL} '
                elif location_str in goals_locations:
                    print_item = f'{Fore.MAGENTA}{goals_locations.index(location_str) + 1}{Style.RESET_ALL} '
                else:
                    print_item = f'{Fore.GREEN}O{Style.RESET_ALL} ' if item == 1 else f'{Fore.RED}X{Style.RESET_ALL} '
                    
                print_row += print_item
            result += print_row + '\n'
        return result


    # This function converts the grid to a graph (edges representation)
    def convert_to_graph(self):
        edges = []
        i_size = len(self.grid)
        for i in range(i_size):
            row = self.grid[i]
            j_size = len(row)
            for j in range(j_size):
                if j + 1 < j_size and row[j] == row[j + 1] == 1:
                    edges.append([str(i * i_size + j + 1), str(i * i_size + j + 2)])
                if i + 1 < i_size and row[j] == self.grid[i + 1][j] == 1:
                    edges.append([str(i * i_size + j + 1), str((i + 1) * i_size + j + 1)])
        return edges


    def visualize(self):
        cmap = colors.ListedColormap(['red','green'])
        plt.pcolor(self.grid[::-1], cmap=cmap, edgecolors='k', linewidths=1)
        plt.show()
    
