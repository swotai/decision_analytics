import math
import logging

values_map = {
    0: {"label": "value_low", "pr": 0.25, "represented_qtile": 0.1},
    1: {"label": "value_mid", "pr": 0.5, "represented_qtile": 0.5},
    2: {"label": "value_high", "pr": 0.25, "represented_qtile": 0.9},
}


def setup_logging(level=logging.WARNING):
    logging.basicConfig(level=level)


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


def fit_data_with_metalog():
    pass
