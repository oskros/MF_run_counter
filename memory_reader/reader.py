import psutil  # REMOVING THIS LINE BREAKS MEMORY READING FOR GAME.EXE...
import pymem
import win32api
import logging
from memory_reader import reader_utils

D2_GAME_EXE = 'Game.exe'
D2_SE_EXE = 'D2SE.exe'


class D2Reader:
    def __init__(self, process_name=D2_GAME_EXE):
        self.pm = pymem.Pymem(process_name, verbose=False, debug=False)
        self.is_d2se = (process_name == D2_SE_EXE)

        self.base_address = self.pm.process_base.lpBaseOfDll
        logging.debug('D2 base address: %s' % self.base_address)

        self.d2_ver = self.get_d2_version()
        logging.debug('D2 version: %s' % self.d2_ver)

        self.dlls_loaded = True
        self.is_plugy = False
        self.d2client = None
        self.d2game = None
        self.d2net = None
        # print([x.name for x in self.pm.list_modules()])
        for mod in self.pm.list_modules():
            mod_str = mod.name.lower()
            if mod_str == 'plugy.dll':
                self.is_plugy = True
            elif mod_str == 'd2client.dll':
                self.d2client = mod.lpBaseOfDll
            elif mod_str == 'd2game.dll':
                self.d2game = mod.lpBaseOfDll
            elif mod_str == 'd2net.dll':
                self.d2net = mod.lpBaseOfDll

        if self.is_d2se or self.d2_ver in ['1.13c', '1.13d']:
            if self.d2client is None or self.d2game is None or self.d2net is None:
                self.dlls_loaded = False

        self.patch_supported = True
        self.world_ptr = None
        self.players_x_ptr = None
        self.player_unit_ptr = None

    def map_ptrs(self):
        if self.d2_ver == '1.13c':
            self.world_ptr       = self.d2game   + 0x111C24
            self.players_x_ptr   = self.d2game   + 0x111C1C
            self.player_unit_ptr = self.d2client + 0x10A60C
        elif self.d2_ver == '1.13d':
            self.world_ptr       = self.d2game   + 0x111C10
            self.players_x_ptr   = self.d2game   + 0x111C44
            self.player_unit_ptr = self.d2client + 0x101024
        elif self.d2_ver == '1.14b':
            self.world_ptr       = self.base_address + 0x47BD78
            self.players_x_ptr   = self.base_address + 0x47BDB0
            self.player_unit_ptr = self.base_address + 0x39DEFC
        elif self.d2_ver == '1.14c':
            self.world_ptr       = self.base_address + 0x47ACC0
            self.players_x_ptr   = self.base_address + 0x47ACF8
            self.player_unit_ptr = self.base_address + 0x39CEFC
        elif self.d2_ver == '1.14d':
            self.world_ptr       = self.base_address + 0x483D38
            self.players_x_ptr   = self.base_address + 0x483D70
            self.player_unit_ptr = self.base_address + 0x3A5E74
        else:
            self.patch_supported = False

    def get_d2_version(self):
        if self.is_d2se:
            return self.pm.read_string(self.base_address + 0x1A049).strip()
        fixed_file_info = win32api.GetFileVersionInfo(self.pm.process_base.filename.decode(), '\\')
        raw_version = '{:d}.{:d}.{:d}.{:d}'.format(
            fixed_file_info['FileVersionMS'] // 65536,
            fixed_file_info['FileVersionMS'] % 65536,
            fixed_file_info['FileVersionLS'] // 65536,
            fixed_file_info['FileVersionLS'] % 65536)
        patch_map = {'1.14.3.71': '1.14d', '1.14.2.70': '1.14c', '1.14.1.68': '1.14b', '1.0.13.64': '1.13d',
                     '1.0.13.60': '1.13c'}
        return patch_map.get(raw_version, None)

    def in_game_sp(self):
        # This approach only works in single player
        return bool(self.pm.read_uint(self.world_ptr))

    def in_game(self):
        # FIXME: Inappropriate way of testing whether character is in-game, and could create unexpected results
        player_unit = self.pm.read_uint(self.player_unit_ptr)
        try:
            # Gets character name - returns memory error out of game
            self.pm.read_string(self.pm.read_uint(player_unit + 0x14))
            return True
        except pymem.exception.MemoryReadError:
            return False

    def player_unit_stats(self):
        player_unit = self.pm.read_uint(self.player_unit_ptr)

        char_name = self.pm.read_string(self.pm.read_uint(player_unit + 0x14))
        statlist = self.pm.read_uint(player_unit + 0x005C)
        full_stats = hex(self.pm.read_uint(statlist + 0x0010)) == '0x80000000'
        stat_array_addr = self.pm.read_uint(statlist + 0x0048) if full_stats else self.pm.read_uint(statlist + 0x0024)
        stat_array_len = self.pm.read_short(statlist + 0x004C)

        vals = []
        for i in range(0, stat_array_len):
            cur_addr = stat_array_addr + i * 8
            histatid = self.pm.read_short(cur_addr + 0x00)
            lostatid = self.pm.read_short(cur_addr + 0x02)
            value = self.pm.read_uint(cur_addr + 0x04)

            vals.append({'histatid': histatid, 'lostatid': lostatid, 'value': value})
        # lostatid: 12=level, 13=experience, 80=mf, 105=fcr

        out = dict()
        out['Name'] = char_name
        out['Level'] = next((v['value'] for v in vals if v['lostatid'] == 12 and v['histatid'] == 0), -1)
        out['Exp'] = next((v['value'] for v in vals if v['lostatid'] == 13 and v['histatid'] == 0), -1)
        out['Exp next'] = reader_utils.EXP_TABLE.get(out['Level'], dict()).get('Next', -1) + reader_utils.EXP_TABLE.get(out['Level'], dict()).get('Experience', 0)
        out['Exp missing'] = out['Exp next'] - out['Exp']
        out['Exp %'] = (out['Exp'] - reader_utils.EXP_TABLE.get(out['Level'], dict()).get('Experience', 0)) / reader_utils.EXP_TABLE.get(out['Level'], dict()).get('Next', 1)
        out['MF'] = next((v['value'] for v in vals if v['lostatid'] == 80 and v['histatid'] == 0), -1)
        out['Players X'] = self.pm.read_uint(self.players_x_ptr)
        return out


if __name__ == '__main__':
    from pprint import pprint
    # print(elevate_access(lambda: eval('D2Reader().in_game()')))
    r = D2Reader()
    r.map_ptrs()
    pprint(r.player_unit_stats())
