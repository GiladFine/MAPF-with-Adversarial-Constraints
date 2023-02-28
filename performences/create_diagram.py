import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np
import json
import glob
import os

NUMBER_OF_RUNS = 50
MAP_NAME = "room-32.map"
RESULTS_FOLDER = "results/old_runs/4/room_32/"
FILE_PATTERN = "*_performence_results.json"
RESULT_FILE_NAME = "performence_results.json"
RESULT_FILE_PATH = os.path.join(RESULTS_FOLDER, RESULT_FILE_NAME)


DOT_RESULTS = [
    [83.4, 91.3, 96, 96.5, 97.4],
    [83.3, 89.8, 93, 95.5, 94.2],
    [85.8, 93.6, 96.2, 97.3, 97.7],
]



def merge_dicts():
    abs_directory_path = os.path.abspath(RESULTS_FOLDER)

    results_dict = {}
    for filepath in glob.glob(os.path.join(abs_directory_path, FILE_PATTERN)):
        with open(filepath, 'r') as file_name:
            new_results_dict = json.load(file_name)
        if results_dict == {}:
            results_dict = new_results_dict
            continue
        for map_name, subdict_1 in new_results_dict.items():
            for network_mode, subdict_2 in subdict_1.items():
                for number_of_goals, subdict_3 in subdict_2.items():
                    for field_name, value in subdict_3.items():
                        results_dict[map_name][network_mode][number_of_goals][field_name] += value
    
    if results_dict == {}:
        return
    with open(RESULT_FILE_PATH, 'w') as results_file:
        results_file.write(json.dumps(results_dict, indent=4))


def read_results():
    merge_dicts()
    with open(RESULT_FILE_PATH) as res_file:
        results = json.load(res_file)
        return results


