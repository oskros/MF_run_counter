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
