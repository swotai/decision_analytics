import math


def format_float(n, format_str: str = ".0f", millify: bool = True) -> str:
    """
    Format float to string.
    Sample usage:
      - percentages: print(format_float(0.2, '.2%'))
      - large dollar amounts: print(format_float(n=25489.76, format_str=',.2f', millify=True))

    Parameters
    ----------
    n : float or int
        Input Number
    format_str : str, optional
        Formatting string, default ".0f"
    millify : bool, optional
        Whether to convert large numbers to K/M/B/T, default True

    Returns
    -------
    str
        Output string
    """
    millnames = ["", " K", " M", " B", " T"]
    n = float(n)
    millidx = max(
        0,
        min(
            len(millnames) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))
        ),
    )
    if millify:
        value = n / 10 ** (3 * millidx)
    else:
        value = n
        millidx = 0
    return f"{{:{format_str}}}{{}}".format(value, millnames[millidx])


class Node:
    def __init__(
        self,
        name: str,
        value: float,
        format_str: str,
        input_type: str,
        readable_large_number: bool = True,
    ):
        self.name = name
        self.value = value
        self.format_str = format_str
        self.input_type = input_type
        self.readable_large_number = readable_large_number

    def pretty_value(self):
        """
        Pretty printing the value of the node, applying string formatting to the numeric value
        """
        return format_float(self.value, self.format_str, self.readable_large_number)

    def __repr__(self):
        node_description = (
            f"{self.name} (Type: {self.input_type}, Value:{self.pretty_value()})"
        )
        return node_description


class CalculatedNode(Node):
    def __init__(self, definition: str, **kwargs):
        self.definition = definition
        # pass rest to node init
        super().__init__(**kwargs)

        assert (
            self.input_type == "calculation"
        ), "Relation node must be calculation type"

    def __repr__(self):
        node_description = f"{self.name} (Type: {self.input_type}, Definition: {self.definition}, Value:{self.pretty_value()})"
        return node_description


class Funnel:

    def check_valid_definition(self):
        """Make sure that the definition of the relationship is valid and is safe"""
        # This can't happen inside calculated node, it has to happen inside the collection instead, as it needs to know the collection of input and calculated nodes.
        # Check to make sure all vars are valid input nodes (meaning this needs to be done after all nodes are finish init)
        # Check to make sure only allowed operators (+ - * / and () only )

    def sort_calculated_nodes(self):
        """
        Sort calculated nodes by level of dependency
        - go through list of all nodes, rank in order of:
            - input nodes
            - calculated nodes with all input nodes present
        - repeat till all nodes covered
        """

    def update_value(self):
        # This also needs to be in the collection class as it needs input from other node values
        self.value = safe_eval()
