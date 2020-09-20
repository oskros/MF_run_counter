import psutil
import pymem
import win32api
import os
import ctypes
import sys


class AdminStateUnknownError(Exception):
    """Cannot determine whether the user is an admin."""
    pass


def is_user_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        pass
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() == 1
    except AttributeError:
        raise AdminStateUnknownError


def elevate_access(func):
    if is_user_admin():
        return func()
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)


class D2Reader:
    def __init__(self):
        self.pm = pymem.Pymem('Game.exe')
        self.d2_ver = self.get_d2_version()
        if self.d2_ver != '1.13d':
            raise ValueError('Your game version is "%s", currently only "1.13d" is supported')

        self.base_address = self.pm.process_base.lpBaseOfDll

        dlls = ['D2Common.dll', 'D2Launch.dll', 'D2Lang.dll', 'D2Net.dll', 'D2Game.dll', 'D2Client.dll']
        self.dll_addrs = {x.name: x.lpBaseOfDll for x in self.pm.list_modules() if x.name in dlls}

    def get_d2_version(self):
        fixed_file_info = win32api.GetFileVersionInfo(self.pm.process_base.filename.decode(), '\\')
        raw_version = '{:d}.{:d}.{:d}.{:d}'.format(
            fixed_file_info['FileVersionMS'] // 65536,
            fixed_file_info['FileVersionMS'] % 65536,
            fixed_file_info['FileVersionLS'] // 65536,
            fixed_file_info['FileVersionLS'] % 65536)
        patch_map = {'1.14.3.71': '1.14d', '1.14.2.70': '1.14c', '1.14.1.68': '1.14b', '1.0.13.64': '1.13d',
                     '1.0.13.60': '1.13c'}
        return patch_map.get(raw_version, None)


if __name__ == '__main__':
    reader = elevate_access(D2Reader)
    players_x_addr = reader.dll_addrs['D2Game.dll'] + 0x111C44

    print(reader.d2_ver)
    print(reader.pm.read_int(players_x_addr))
