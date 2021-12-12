import os
import json
from tkinter import messagebox
import libs.screeninfo
from libs.pymem import exception as pymem_exception
import atomicwrites


def safe_eval(inp_str):
    if not isinstance(inp_str, str):
        return inp_str
    try:
        return eval(inp_str, {'__builtins__': {}})
    except SyntaxError:
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


def test_mapfile_path(game_path, char_name):
    if not os.path.exists(game_path) or game_path in ['', '.']:
        messagebox.showerror('Game path error', """Game path not found, please update the path in options (for PoD, it's ending with "/Path of Diablo/Save/Path of Diablo") \n\n"""
                                                'This session will continue in manual mode.')
        return False
    elif char_name == '':
        messagebox.showerror('Character name missing', 'Chosen profile has no character name specified. Create a new profile with a character name to use automode\n\n'
                                                       'This session will continue in manual mode.')
        return False
    elif not os.path.exists(os.path.join(game_path, char_name)):
        messagebox.showerror('Character file not found', 'Map file for specified character not found. Make sure the character name in chosen profile is identical to your in-game character name. If not, create a new profile with the correct character name\n\n'
                                                         'This session will continue in manual mode')
        return False
    return True


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
