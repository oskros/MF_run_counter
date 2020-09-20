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
        self.pm = pymem.Pymem('Game.exe', verbose=False)

        self.d2_ver = self.get_d2_version()

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

    def in_game(self):
        if self.d2_ver == '1.13d':
            world_addr = self.dll_addrs['D2Game.dll'] + 0x111C10
        elif self.d2_ver == '1.13c':
            world_addr = self.dll_addrs['D2Game.dll'] + 0x111C24
        else:
            raise NotImplementedError("Addresses for other versions than 1.13c and 1.13d not implemented yet")

        return bool(self.pm.read_int(world_addr))


if __name__ == '__main__':
    # D2Reader()
    print(elevate_access(lambda: eval('D2Reader().in_game()')))
    # players_x_addr = reader.dll_addrs['D2Game.dll'] + 0x111C44
    # selected_inv_addr = reader.dll_addrs['D2Client.dll'] + 0x11CB28
    # get_item_name_addr = reader.dll_addrs['D2Client.dll'] + 0x958C0

    # ping_addr = reader.dll_addrs['D2Client.dll'] + 0x108764
    # object_text = reader.dll_addrs['D2Common.dll'] + 0x1ADC0
    # world = reader.dll_addrs['D2Game.dll'] + 0x111C10

    # print(reader.d2_ver)
    # print(reader.pm.read_int(players_x_addr))
    # print(reader.pm.read_int(selected_inv_addr))
    # print(reader.pm.read_int(get_item_name_addr))
    # print(reader.pm.read_int(ping_addr))
    # print(reader.pm.read_int(world))
    # print(reader.pm.read_int(object_text))
    # print(reader.pm.read_bytes(object_text, 100))

    # print(reader.pm.read_string(test_addr, 10))
    # print(reader.pm.read_char(test_addr))