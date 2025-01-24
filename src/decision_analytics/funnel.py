import itertools
import pandas as pd
from decision_analytics import NodesCollection
import logging


class Funnel:
    def __init__(self, nodes_collection: NodesCollection):
        self.nodes_collection = nodes_collection

    def simulate(self):
        # Given the nodes collection, simulate all the variation of the funnel by looping through all the nodes, and all the value percentiles of each node, and calculate the final outcome for each combination.

        # Make sure that the nodes_collection has at least 1 calculated node tagged is_kpi=True
        if not any(node.is_kpi for node in self.nodes_collection):
            raise ValueError("No KPI node found in the funnel.")

        inputs = [i.name for i in self.nodes_collection.get_input_nodes()]
        possible_values = [0, 1, 2]
        kpis = [i.name for i in self.nodes_collection.get_kpi_nodes()]

        all_combinations = itertools.product(possible_values, repeat=len(inputs))

        results = []
        for combo in all_combinations:
            combo_dict = dict(zip(inputs, combo))
            self.nodes_collection.set_node_values_from_dict(combo_dict)
            logging.INFO(combo_dict)
            logging.INFO(self.nodes_collection.get_input_nodes())
            self.nodes_collection.refresh_nodes()
            kpi_values = [node.value for node in self.nodes_collection.get_kpi_nodes()]
            results.append(
                {
                    **combo_dict,
                    **{k: v for k, v in zip(kpis, kpi_values)},
                }
            )
        results_df = pd.DataFrame(results)
        return results_df
