import os
import json
import libs.screeninfo
from libs.pymem import exception as pymem_exception
import atomicwrites
import logging


def listdir(path):
    try:
        return os.listdir(path=path)
    except FileNotFoundError as e:
        logging.warning(f'Path not found. Error: {e}')
        return []


def safe_eval(inp_str):
    if not isinstance(inp_str, str):
        return inp_str
    try:
        return eval(inp_str, {'__builtins__': {}})
    except (SyntaxError, NameError):
        return inp_str


def build_time_str(elap):
    hours = int(elap / 3600)
    minutes = int(elap / 60 - hours * 60.0)
    seconds = int(elap - hours * 3600.0 - minutes * 60.0)
    hseconds = int((elap - hours * 3600.0 - minutes * 60.0 - seconds) * 10)
    return '%02d:%02d:%02d:%1d' % (hours, minutes, seconds, hseconds)


def get_monitor_from_coord(x, y, disable_scaling=True):
    monitors = libs.screeninfo.get_monitors(disable_scaling=disable_scaling)

    for m in reversed(monitors):
        if m.x <= x <= m.width + m.x and m.y <= y <= m.height + m.y:
            return m
    return monitors[0]


def atomic_json_dump(dest_file: str, data: [dict, list]) -> None:
    """
    Some users experienced data loss in case of sudden power outages, this wrapper should ensure that file saves are
    atomic such that it doesn't happen going forward
    """
    with atomicwrites.atomic_write(dest_file, overwrite=True) as fo:
        json.dump(data, fo, indent=2)


def json_load_err(file_path):
    with open(file_path, 'r') as fo:
        try:
            state = json.load(fo)
        except json.JSONDecodeError as e:
            e.args = (e.args[0] + f' - file: {file_path}', *e.args[1:])
            raise e
    return state


pymem_err_list = (pymem_exception.ProcessError, pymem_exception.ProcessNotFound, pymem_exception.WinAPIError,
                  pymem_exception.MemoryReadError, KeyError, AttributeError, TypeError)


def filter_items(data_list, field):
    """
    Filter items from a list of dictionaries where field exists and doesn't contain '--'.
    
    Args:
        data_list: List of dictionaries
        field: Field name to check
    
    Returns:
        List of filtered items (dictionaries)
    """
    return [item for item in data_list if field in item and '--' not in str(item[field])]


def safe_avg(values, decimals=None):
    """
    Calculate average, returning empty string if values list is empty.
    
    Args:
        values: List of numeric values
        decimals: Number of decimal places for rounding (None for no rounding)
    
    Returns:
        Average (rounded if decimals specified), or empty string if no values
    """
    if not values:
        return ''
    result = sum(values) / len(values)
    return round(result, decimals) if decimals is not None else result


def safe_divide(numerator, denominator, decimals=None):
    """
    Safely divide two numbers, returning empty string if denominator is zero/falsy or numerator is empty string.
    
    Args:
        numerator: Numerator value (can be empty string)
        denominator: Denominator value (can be empty string, zero, or falsy)
        decimals: Number of decimal places for rounding (None for no rounding)
    
    Returns:
        Division result (rounded if decimals specified), or empty string if invalid
    """
    if not denominator or numerator == '':
        return ''
    result = numerator / denominator
    return round(result, decimals) if decimals is not None else result


def numeric_sort_key(value, empty_first=True):
    """
    Returns a sort key for numeric values that may contain percentage signs.
    Handles empty strings, percentage signs, and invalid values gracefully.
    
    Args:
        value: The value to create a sort key for (string or number)
        empty_first: If True, empty values sort first (return -inf), else last (return inf)
    
    Returns:
        float: Sort key value (-inf/inf for empty, numeric value otherwise)
    """
    if value == '' or value is None:
        return float('-inf') if empty_first else float('inf')
    
    try:
        # Convert to string, remove percentage sign, and convert to float
        str_value = str(value).replace('%', '').strip()
        if not str_value:
            return float('-inf') if empty_first else float('inf')
        return float(str_value)
    except (ValueError, TypeError):
        # If conversion fails, treat as empty
        return float('-inf') if empty_first else float('inf')