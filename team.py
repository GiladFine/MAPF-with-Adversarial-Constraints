import json

# This class represents a Team of agents and their location
class Team:
    def __init__(self, agents):
        self.agents = agents


    # This function returns a list of the Team's locations
    def get_locations_list(self):
        return list(self.agents.values())


    # This function returns a list of the Team's agents names
    def get_agents_list(self):
        return list(self.agents.keys())


    # This funcion find the agent in a given location
    def get_agent_by_location(self, location):
        return self.get_agents_list()[self.get_locations_list().index(location)]


    # This function find the location of a given agent
    def get_location_by_agent(self, agent):
        return self.agents[agent]


    # This function sets the location of a an agent
    def set_location(self, agent, location):
        self.agents[agent] = location


    # This function prints to the console the Team as a json
    def print(self):
        print(json.dumps(self.agents, indent=1))   