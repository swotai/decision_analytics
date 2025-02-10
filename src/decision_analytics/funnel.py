import itertools
import logging

import numpy as np
import pandas as pd

from decision_analytics import NodesCollection
from decision_analytics.plotting_utils import (
    plot_tornado,
    display_cdf_plot,
    display_pdf_plot,
    generate_cumulative_distribution_chart,
)
from decision_analytics.utils import values_map
from decision_analytics.metalogistic import MetaLogistic


class Funnel:
    def __init__(self, nodes_collection: NodesCollection):
        self.nodes_collection = nodes_collection
        self.input_node_names = [
            i.name for i in self.nodes_collection.get_input_nodes()
        ]
        self.kpi_node_names = [i.name for i in self.nodes_collection.get_kpi_nodes()]
        self.sim_result = pd.DataFrame()

    def simulate(self) -> None:
        """
        Workflow to complete simulation, first simulating variance by each input's low/mid/high values.
        Then updates calculations based on these simulated variances for all KPIs.
        """
        self.simulate_variances()
        self.update_calculations()

    def simulate_variances(self) -> pd.DataFrame:
        """
        Simulates all variations of the funnel by looping through all nodes and their value percentiles.
        Stores the results in self.sim_result.

        Returns
        -------
        pd.DataFrame
            Result dataframe with all simulated scenarios (inputs x low/mid/high). Dataframe is kept
            as instance property.

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
        # Reset all input nodes to median value
        self.nodes_collection.reset_input_nodes()
        return results_df

    def update_calculations(self) -> pd.DataFrame:
        """
        Update variance calculations based on the current simulation results for all KPIs.

        Returns
        -------
        pd.DataFrame
            Dataframe containing the summary table of each input's swing, swing squared,
            variance percentage of total, and combined uncertainty.
            Dataframe is stored as instance property.
        """
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

    def get_tornado_chart(self, kpi: str):
        df = self.calculations_result.sort_values(
            by=f"{kpi}_swing_squared", na_position="first"
        )
        return plot_tornado(df=df, kpi=kpi)

    def get_metalog(self, kpi: str):
        calc_result = self.calculations_result.loc[
            "Combined Uncertainty", [f"{kpi}_low", f"{kpi}_mid", f"{kpi}_high"]
        ]
        return MetaLogistic(cdf_xs=calc_result.tolist(), cdf_ps=[0.1, 0.5, 0.9])

    def get_cdf_chart(self, report_kpi: str):
        result_ml = self.get_metalog(report_kpi)
        cdf_data = result_ml.create_cdf_plot_data(p_from_to=(0.001, 0.999), n=100)
        report_kpi_label = self.nodes_collection.get_nodes_mapping()[report_kpi]
        return display_cdf_plot(cdf_data, report_kpi_label)

    def get_pdf_chart(self, report_kpi: str):
        result_ml = self.get_metalog(report_kpi)
        pdf_data = result_ml.create_pdf_plot_data(p_from_to=(0.001, 0.999), n=100)
        report_kpi_label = self.nodes_collection.get_nodes_mapping()[report_kpi]
        return display_pdf_plot(pdf_data, report_kpi_label)

    def get_cumulative_chart(self, kpi: str):
        return generate_cumulative_distribution_chart(self.sim_result, kpi=kpi)
