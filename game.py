from env_generator import Environment

# This class is used to define and run a game between two Teams and theit planned strategy
class Game:
    def __init__(self, environment, team_a_strategy, team_b_strategy):
        self.team_a = environment.team_a
        self.team_b = environment.team_b
        self.goals = environment.goals
        self.graph = environment.graph
        self.team_a_strategy = team_a_strategy
        self.team_b_strategy = team_b_strategy
        self.captured_agents = set()
        self.lost_goals = set()
        self.coverage_percentage = 0

    
    # This function runs the game and prints the results
    def run(self):
        while not self.check_finish():
            self.move_team(self.team_a, self.team_a_strategy)
            self.move_team(self.team_b, self.team_b_strategy)
            self.check_collisions()
            self.finalize_round()

        self.print_results()    


    # This function checks if both of the Teams has finished executing their strategies
    def check_finish(self):
        for vertex in self.team_a_strategy:
            if self.team_a_strategy[vertex] != []:
                return False
        
        for vertex in self.team_b_strategy:
            if self.team_b_strategy[vertex] != []:
                return False

        return True


    # This function move a team one step according to the strategy, then update the strategy accordingly
    def move_team(self, team, strategy):
        for agent in team.get_agents_list():
            if strategy[agent] != []:
                team.set_location(agent, strategy[agent][0])
                del strategy[agent][0]


    # This function is used to detect collisions between the two teams locations, and update the captured_agents set
    def check_collisions(self):
        for b_agent in self.team_b.get_agents_list():
            b_agent_location = self.team_b.get_location_by_agent(b_agent)
            for a_agent in self.team_a.get_agents_list():
                a_agent_location = self.team_a.get_location_by_agent(a_agent)
                # Checking vertex collisions
                if a_agent_location == b_agent_location and b_agent_location not in self.lost_goals:
                    self.captured_agents.add(b_agent)

                # No edge collision check in last position
                if self.team_b_strategy[b_agent] == [] or self.team_a_strategy[a_agent] == []:
                    continue

                # Checking edge collisions
                if a_agent_location == self.team_b_strategy[b_agent][0] and b_agent_location == self.team_a_strategy[a_agent][0]:
                    self.captured_agents.add(b_agent)


    # This function updates the lost-goals set after each round and prints it to the consolse
    def finalize_round(self):
        for agent in self.team_b.get_agents_list():
            cur_agent_location = self.team_b.get_location_by_agent(agent)
            if cur_agent_location in self.goals.get_locations_list() and agent not in self.captured_agents:
                self.lost_goals.add(cur_agent_location)

        print('Captures Agents: {0}'.format(self.captured_agents))
        print('Lost Goals: {0}'.format(self.lost_goals))
        

    # This function calcs & prints the game results to the console
    def print_results(self):
        self.coverage_percentage = 100 * (1 - len(self.lost_goals) / len(self.goals.get_agents_list()))
        print('Coverage Percentage: {0}%'.format(self.coverage_percentage))
