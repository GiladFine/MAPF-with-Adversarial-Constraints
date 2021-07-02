import numpy as np
from matplotlib import pyplot as plt, text
from matplotlib import animation
from matplotlib import colors
from numpy.core.fromnumeric import size


class Animation:
    def __init__(self, environment, a_team_strategy, b_team_strategy, lost_goals):
        self.environment = environment
        self.strategy_a = a_team_strategy
        self.strategy_b = b_team_strategy
        self.lost_goals = lost_goals
        self.max_timestep = max([len(item) - 1 for item in self.strategy_a.values()] + [len(item) - 1 for item in self.strategy_b.values()])
        self.frames = 25
        self.interval = 1
        self.speed = 1 / self.frames
        self.cmap = colors.ListedColormap(['red','green'])
        self.fig = plt.figure()
        self.ax = plt.axes(xlim=(0, self.environment.grid_size), ylim=(0, self.environment.grid_size))
        plt.pcolor(self.environment.grid.grid[::-1], cmap=self.cmap, edgecolors='k', linewidths=1)
        self.calc_title()
        self.reset_animation()
        self.animation = animation.FuncAnimation(self.fig, self.anim_func, init_func=self.init_background,
                               frames=self.frames, interval=self.interval, blit=True)

    def init_background(self):
        return self.anim_func(0)

    def calc_title(self):
        title = "Goals: "
        goals_to_agents = {}
        for agent in self.strategy_a.keys():
            goals_to_agents[self.strategy_a[agent][-1]] = [agent]
        for agent in self.strategy_b.keys():
            goals_to_agents[self.strategy_b[agent][-1]].append(agent)

        for goal in self.environment.goals.agents:
            goal_location = self.environment.goals.get_location_by_agent(goal)
            winner = "(B)" if goal_location in self.lost_goals else "(A)"
            title += goal + " - " + ", ".join(goals_to_agents[goal_location]) + winner + " | "
        self.ax.set_title(title)


    def direction_to_speed(self, direction):
        if direction == "up":
            return 0, self.speed
        if direction == "down":
            return 0, -self.speed
        if direction == "right":
            return self.speed, 0
        if direction == "left":
            return -self.speed, 0
        
        return (0, 0)


    def vertex_to_location(self, vertex):
        square_num = int(vertex) - 1
        y_pos = self.environment.grid_size - np.floor(square_num / self.environment.grid_size) - 0.5
        x_pos = square_num % self.environment.grid_size + 0.5
        return (x_pos, y_pos)
    

    def reset_animation(self):
        self.agents_positions_a = {}
        self.agents_positions_b = {}
        self.directions_a = {}
        self.directions_b = {}
        self.speeds_a = {}
        self.speeds_b = {}
        self.curr_timestep = 0

        for agent in self.strategy_a.keys():
            self.agents_positions_a[agent] = self.vertex_to_location(self.strategy_a[agent][0])
            self.directions_a[agent] = []
            self.speeds_a[agent] = []
            for i, item in enumerate(self.strategy_a[agent]):
                if i >= len(self.strategy_a[agent]) - 1:
                    break
                next_item = self.strategy_a[agent][i + 1]
                curr_x, curr_y = self.vertex_to_location(item)
                next_x, next_y = self.vertex_to_location(next_item)
                x_diff = next_x - curr_x
                y_diff = next_y - curr_y
                if x_diff == 1:
                    direction = "right"
                elif x_diff == -1:
                    direction = "left"      
                elif y_diff == 1:
                    direction = "up"
                elif y_diff == -1:
                    direction = "down"
                else:
                    direction = "stay"
                self.directions_a[agent].append(direction)
                self.speeds_a[agent].append(self.direction_to_speed(direction))
        
        for agent in self.strategy_b.keys():
            self.agents_positions_b[agent] = self.vertex_to_location(self.strategy_b[agent][0])
            self.directions_b[agent] = []
            self.speeds_b[agent] = []
            for i, item in enumerate(self.strategy_b[agent]):
                if i >= len(self.strategy_b[agent]) - 1:
                    break
                next_item = self.strategy_b[agent][i + 1]
                curr_x, curr_y = self.vertex_to_location(item)
                next_x, next_y = self.vertex_to_location(next_item)
                x_diff = next_x - curr_x
                y_diff = next_y - curr_y
                if x_diff == 1:
                    direction = "right"
                elif x_diff == -1:
                    direction = "left"      
                elif y_diff == 1:
                    direction = "up"
                elif y_diff == -1:
                    direction = "down"
                else:
                    direction = "stay"
                self.directions_b[agent].append(direction)
                self.speeds_b[agent].append(self.direction_to_speed(direction))

            
    def prepare_next_move(self):
        for agent in self.agents_positions_a:
            direction = self.directions_a[agent][self.curr_timestep] if self.curr_timestep < len(self.directions_a[agent]) else "stay"
            self.agents_positions_a[agent] = tuple(np.add(self.agents_positions_a[agent], np.multiply(self.direction_to_speed(direction), self.frames)))
            
        for agent in self.agents_positions_b:
            direction = self.directions_b[agent][self.curr_timestep] if self.curr_timestep < len(self.directions_b[agent]) else "stay"
            self.agents_positions_b[agent] = tuple(np.add(self.agents_positions_b[agent], np.multiply(self.direction_to_speed(direction), self.frames)))

        self.curr_timestep += 1


    def anim_func(self, i):
        ret_agents = []
        for goal in self.environment.goals.agents:
            x_pos, y_pos = self.environment.location_to_grid_position(int(self.environment.goals.get_location_by_agent(goal)))
            ret_agents.append(plt.text(x_pos, y_pos, goal, size=10,
                ha="center", va="center",
                bbox=dict(boxstyle="circle", color="orange")
                ))


        for agent in self.strategy_a.keys():
            curr_pos = self.agents_positions_a[agent]
            if self.curr_timestep >= len(self.speeds_a[agent]):
                curr_speed = (0, 0)
            else:
                curr_speed = self.speeds_a[agent][self.curr_timestep]
            ret_agents.append(plt.text(curr_pos[0] + curr_speed[0] * i, curr_pos[1] + curr_speed[1] * i, agent, size=10,
                ha="center", va="center",
                bbox=dict(boxstyle="circle", color="blue")
                ))

        for agent in self.strategy_b.keys():
            curr_pos = self.agents_positions_b[agent]
            if self.curr_timestep >= len(self.speeds_b[agent]):
                curr_speed = (0, 0)
            else:
                curr_speed = self.speeds_b[agent][self.curr_timestep]
            ret_agents.append(plt.text(curr_pos[0] + curr_speed[0] * i, curr_pos[1] + curr_speed[1] * i, agent, size=10,
                ha="center", va="center",
                bbox=dict(boxstyle="circle", color="purple")
                ))

        if i == self.frames - 1:
            if self.curr_timestep >= self.max_timestep:
                self.reset_animation()
            else:
                self.prepare_next_move()
        
        return ret_agents
        


    def plot(self):
        plt.show()

    
    def save(self):
        pass