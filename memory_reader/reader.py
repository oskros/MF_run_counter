import psutil  # REMOVING THIS LINE BREAKS MEMORY READING FOR GAME.EXE...
import pymem
import win32api
import logging
from memory_reader import reader_utils, stat_mappings
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
        self.d2lang = None
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
            elif mod_str == 'd2lang.dll':
                self.d2lang = mod.lpBaseOfDll

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
        self.hovered_item = None
        self.item_descripts = None
        self.str_indexer_table = None
        self.str_address_table = None
        self.patch_str_indexer_table = None
        self.patch_str_address_table = None
        self.exp_str_indexer_table = None
        self.exp_str_address_table = None

    def map_ptrs(self):
        if self.d2_ver == '1.13c':
            self.world_ptr       = self.d2game   + 0x111C24
            self.players_x_ptr   = self.d2game   + 0x111C1C
            self.player_unit_ptr = self.d2client + 0x10A60C
            self.in_pause_menu   = self.d2client + 0xFADA4
            self.unit_list_addr  = self.d2client + 0x10A808
            self.monster_add_adr = 0x0
            self.hovered_item    = self.d2client + 0x11BC38
            self.item_descripts  = self.d2common + 0x9FB94
            self.str_indexer_table       = self.d2lang + 0x10A64
            self.str_address_table       = self.d2lang + 0x10a68
            self.patch_str_indexer_table = self.d2lang + 0x10A80
            self.patch_str_address_table = self.d2lang + 0x10A6C
            self.exp_str_indexer_table   = self.d2lang + 0x10A84
            self.exp_str_address_table   = self.d2lang + 0x10A70
        elif self.d2_ver == '1.13d':
            self.world_ptr       = self.d2game   + 0x111C10
            self.players_x_ptr   = self.d2game   + 0x111C44
            self.player_unit_ptr = self.d2client + 0x101024
            self.in_pause_menu   = self.d2client + 0x11C8B4
            self.unit_list_addr  = self.d2client + 0x1049B8
            self.monster_add_adr = 0x0
            self.hovered_item    = self.d2client + 0x11CB28
            self.item_descripts  = self.d2common + 0xA4CB0
        elif self.d2_ver == '1.14b':
            self.world_ptr       = self.base_address + 0x47BD78
            self.players_x_ptr   = self.base_address + 0x47BDB0
            self.player_unit_ptr = self.base_address + 0x39DEFC
            self.in_pause_menu   = None
            self.unit_list_addr  = self.base_address + 0x39DEF8
            self.monster_add_adr = 0x80
            self.hovered_item    = None
            self.item_descripts  = self.base_address + 0x564A98
        elif self.d2_ver == '1.14c':
            self.world_ptr       = self.base_address + 0x47ACC0
            self.players_x_ptr   = self.base_address + 0x47ACF8
            self.player_unit_ptr = self.base_address + 0x39CEFC
            self.in_pause_menu   = None
            self.unit_list_addr  = self.base_address + 0x39CEF8
            self.monster_add_adr = 0x80
            self.hovered_item    = None
            self.item_descripts  = self.base_address + 0x5639E0
        elif self.d2_ver == '1.14d':
            self.world_ptr       = self.base_address + 0x483D38
            self.players_x_ptr   = self.base_address + 0x483D70
            self.player_unit_ptr = self.base_address + 0x3A5E74
            self.in_pause_menu   = self.base_address + 0x3A27E4
            self.unit_list_addr  = self.base_address + 0x3A5E70
            self.monster_add_adr = 0x80
            self.hovered_item    = None
            self.item_descripts  = self.base_address + 0x56CA58
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
            d2se_patch = self.pm.read_string(self.base_address + 0x1A049).strip()
            if d2se_patch not in ['1.07', '1.08', '1.09b', '1.09d', '1.10f', '1.11b', '1.12a', '1.13c']:
                d2se_patch = '1.13c'
            return d2se_patch
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
        vals = self.get_stats(player_unit)
        # lostatid: 12=level, 13=experience, 80=mf, 105=fcr

        out = dict()
        out['Name'] = char_name
        out['Level'] = next((v['value'] for v in vals if v['lostatid'] == 12 and v['histatid'] == 0), -1)
        out['Exp'] = next((v['value'] for v in vals if v['lostatid'] == 13 and v['histatid'] == 0), -1)
        out['Exp next'] = reader_utils.EXP_TABLE.get(out['Level'], dict()).get('Next', -1) + reader_utils.EXP_TABLE.get(out['Level'], dict()).get('Experience', 0)
        out['Exp missing'] = out['Exp next'] - out['Exp']
        try:
            out['Exp %'] = (out['Exp'] - reader_utils.EXP_TABLE.get(out['Level'], dict()).get('Experience', 0)) / reader_utils.EXP_TABLE.get(out['Level'], dict()).get('Next', 1)
        except ZeroDivisionError:
            out['Exp %'] = 1
        out['MF'] = next((v['value'] for v in vals if v['lostatid'] == 80 and v['histatid'] == 0), -1)
        out['Players X'] = max(self.pm.read_uint(self.players_x_ptr), 1)
        return out

    def get_stats(self, unit, translate_stat=False):
        statlist = self.pm.read_uint(unit + 0x5C)
        full_stats = self.pm.read_uint(statlist + 0x10) in [0x80000000, 0xA0000000]
        stat_array_addr = self.pm.read_uint(statlist + 0x48) if full_stats else self.pm.read_uint(statlist + 0x24)
        stat_array_len = self.pm.read_short(statlist + 0x4C)

        vals = []
        for i in range(0, stat_array_len):
            cur_addr = stat_array_addr + i * 8
            histatid = self.pm.read_short(cur_addr + 0x0)
            lostatid = self.pm.read_short(cur_addr + 0x2)
            if lostatid == 13:
                value = self.pm.read_uint(cur_addr + 0x4)
            else:
                value = self.pm.read_int(cur_addr + 0x4)

            if translate_stat:
                vals.append(reader_utils.translate_stat(histatid=histatid, lostatid=lostatid, value=value, stat_map=stat_mappings.STAT_MAP))
            else:
                vals.append({'histatid': histatid, 'lostatid': lostatid, 'value': value})
        return vals

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
        if prev_unit != 0:
            self.process_unit(prev_unit)

        unit_status = self.pm.read_uint(uadr + 0x10)
        game_guid = self.pm.read_uint(uadr + 0x0C)

        # unit is dead
        if unit_status == 12 and game_guid != 1:
            # unit death not already recorded, and unit also recorded as being alive at some point (no corpses)
            if game_guid not in self.dead_guids and game_guid in self.observed_guids:
                self.dead_guids.append(game_guid)
                mon_typeflag = self.pm.read_uint(self.pm.read_uint(uadr + 0x14) + 0x16)

                self.kill_counts['Total'] += 1
                mon_type = reader_utils.mon_type.get(mon_typeflag, None)
                if mon_type is None:
                    logging.debug('Failed to map monster TypeFlag: %s' % mon_typeflag)
                if mon_type in ['Unique', 'Champion', 'Minion']:
                    self.kill_counts[mon_type] += 1
        else:
            # Dont add non-selectable units to the observed list (npcs, hydras, etc)
            monstats_addr = self.pm.read_uint(self.pm.read_uint(uadr + 0x14) + 0x00)
            selectable = self.pm.read_short(monstats_addr + 0x4)
            if selectable > 0:
                self.observed_guids.add(game_guid)

    def get_string_table_by_identifier(self, identifier):
        if identifier >= 0x4E20:  # 20.000
            return {'index': self.exp_str_indexer_table,
                    'address': self.exp_str_address_table,
                    'offset': 0x4E20}
        elif identifier >= 0x2710:  # 10.000
            return {'index': self.patch_str_indexer_table,
                    'address': self.patch_str_address_table,
                    'offset': 0x2710}
        else:
            return {'index': self.str_indexer_table,
                    'address': self.str_address_table,
                    'offset': 0x0}

    def lookup_string_table(self, identifier):
        str_table = self.get_string_table_by_identifier(identifier)
        identifier -= str_table['offset']

        indexer_table = self.pm.read_uint(str_table['index'])
        address_table = self.pm.read_ushort(str_table['address'])

        identifier_count = self.pm.read_ushort(indexer_table + 0x2)
        if identifier >= identifier_count:
            identifier = 0x1F4

        str_data_region = indexer_table + 0x15
        get_address_index_location = lambda index: str_data_region + index * 2  # sizeof(ushort) = 2
        address_table_index = self.pm.read_ushort(get_address_index_location(identifier))

        if address_table_index >= self.pm.read_uint(indexer_table + 0x4):
            return None

        string_info_block = get_address_index_location(identifier_count)
        string_info_address = string_info_block + address_table_index * 0x11

        end_test = indexer_table + self.pm.read_ushort(indexer_table + 0x11)
        if string_info_address >= end_test:
            return None

        if not self.pm.read_ushort(string_info_address):
            return None

        string_address = self.pm.read_uint(address_table + address_table_index * 4)  # sizeof(uint) = 4
        if not string_address:
            return None

        return self.get_null_terminated_string(string_address, 0x100, 0x4000)

    def get_null_terminated_string(self, address, size, max_size):
        buffer_size = size
        value = None
        while buffer_size <= max_size:
            value = self.pm.read_string(address, buffer_size)
            null_terminator_index = value.index('\0')
            if null_terminator_index >= 0:
                value = value.replace('\0', '')
                return value
            buffer_size *= 2
        return value




