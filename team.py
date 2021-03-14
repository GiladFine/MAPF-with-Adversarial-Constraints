import json

class Team:
    def __init__(self, agents):
        self.agents = agents
        self.paths = {}


    def get_locations_list(self):
        return list(self.agents.values())


    def get_agents_list(self):
        return list(self.agents.keys())


    def get_agent_by_location(self, location):
        return self.get_agents_list()[self.get_locations_list().index(location)]


    def get_location_by_agent(self, agent):
        return self.agents[agent]


    def set_location(self, agent, location):
        self.agents[agent] = location


    def print(self):
        print(json.dumps(self.agents, indent=1))   