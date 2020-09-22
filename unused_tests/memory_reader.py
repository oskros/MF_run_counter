import psutil
import pymem
import win32api
# tp = pymem.ressources.structure.TOKEN_PRIVILEGES()
# luid = pymem.ressources.structure.LUID()
# pymem.process.set_debug_privilege()

# look here for reading .d2s files: https://github.com/nokka/d2s
# Will pull memory addresses from https://github.com/Zutatensuppe/DiabloInterface/blob/master/src/D2Reader/GameMemoryTableFactory.cs#L70-L74


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


print('User admin: %s' % is_user_admin())
if is_user_admin():
    pm = pymem.Pymem('Game.exe')
    pid = pm.process_id
    print('Process id: %s' % pid)
    base_address = pm.process_base.lpBaseOfDll
    print('Base address: %s' % base_address)

    dlls = ['D2Common.dll', 'D2Launch.dll', 'D2Lang.dll', 'D2Net.dll', 'D2Game.dll', 'D2Client.dll']
    addrs = {x.name: x.lpBaseOfDll for x in pm.list_modules() if x.name in dlls}

    PlayersX = addrs['D2Game.dll'] + 0x111C44

    players_x = pm.read_int(PlayersX)
    print(players_x)

    player_unit_ptr = pm.read_int(address=addrs['D2Client.dll'] + 0x00101024)
    statlist = pm.read_int(player_unit_ptr + 0x005C)
    full_stats = hex(pm.read_uint(statlist + 0x0010)) == '0x80000000'
    stat_array_addr = pm.read_int(statlist + 0x0048) if full_stats else pm.read_int(statlist + 0x0024)
    stat_array_len = pm.read_short(statlist + 0x004C)

    vals = []
    for i in range(0, stat_array_len):
        cur_addr = stat_array_addr + i * 8
        histatid = pm.read_short(cur_addr + 0x00)
        lostatid = pm.read_short(cur_addr + 0x02)
        value = pm.read_uint(cur_addr + 0x04)
        vals.append({'histatid': histatid, 'lostatid': lostatid, 'value': value})
    # 12: level, 13: experience, 80: mf, 105: fcr
    # experience table: http://classic.battle.net/diablo2exp/basics/levels.shtml

    fixed_file_info = win32api.GetFileVersionInfo(pm.process_base.filename.decode(), '\\')
    raw_version = '{:d}.{:d}.{:d}.{:d}'.format(
        fixed_file_info['FileVersionMS'] // 65536,
        fixed_file_info['FileVersionMS'] % 65536,
        fixed_file_info['FileVersionLS'] // 65536,
        fixed_file_info['FileVersionLS'] % 65536)
    patch_map = {'1.14.3.71': '1.14d', '1.14.2.70': '1.14c', '1.14.1.68': '1.14b', '1.0.13.64': '1.13d', '1.0.13.60': '1.13c'}
    patch = patch_map.get(raw_version, None)

    print(patch)
else:
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)


    # full_stats = hex(abs(pm.read_int(statlist + 0x0010))) == '0x80000000'
    # if full_stats:
    #     stat_array = pm.read_int(statlist + 0x0048)
    # else:
    #     stat_array = pm.read_int(statlist + 0x0024)
