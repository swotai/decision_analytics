import itertools
import pandas as pd
from decision_analytics import NodesCollection
import logging


class Funnel:
    def __init__(self, nodes_collection: NodesCollection):
        self.nodes_collection = nodes_collection
        self.input_node_names = [
            i.name for i in self.nodes_collection.get_input_nodes()
        ]
        self.kpi_node_names = [i.name for i in self.nodes_collection.get_kpi_nodes()]
        self.sim_result = pd.DataFrame()

    def simulate(self) -> None:
        self.simulate_variances()
        self.update_calculations()

    def simulate_variances(self) -> pd.DataFrame:
        """
        Simulates all variations of the funnel by looping through all nodes and their value percentiles.
        Stores the results in self.sim_result.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If no KPI node is found in the funnel.
        """
        # Given the nodes collection, simulate all the variation of the funnel by looping through all the nodes, and all the value percentiles of each node, and calculate the final outcome for each combination.

        # Make sure that the nodes_collection has at least 1 calculated node tagged is_kpi=True
        if not any(node.is_kpi for node in self.nodes_collection):
            raise ValueError("No KPI node found in the funnel.")

        inputs = self.input_node_names
        possible_values = [0, 1, 2]
        kpis = self.kpi_node_names

        all_combinations = itertools.product(possible_values, repeat=len(inputs))

        results = []
        for combo in all_combinations:
            combo_dict = dict(zip(inputs, combo))
            self.nodes_collection.set_node_values_from_dict(combo_dict)
            logging.debug(combo_dict)
            logging.debug(self.nodes_collection.get_input_nodes())
            self.nodes_collection.refresh_nodes()
            kpi_values = [node.value for node in self.nodes_collection.get_kpi_nodes()]
            results.append(
                {
                    **combo_dict,
                    **{k: v for k, v in zip(kpis, kpi_values)},
                }
            )
        results_df = pd.DataFrame(results)
        self.sim_result = results_df
        return results_df

    def update_calculations(self):
        df = self.sim_result
        kpi_cols = [f"{i}_{j}" for i in self.kpi_node_names for j in [0, 1, 2]]
        calculations_df = pd.DataFrame(index=self.input_node_names, columns=kpi_cols)
        for kpi in self.kpi_node_names:
            for input in self.input_node_names:
                for i in [0, 1, 2]:
                    other_cols = [x for x in self.input_node_names if x != input]
                    lookup = df[(df[input] == i) & ((df[other_cols] == 1).all(axis=1))]
                    calculations_df.loc[input, f"{kpi}_{i}"] = lookup[kpi].values[0]
        # Add swing (abs diff) and swing ^2
        # What happen if there's a reverse relationship, so that the low-mid-high would lead to high-mid-low of kpi? interesting. I think in that case we should specify that input as "reverse" so that it's positive.
        # e.g. churn, switch to survival.
        # Because value base, most of the time if we are building the value funnel everything should more be positive correlation than negative.
        self.calculations_result = calculations_df
        return calculations_df
