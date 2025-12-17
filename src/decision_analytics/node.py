import logging
from typing import Optional

from decision_analytics.utils import format_float


class Node:
    def __init__(
        self,
        name: str,
        format_str: str,
        input_type: str,
        value_percentiles: Optional[tuple] = None,
        long_name: Optional[str] = None,
        description: Optional[str] = None,
        value: Optional[float] = None,
        is_kpi: Optional[bool] = False,
        readable_large_number: bool = True,
    ):
        """Initializes a node object

        Parameters
        ----------
        name : str
            The name of the node.
        format_str : str
            The format string for the node's value. For example, ".2%" for percentage values.
            If left blank, large numbers will be converted to readable format with K/M/B/T.
        input_type : str
            The type of input for the node, should be either "input" or "calculation".
        value_percentiles : Optional[tuple], optional
            The tuple of values for the node at the 10th, 50th, and 90th percentiles. By default None.
        long_name : Optional[str], optional
            A longer, more descriptive name for the node, by default None.
            If left blank, will convert regular_name to Regular Name.
        description : Optional[str], optional
            A brief description of the node, by default None.
        value : Optional[float], optional
            The initial value of the node, by default None.
        readable_large_number : bool, optional
            Whether to format large numbers in a more readable way, by default True.

        Raises
        ------
        ValueError
            If input_type is 'input' and value is None.
        ValueError
            If input_type is not 'input' or 'calculation'.
        ValueError
            If value_percentiles is provided and does not contain exactly 3 values.
        """
        # Check for invalid inputs
        if input_type == "input" and value is None:
            raise ValueError("Value must be provided when input_type is 'input'")
        if input_type not in ["input", "calculation"]:
            raise ValueError("input_type must be either 'input' or 'calculation'")

        # metadata attributes
        self.name = name
        self.input_type = input_type
        self.readable_large_number = readable_large_number
        self.long_name = (
            name.replace("_", " ").title()
            if long_name is None or long_name == ""
            else long_name
        )
        self.description = description
        if is_kpi and input_type == "input":
            raise ValueError("KPIs cannot be input node.")
        self.is_kpi = is_kpi

        # value and distribution attributes
        self.value = value
        if format_str:
            self.format_str = format_str
        else:
            # default 2 decimal places
            self.format_str = ".2f"
        if value_percentiles == ():
            value_percentiles = None
        if value_percentiles is not None and len(value_percentiles) != 3:
            raise ValueError(
                "Range must contain exactly 3 values representing 10th, 50th, and 90th percentiles"
            )
        # self.value_percentiles = (
        #     value_percentiles if value_percentiles is not None else [None, None, None]
        # )
        self.value_percentiles = value_percentiles
        # rank, for sorting nodes
        self.rank = 0

    def _pretty_value(self) -> str:
        """
        Pretty printing the value of the node, applying string formatting to the numeric value
        """
        if self.value is not None:
            return format_float(self.value, self.format_str, self.readable_large_number)
        else:
            return "N/A"

    def __repr__(self):
        repr_node_desc = f"{self.name} (Type: {self.input_type}, Value:{self._pretty_value()}, Rank: {self.rank})"
        if self.value_percentiles:
            repr_node_desc += f", Input Range: {self.value_percentiles}"
        return repr_node_desc

    def get_chart_str(self) -> str:
        """Pretty printing for pumping to mermaid chart

        Returns
        -------
        str
            String representation of the node description suitable for Mermaid chart.
        """
        chart_str = f"{self.long_name}\n{self._pretty_value()}"
        return chart_str

    def update_value_percentiles(self, value_percentiles: tuple) -> None:
        if value_percentiles is not None and len(value_percentiles) != 3:
            raise ValueError(
                "Range must contain exactly 3 values representing 10th, 50th, and 90th percentiles"
            )
        if not all(x < y for x, y in zip(value_percentiles, value_percentiles[1:])):
            raise ValueError("Values in value_percentiles must be in ascending order")
        self.value_percentiles = value_percentiles
        logging.debug(
            f"Added value percentiles to node {self.name}: {value_percentiles}"
        )

    def update_value(self, new_value: float) -> None:
        """
        Update the value of the node.

        Parameters
        ----------
        new_value : float
            The new value to set for the node.
        """
        if self.input_type == "input" and new_value is None:
            raise ValueError("Value must be provided when input_type is 'input'")
        self.value = new_value
        logging.debug(f"Updated value of node {self.name} to: {new_value}")