if __name__ == '__main__':
    # print(elevate_access(lambda: eval('D2Reader().in_game()')))
    r = D2Reader()
    # print(r.d2_ver)
    r.map_ptrs()



    import tkinter as tk
    root = tk.Tk()
    root.wm_attributes("-topmost", 1)
    sv = tk.StringVar()
    cur_unit = None

    def update_hovered(cur_unit):
        p_unit = r.pm.read_uint(r.hovered_item)
        if p_unit > 0 and p_unit != cur_unit:
            cur_unit = p_unit
            e_class = r.pm.read_uint(p_unit + 0x4)
            item_descr_len = r.pm.read_uint(r.item_descripts)
            item_descr_adr = r.pm.read_uint(r.item_descripts + 0x4)
            specific_item_adr = r.pm.read_uint(item_descr_adr + item_descr_len*e_class)
            string_index = r.pm.read_ushort(specific_item_adr + 0xF4)
            name = r.lookup_string_table(string_index)

            vals = r.get_stats(p_unit, translate_stat=True)
            vals = reader_utils.group_and_hide_stats(vals)
            s_str = '\n'.join(['%s: %s' % (v['Display'], v['value']) if v['value'] != '' else '%s' % v['Display'] for v in vals])
            sv.set(s_str)
        root.after(50, lambda: update_hovered(cur_unit))
        return cur_unit

    cur_unit = update_hovered(cur_unit)

    tk.Label(root, text='hovered').pack()
    tk.Label(root, textvariable=sv).pack()

    root.mainloop()

