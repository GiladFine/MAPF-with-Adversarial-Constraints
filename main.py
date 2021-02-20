from env_generator import Environment

def main():
    environment = Environment()
    environment.grid.print()
    print("-------------------------------------------")
    environment.graph.print()
    print("-------------------------------------------")
    environment.team_a.print()
    print("-------------------------------------------")
    environment.team_b.print()
    print("-------------------------------------------")
    environment.goals.print()
    #environment.graph.visualize()


if __name__ == "__main__":
    main()