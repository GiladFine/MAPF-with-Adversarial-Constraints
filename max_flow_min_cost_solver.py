from typing import Any, Dict, Tuple
from collections import defaultdict
import numpy as np

from networkx import DiGraph
from ortools.graph.python import min_cost_flow, max_flow


class MaxFlowMinCostSolver:
    def __init__(self, network: DiGraph) -> None:
        self.number_of_nodes = 0
        self.nodes_names = []
        self.nodes_names_to_numbers = {}
        self.src_nodes = []
        self.dst_nodes = []
        self.capacities = []
        self.unit_costs = []
        network_edges = network.edges(data=True)
        for src_name, dst_name, data_dict in network_edges:
            src_number = self._node_name_to_number(node_name=src_name)
            dst_number = self._node_name_to_number(node_name=dst_name)
            self.src_nodes.append(src_number)
            self.dst_nodes.append(dst_number)
            self.capacities.append(
                int(data_dict.get("capacity", 0))
            )
            self.unit_costs.append(
                int(data_dict.get("weight", 0))
            )

    def _node_name_to_number(self, node_name: str) -> int:
        if node_name in self.nodes_names_to_numbers:
            return self.nodes_names_to_numbers[node_name]
        
        self.nodes_names_to_numbers[node_name] = self.number_of_nodes
        self.nodes_names.append(node_name)
        self.number_of_nodes += 1
        return self.nodes_names_to_numbers[node_name]

    def calc_max_flow(self):
        smf = max_flow.SimpleMaxFlow()
        all_arcs = smf.add_arcs_with_capacity(
            self.src_nodes,
            self.dst_nodes,
            self.capacities,
        )

        status = smf.solve(
            self._node_name_to_number("src"),
            self._node_name_to_number("dst"),
        )
        return smf.optimal_flow()

    def max_flow_min_cost(self) -> Tuple[Dict[str, Dict[str, int]], int, int]:
        smcf = min_cost_flow.SimpleMinCostFlow()
        
        max_flow_value = self.calc_max_flow()
        
        supplies = [0] * self.number_of_nodes
        supplies[self._node_name_to_number("src")] = max_flow_value
        supplies[self._node_name_to_number("dst")] = -max_flow_value

        # Add arcs, capacities and costs in bulk using numpy.
        all_arcs = smcf.add_arcs_with_capacity_and_unit_cost(
            self.src_nodes,
            self.dst_nodes,
            self.capacities,
            self.unit_costs,
        )

        # Add supply for each nodes.
        smcf.set_nodes_supply(np.arange(0, len(supplies)), supplies)

        # Find the min cost flow.
        status = smcf.solve()

        if status != smcf.OPTIMAL:
            raise ValueError(f"There was an issue with the min cost flow input - status = {status}")

        flow_cost = smcf.optimal_cost()
        solution_flows = smcf.flows(all_arcs)
        flow_dict = self._create_flow_dict(
            smcf=smcf,
            all_arcs=all_arcs,
            solution_flows=solution_flows,
        )
        return flow_dict, max_flow_value, flow_cost


    def _create_flow_dict(self, smcf: Any, all_arcs, solution_flows):
        flow_dict = defaultdict(dict)
        
        for arc, flow in zip(all_arcs, solution_flows):
            source_node = self.nodes_names[smcf.tail(arc)]
            dest_node = self.nodes_names[smcf.head(arc)]
            flow_dict[source_node][dest_node] = flow
        
        flow_dict = dict(flow_dict)
        return flow_dict
