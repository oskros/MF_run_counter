import psutil  # REMOVING THIS LINE BREAKS MEMORY READING FOR GAME.EXE...
import pymem
import win32api
import logging
from memory_reader import reader_utils
from utils.other_utils import pymem_err_list
from collections import defaultdict

D2_GAME_EXE = 'Game.exe'
D2_SE_EXE = 'D2SE.exe'


class D2Reader:
    def __init__(self, process_name=D2_GAME_EXE):
        self.pm = pymem.Pymem(process_name, verbose=False, debug=False)
        self.is_d2se = (process_name == D2_SE_EXE)
        self.dead_guids = []
        self.observed_guids = set()
        self.kill_counts = defaultdict(lambda: 0)

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
            elif mod_str == 'd2common.dll':
                self.d2common = mod.lpBaseOfDll

        if self.is_d2se or self.d2_ver in ['1.13c', '1.13d']:
            if self.d2client is None or self.d2game is None or self.d2net is None:
                self.dlls_loaded = False

        self.patch_supported = True
        self.world_ptr = None
        self.players_x_ptr = None
        self.player_unit_ptr = None
        self.in_pause_menu = None
        self.unit_list_addr = None
        self.monster_add_adr = None

    def map_ptrs(self):
        if self.d2_ver == '1.13c':
            self.world_ptr       = self.d2game   + 0x111C24
            self.players_x_ptr   = self.d2game   + 0x111C1C
            self.player_unit_ptr = self.d2client + 0x10A60C
            self.in_pause_menu   = self.d2client + 0xFADA4
            self.unit_list_addr  = self.d2client + 0x10A808  # units113
            self.monster_add_adr = 0x0
        elif self.d2_ver == '1.13d':
            self.world_ptr       = self.d2game   + 0x111C10
            self.players_x_ptr   = self.d2game   + 0x111C44
            self.player_unit_ptr = self.d2client + 0x101024
            self.in_pause_menu   = self.d2client + 0x11C8B4
            self.unit_list_addr  = self.d2client + 0x1049B8
            self.monster_add_adr = 0x0
        elif self.d2_ver == '1.14b':
            self.world_ptr       = self.base_address + 0x47BD78
            self.players_x_ptr   = self.base_address + 0x47BDB0
            self.player_unit_ptr = self.base_address + 0x39DEFC
            self.unit_list_addr  = self.base_address + 0x39DEF8
            self.monster_add_adr = 0x80
        elif self.d2_ver == '1.14c':
            self.world_ptr       = self.base_address + 0x47ACC0
            self.players_x_ptr   = self.base_address + 0x47ACF8
            self.player_unit_ptr = self.base_address + 0x39CEFC
            self.unit_list_addr  = self.base_address + 0x39CEF8
            self.monster_add_adr = 0x80
        elif self.d2_ver == '1.14d':
            self.world_ptr       = self.base_address + 0x483D38
            self.players_x_ptr   = self.base_address + 0x483D70
            self.player_unit_ptr = self.base_address + 0x3A5E74
            self.in_pause_menu   = self.base_address + 0x3A27E4
            self.unit_list_addr  = self.base_address + 0x3A5E70
            self.monster_add_adr = 0x80
        else:
            self.patch_supported = False

    def is_game_paused(self):
        if self.in_pause_menu is not None:
            try:
                out = bool(self.pm.read_uint(self.in_pause_menu))
            except pymem_err_list:
                out = False
        else:
            out = False
        return out

    def get_d2_version(self):
        if self.is_d2se:
            return self.pm.read_string(self.base_address + 0x1A049).strip()
        try:
            decoded_filename = self.pm.process_base.filename.decode('utf-8')
        except UnicodeDecodeError:
            # Handle issues with decoding umlauts
            decoded_filename = self.pm.process_base.filename.decode('windows-1252')
        fixed_file_info = win32api.GetFileVersionInfo(decoded_filename, '\\')
        raw_version = '{:d}.{:d}.{:d}.{:d}'.format(
            fixed_file_info['FileVersionMS'] // 65536,
            fixed_file_info['FileVersionMS'] % 65536,
            fixed_file_info['FileVersionLS'] // 65536,
            fixed_file_info['FileVersionLS'] % 65536)
        patch_map = {'1.14.3.71': '1.14d', '1.14.2.70': '1.14c', '1.14.1.68': '1.14b', '1.0.13.64': '1.13d',
                     '1.0.13.60': '1.13c'}
        return patch_map.get(raw_version, raw_version)

    def in_game_sp(self):
        # This approach only works in single player
        return bool(self.pm.read_uint(self.world_ptr))

    def in_game(self):
        # FIXME: Indirect way of testing whether character is in-game, rather have a direct test
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

    def update_dead_guids(self):
        for guid in range(128):
            unit_addr = self.pm.read_uint(self.unit_list_addr + (guid + self.monster_add_adr)*4)
            if unit_addr > 0:
                self.process_unit(unit_addr)

    def process_unit(self, uadr):
        # Check unit is monster
        if self.pm.read_uint(uadr) != 1:
            return

        # Sometimes a previous unit is attached to another unit, we handle that recursively here
        prev_unit = self.pm.read_uint(uadr + 0xE4)
        if prev_unit != 0:            # print('prev_unit: %s' % prev_unit)
            self.process_unit(prev_unit)

        unit_status = self.pm.read_uint(uadr + 0x10)
        game_guid = self.pm.read_uint(uadr + 0x0C)

        # unit is dead
        if unit_status == 12 and game_guid != 1:
            # unit death not already recorded, and unit also recorded as being alive at some point (no corpses)
            if game_guid not in self.dead_guids and game_guid in self.observed_guids:
                self.dead_guids.append(game_guid)
                mon_typeflag = self.pm.read_uint(self.pm.read_uint(uadr + 0x14) + 0x16)

                # FIXME: seems like hydras (and potentially also other summons) will increment the counter
                self.kill_counts['Total'] += 1
                mon_type = reader_utils.mon_type.get(mon_typeflag, None)
                if mon_type is None:
                    # print(mon_typeflag)
                    logging.debug('Failed to map monster TypeFlag: %s' % mon_typeflag)
                if mon_type in ['Unique', 'Champion']:
                    self.kill_counts[mon_type] += 1
        else:
            self.observed_guids.add(game_guid)


if __name__ == '__main__':
    # print(elevate_access(lambda: eval('D2Reader().in_game()')))
    r = D2Reader()
    # print(r.d2_ver)
    r.map_ptrs()

    import tkinter as tk
    root = tk.Tk()
    root.wm_attributes("-topmost", 1)
    sv = tk.StringVar()

    def add_to_killed():
        r.in_game()
        r.update_dead_guids()
        sv.set('\n'.join(['%s: %s' % (k, v) for k, v in r.kill_counts.items()]))
        root.after(50, add_to_killed)

    add_to_killed()

    tk.Label(root, text='killcount').pack()
    tk.Label(root, textvariable=sv).pack()

    root.mainloop()

