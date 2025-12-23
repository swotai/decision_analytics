import logging
from typing import Optional

from decision_analytics.utils import format_float


class Node:
    def __init__(
        self,
        name: str,
        format_str: str,
        node_type: str,
        value_low: Optional[float] = None,
        value_mid: Optional[float] = None,
        value_high: Optional[float] = None,
        long_name: Optional[str] = None,
        description: Optional[str] = None,
        value: Optional[float] = None,
        is_kpi: Optional[bool] = False,
        readable_large_number: bool = True,
        **kwargs,
    ):
        """Initializes a node object

        Parameters
        ----------
        name : str
            The name of the node.
        format_str : str
            The format string for the node's value. For example, ".2%" for percentage values.
            If left blank, large numbers will be converted to readable format with K/M/B/T.
        node_type : str
            The type of input for the node, should be either "input" or "calculation".
        value_low : Optional[float], optional
            The lower bound value for the node (10th percentile), by default None.
        value_mid : Optional[float], optional
            The middle value for the node (50th percentile), by default None.
        value_high : Optional[float], optional
            The upper bound value for the node (90th percentile), by default None.
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
            If node_type is 'input' and value is None.
        ValueError
            If node_type is not 'input' or 'calculation'.
        ValueError
            If value_low, value_mid, and value_high are not consistently provided or ordered.
        """
        # Check for invalid inputs
        if node_type == "input" and value is None:
            raise ValueError("Value must be provided when node_type is 'input'")
        if node_type not in ["input", "calculation"]:
            raise ValueError("node_type must be either 'input' or 'calculation'")

        # metadata attributes
        self.name = name
        self.node_type = node_type
        self.readable_large_number = readable_large_number
        self.long_name = (
            name.replace("_", " ").title()
            if long_name is None or long_name == ""
            else long_name
        )
        self.description = description
        if is_kpi and node_type == "input":
            raise ValueError("KPIs cannot be input node.")
        self.is_kpi = is_kpi

        # value and distribution attributes
        self.value = value
        if format_str:
            self.format_str = format_str
        else:
            # default 2 decimal places
            self.format_str = ".2f"
        # Value percentiles
        self.value_low = value_low
        self.value_mid = value_mid
        self.value_high = value_high

        if any([value_low, value_mid, value_high]) and not all(
            [value_low, value_mid, value_high]
        ):
            raise ValueError(
                "If any of value_low, value_mid, or value_high are provided, all three must be provided."
            )
        if (
            all([value_low, value_mid, value_high])
            and not value_low <= value_mid <= value_high
        ):
            raise ValueError(
                "value_low, value_mid, and value_high must be in ascending order."
            )
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
        repr_node_desc = f"{self.name} (Type: {self.node_type}, Value:{self._pretty_value()}, Rank: {self.rank})"
        if all([self.value_low, self.value_mid, self.value_high]):
            repr_node_desc += f", Input Range: ({self.value_low}, {self.value_mid}, {self.value_high})"
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

    def update_value(self, new_value: float) -> None:
        """
        Update the value of the node.

        Parameters
        ----------
        new_value : float
            The new value to set for the node.
        """
        if self.node_type == "input" and new_value is None:
            raise ValueError("Value must be provided when node_type is 'input'")
        self.value = new_value
        logging.debug(f"Updated value of node {self.name} to: {new_value}")
