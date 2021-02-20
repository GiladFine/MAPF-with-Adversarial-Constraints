import json

class Team:
    def __init__(self, agents):
        self.agents = agents


    def get_locations_list(self):
        locations_list = [self.agents[agent] for agent in self.agents]
        return locations_list


    def print(self):
        print(json.dumps(self.agents, indent=1))   