def plot_sat_graph(mode):
    result = read_results()
    
    labels = set()
    variations = []
    arrays_dict = defaultdict(list)
    for variation, data in result[MAP_NAME].items():
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
                ) if data_of_agents_amount["number_of_sat_solutions"] > 0 else 0
            elif mode == "solver-SAT-times":
                value = round(
                    data_of_agents_amount["overall_sat_time_solver"]
                    / data_of_agents_amount["number_of_sat_solutions"],
                    1
                ) if data_of_agents_amount["number_of_sat_solutions"] > 0 else 0
            elif mode == "non-SAT-times":
                number_of_non_sat_solutions = (       
                    NUMBER_OF_RUNS
                    - data_of_agents_amount["number_of_sat_solutions"]
                )
                value = round(
                    data_of_agents_amount["overall_non_sat_time"]
                    / number_of_non_sat_solutions,
                    1
                ) if number_of_non_sat_solutions > 0 else 0
            elif mode == "solver-non-SAT-times":
                number_of_non_sat_solutions = (       
                    NUMBER_OF_RUNS
                    - data_of_agents_amount["number_of_sat_solutions"]
                )
                value = round(
                    data_of_agents_amount["overall_non_sat_time_solver"]
                    / number_of_non_sat_solutions,
                    1
                ) if number_of_non_sat_solutions else 0
            elif mode == "overall-times":
                value = round(
                    (
                        data_of_agents_amount["overall_non_sat_time"]
                        + data_of_agents_amount["overall_sat_time"]
                    )
                    / NUMBER_OF_RUNS,
                    1
                )
            elif mode == "avg_paths_length":
                value = round(
                    (
                        data_of_agents_amount["overall_paths_sizes_generally_sat"]
                        / (
                            int(num_of_agents) * result[MAP_NAME]["stays"][num_of_agents]["number_of_sat_solutions"]
                        )
                    ),
                    1
                ) if result[MAP_NAME]["stays"][num_of_agents]["number_of_sat_solutions"] > 0 else 0
            elif mode == "coverage_percentage_DOT":
                if variation != "disappearing":
                    continue
                number_of_non_sat_solutions = (       
                    NUMBER_OF_RUNS
                    - data_of_agents_amount["number_of_sat_solutions"]
                )
                value = round(
                    100 * (int(data_of_agents_amount["overall_flow_values"]) - data_of_agents_amount["number_of_sat_solutions"] * int(num_of_agents))
                    / (int(num_of_agents) * number_of_non_sat_solutions),
                    1
                )
            else:
                raise ValueError("BAD MODE")
            arrays_dict[variation].append(value)

    labels = sorted(list(labels))
    x = np.arange(len(labels))  # the label locations
    pad_width = 0.22
    width = pad_width - 0.005  # the width of the bars

    fig, ax = plt.subplots()
    if mode == "coverage_percentage_DOT":
        rects1 = ax.bar(x - 1 * pad_width, DOT_RESULTS[0], width, label='Room-32', hatch='///')
        rects2 = ax.bar(x, DOT_RESULTS[1], width, label='Maze-32', hatch='.O')
        rects3 = ax.bar(x + 1 * pad_width, DOT_RESULTS[2], width, label='Warehouse', hatch='..')

    else:
        rects1 = ax.bar(x - 1.5 * pad_width, arrays_dict[variations[0]], width, label='SOT', hatch='///')
        rects2 = ax.bar(x - 0.5 * pad_width, arrays_dict[variations[1]], width, label='HOT-2', hatch='.O')
        rects3 = ax.bar(x + 0.5 * pad_width, arrays_dict[variations[2]], width, label='DOT', hatch='..')
        rects4 = ax.bar(x + 1.5 * pad_width, arrays_dict[variations[3]], width, label='HOT-0', hatch='.|.|.')


    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_xlabel('number of agents')
    if mode == "percent-of-SAT":
        ax.set_ylabel('% of SAT instances')
        plt.ylim(0, 110)
    elif mode == "SAT-times":
        ax.set_ylabel('Average time per SAT instance (seconds)')
        ylim = 80 if MAP_NAME == "room-32.map" else 140
        plt.ylim(0, ylim)
    elif mode == "solver-SAT-times":
        ax.set_ylabel('Average solver time per SAT instance (seconds)')
        ylim = 12 if MAP_NAME == "room-32.map" else 35
        plt.ylim(0, ylim)
    elif mode == "non-SAT-times":
        ax.set_ylabel('Average time per non-SAT instance (seconds)')
        ylim = 70 if MAP_NAME == "room-32.map" else 140
        plt.ylim(0, ylim)
    elif mode == "solver-non-SAT-times":
        ax.set_ylabel('Average solver time per non-SAT instance (seconds)')
        ylim = 12 if MAP_NAME == "room-32.map" else 35
        plt.ylim(0, ylim)
    elif mode == "overall-times":
        ax.set_ylabel('Average time per instance (seconds)')
        ylim = 100 if MAP_NAME == "room-32.map" else 180
        plt.ylim(0, ylim)
    elif mode == "avg_paths_length":
        ax.set_ylabel('Average path length for SAT instances')
        ylim = 60 if MAP_NAME == "maze-32.map" else 25
        plt.ylim(0, ylim)
    elif mode == "coverage_percentage_DOT":
        ax.set_ylabel('% Coverage of DOT for non-SAT instances')
        plt.ylim(0, 130)
    else:
        raise ValueError("BAD MODE")
    

    ax.set_xticks(x, labels)
    ax.legend()

    ax.bar_label(rects1, padding=3, fontsize=8)
    ax.bar_label(rects2, padding=3, fontsize=8)
    ax.bar_label(rects3, padding=3, fontsize=8)

    if mode != "coverage_percentage_DOT":
        ax.bar_label(rects4, padding=3, fontsize=8)


    fig.tight_layout()
    # plt.show()
    plt.savefig(f"{RESULTS_FOLDER}/graphs/coverage_percentage_DOT_combined.png")
           


if __name__ == "__main__":
    # plot_sat_graph("percent-of-SAT")
    # plot_sat_graph("overall-times")
    # plot_sat_graph("avg_paths_length")
    plot_sat_graph("coverage_percentage_DOT")
    
    
    
    # plot_sat_graph("SAT-times")
    # plot_sat_graph("non-SAT-times")
    # plot_sat_graph("solver-SAT-times")
    # plot_sat_graph("solver-non-SAT-times")
