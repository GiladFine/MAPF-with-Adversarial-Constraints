import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np
import json

NUMBER_OF_RUNS = 100

def read_results():
    with open("performence_results.json") as res_file:
        results = json.load(res_file)
        return results


def plot_sat_graph(mode):
    result = read_results()
    
    labels = set()
    variations = []
    arrays_dict = defaultdict(list)
    for variation, data in result["room-32.map"].items():
        variations.append(variation)
        for num_of_agents, data_of_agents_amount in data.items():
            labels.add(int(num_of_agents))
            if mode == "percent-of-SAT":
                value = (
                    data_of_agents_amount["number_of_sat_solutions"]
                    / NUMBER_OF_RUNS
                ) * 100
            elif mode == "SAT-times":
                value = round(
                    data_of_agents_amount["overall_sat_time"]
                    / data_of_agents_amount["number_of_sat_solutions"],
                    1
                )
            elif mode == "non-SAT-times":
                value = round(
                    data_of_agents_amount["overall_non_sat_time"]
                    / (
                        NUMBER_OF_RUNS
                        - data_of_agents_amount["number_of_sat_solutions"]
                    ),
                    1
                )
            else:
                raise ValueError("BAD MODE")
            arrays_dict[variation].append(value)

    labels = sorted(list(labels))
    x = np.arange(len(labels))  # the label locations
    width = 0.3  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width, arrays_dict[variations[0]], width, label=variations[0])
    rects2 = ax.bar(x, arrays_dict[variations[1]], width, label=variations[1])
    rects3 = ax.bar(x + width, arrays_dict[variations[2]], width, label=variations[2])


    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_xlabel('number of agents')
    if mode == "percent-of-SAT":
        ax.set_ylabel('% of SAT instances')
        ax.set_title('% of SAT instances for each problem type')
        plt.ylim(0, 130)
    elif mode == "SAT-times":
        ax.set_ylabel('Avarage time per SAT instance (seconds)')
        ax.set_title('Avarage time of SAT instance for each problem type')
        plt.ylim(0, 70)
    elif mode == "non-SAT-times":
        ax.set_ylabel('Avarage time per non-SAT instance (seconds)')
        ax.set_title('Avarage time of non-SAT instance for each problem type')
        plt.ylim(0, 70)
    else:
        raise ValueError("BAD MODE")
    

    ax.set_xticks(x, labels)
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)
    ax.bar_label(rects3, padding=3)


    fig.tight_layout()
    plt.show()
    # plt.savefig(mode + ".png")
           


if __name__ == "__main__":
    plot_sat_graph("percent-of-SAT")
    plot_sat_graph("SAT-times")
    plot_sat_graph("non-SAT-times")
