import itertools
import numpy as np
import pandas as pd
from decision_analytics import NodesCollection
import logging
from decision_analytics.utils import values_map


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
        possible_values = values_map.keys()
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

        pr_mapping = {key: values["pr"] for key, values in values_map.items()}
        results_df["weights"] = results_df[inputs].apply(
            lambda row: row.map(pr_mapping).prod(), axis=1
        )

        label_mapping = {key: values["label"] for key, values in values_map.items()}
        results_df[inputs] = results_df[inputs].replace(label_mapping)
        self.sim_result = results_df
        return results_df

    def update_calculations(self):
        labels_list = [details["label"] for details in values_map.values()]
        df = self.sim_result
        kpi_cols = [f"{i}_{j}" for i in self.kpi_node_names for j in labels_list]
        calculations_df = pd.DataFrame(index=self.input_node_names, columns=kpi_cols)
        for kpi in self.kpi_node_names:
            for input in self.input_node_names:
                for i in labels_list:
                    other_cols = [x for x in self.input_node_names if x != input]
                    lookup = df[
                        (df[input] == i) & ((df[other_cols] == "mid").all(axis=1))
                    ]
                    calculations_df.loc[input, f"{kpi}_{i}"] = lookup[kpi].values[0]

        # calculate swings
        for kpi in self.kpi_node_names:
            # max - min for all columns with column name starts with kpi_
            kpi_cols = [x for x in calculations_df.columns if x.startswith(f"{kpi}_")]
            calculations_df[f"{kpi}_swing"] = calculations_df[kpi_cols].max(
                axis=1
            ) - calculations_df[kpi_cols].min(axis=1)
            # Add swing ^2
            calculations_df[f"{kpi}_swing_squared"] = calculations_df[
                f"{kpi}_swing"
            ].apply(lambda x: x**2)
            calculations_df.loc["Combined Uncertainty", f"{kpi}_low"] = np.quantile(
                df[kpi], 0.1, weights=df["weights"], method="inverted_cdf"
            )
            calculations_df.loc["Combined Uncertainty", f"{kpi}_mid"] = np.quantile(
                df[kpi], 0.5, weights=df["weights"], method="inverted_cdf"
            )
            calculations_df.loc["Combined Uncertainty", f"{kpi}_high"] = np.quantile(
                df[kpi], 0.9, weights=df["weights"], method="inverted_cdf"
            )
            calculations_df[f"% of Variance ({kpi})"] = (
                calculations_df[f"{kpi}_swing_squared"]
                / calculations_df[f"{kpi}_swing_squared"].sum()
            )
        calculations_df.rename(
            index=self.nodes_collection.get_nodes_mapping(), inplace=True
        )
        self.calculations_result = calculations_df
        return calculations_df
