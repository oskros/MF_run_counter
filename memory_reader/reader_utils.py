import ctypes
from libs import pymem
import logging
from memory_reader import stat_mappings
from init import *

EXP_TABLE = {1: {'Experience': 0, 'Next': 500},
             2: {'Experience': 500, 'Next': 1000},
             3: {'Experience': 1500, 'Next': 2250},
             4: {'Experience': 3750, 'Next': 4125},
             5: {'Experience': 7875, 'Next': 6300},
             6: {'Experience': 14175, 'Next': 8505},
             7: {'Experience': 22680, 'Next': 10206},
             8: {'Experience': 32886, 'Next': 11510},
             9: {'Experience': 44396, 'Next': 13319},
             10: {'Experience': 57715, 'Next': 14429},
             11: {'Experience': 72144, 'Next': 18036},
             12: {'Experience': 90180, 'Next': 22545},
             13: {'Experience': 112725, 'Next': 28181},
             14: {'Experience': 140906, 'Next': 35226},
             15: {'Experience': 176132, 'Next': 44033},
             16: {'Experience': 220165, 'Next': 55042},
             17: {'Experience': 275207, 'Next': 68801},
             18: {'Experience': 344008, 'Next': 86002},
             19: {'Experience': 430010, 'Next': 107503},
             20: {'Experience': 537513, 'Next': 134378},
             21: {'Experience': 671891, 'Next': 167973},
             22: {'Experience': 839864, 'Next': 209966},
             23: {'Experience': 1049830, 'Next': 262457},
             24: {'Experience': 1312287, 'Next': 328072},
             25: {'Experience': 1640359, 'Next': 410090},
             26: {'Experience': 2050449, 'Next': 512612},
             27: {'Experience': 2563061, 'Next': 640765},
             28: {'Experience': 3203826, 'Next': 698434},
             29: {'Experience': 3902260, 'Next': 761293},
             30: {'Experience': 4663553, 'Next': 829810},
             31: {'Experience': 5493363, 'Next': 904492},
             32: {'Experience': 6397855, 'Next': 985897},
             33: {'Experience': 7383752, 'Next': 1074627},
             34: {'Experience': 8458379, 'Next': 1171344},
             35: {'Experience': 9629723, 'Next': 1276765},
             36: {'Experience': 10906488, 'Next': 1391674},
             37: {'Experience': 12298162, 'Next': 1516924},
             38: {'Experience': 13815086, 'Next': 1653448},
             39: {'Experience': 15468534, 'Next': 1802257},
             40: {'Experience': 17270791, 'Next': 1964461},
             41: {'Experience': 19235252, 'Next': 2141263},
             42: {'Experience': 21376515, 'Next': 2333976},
             43: {'Experience': 23710491, 'Next': 2544034},
             44: {'Experience': 26254525, 'Next': 2772997},
             45: {'Experience': 29027522, 'Next': 3022566},
             46: {'Experience': 32050088, 'Next': 3294598},
             47: {'Experience': 35344686, 'Next': 3591112},
             48: {'Experience': 38935798, 'Next': 3914311},
             49: {'Experience': 42850109, 'Next': 4266600},
             50: {'Experience': 47116709, 'Next': 4650593},
             51: {'Experience': 51767302, 'Next': 5069147},
             52: {'Experience': 56836449, 'Next': 5525370},
             53: {'Experience': 62361819, 'Next': 6022654},
             54: {'Experience': 68384473, 'Next': 6564692},
             55: {'Experience': 74949165, 'Next': 7155515},
             56: {'Experience': 82104680, 'Next': 7799511},
             57: {'Experience': 89904191, 'Next': 8501467},
             58: {'Experience': 98405658, 'Next': 9266598},
             59: {'Experience': 107672256, 'Next': 10100593},
             60: {'Experience': 117772849, 'Next': 11009646},
             61: {'Experience': 128782495, 'Next': 12000515},
             62: {'Experience': 140783010, 'Next': 13080560},
             63: {'Experience': 153863570, 'Next': 14257811},
             64: {'Experience': 168121381, 'Next': 15541015},
             65: {'Experience': 183662396, 'Next': 16939705},
             66: {'Experience': 200602101, 'Next': 18464279},
             67: {'Experience': 219066380, 'Next': 20126064},
             68: {'Experience': 239192444, 'Next': 21937409},
             69: {'Experience': 261129853, 'Next': 23911777},
             70: {'Experience': 285041630, 'Next': 26063836},
             71: {'Experience': 311105466, 'Next': 28409582},
             72: {'Experience': 339515048, 'Next': 30966444},
             73: {'Experience': 370481492, 'Next': 33753424},
             74: {'Experience': 404234916, 'Next': 36791232},
             75: {'Experience': 441026148, 'Next': 40102443},
             76: {'Experience': 481128591, 'Next': 43711663},
             77: {'Experience': 524840254, 'Next': 47645713},
             78: {'Experience': 572485967, 'Next': 51933826},
             79: {'Experience': 624419793, 'Next': 56607872},
             80: {'Experience': 681027665, 'Next': 61702579},
             81: {'Experience': 742730244, 'Next': 67255812},
             82: {'Experience': 809986056, 'Next': 73308835},
             83: {'Experience': 883294891, 'Next': 79906630},
             84: {'Experience': 963201521, 'Next': 87098226},
             85: {'Experience': 1050299747, 'Next': 94937067},
             86: {'Experience': 1145236814, 'Next': 103481403},
             87: {'Experience': 1248718217, 'Next': 112794729},
             88: {'Experience': 1361512946, 'Next': 122946255},
             89: {'Experience': 1484459201, 'Next': 134011418},
             90: {'Experience': 1618470619, 'Next': 146072446},
             91: {'Experience': 1764543065, 'Next': 159218965},
             92: {'Experience': 1923762030, 'Next': 173548673},
             93: {'Experience': 2097310703, 'Next': 189168053},
             94: {'Experience': 2286478756, 'Next': 206193177},
             95: {'Experience': 2492671933, 'Next': 224750564},
             96: {'Experience': 2717422497, 'Next': 244978115},
             97: {'Experience': 2962400612, 'Next': 267026144},
             98: {'Experience': 3229426756, 'Next': 291058498},
             99: {'Experience': 3520485254, 'Next': 0}}


mon_type = {
    0x0: 'Regular',
    0x1: 'Mon_Other',    # Unused
    0x2: 'Superunique',  # Unused
    0x4: 'Champion',     # Unused
    0x8: 'Unique',
    0xA: 'Unique',       # 'Superunique'
    0xC: 'Champion',     # Possessed, Berserker, Fanatic as well
    0x10: 'Minion',
    0x20: 'Possessed',   # Unused
    0x40: 'Ghostly',     # Unused
    0x4C: 'Champion',    # 'Ghostly',
    0x80: 'Multishot',   # Unused
    0x108: 'Unique',     # 'Donno yet: Some unique mod, I think',
    0x10A: 'Unique',     # 'Donno yet: Some unique mod, I think'
}


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


def process_exists(process_name):
    return pymem.process.process_from_name(process_name) is not None


def one_of_processes_exists(process_names):
    try:
        processes = pymem.process.list_processes()
        names = [n.lower() for n in process_names]
        for process in processes:
            if process.szExeFile.decode('utf-8', errors='ignore').lower() in names:
                return True
        return False
    # Argument error causing an integer overflow in the pymem.process.list_processes() function every once in a while
    except ctypes.ArgumentError as e:
        logging.exception(e)
        return True


def number_of_processes_with_names(process_names, logging_level=None):
    processes = pymem.process.list_processes()
    names = [x.lower() for x in process_names]
    out = 0
    for p in processes:
        if p.szExeFile.decode('utf-8', errors='ignore').lower() in names:
            if logging_level == 'DEBUG':
                handle = pymem.process.open(p.th32ProcessID, debug=False, verbose=False)
                base_module = pymem.process.base_module(handle)
                logging.debug('Path of process: %s' % getattr(base_module, 'filename', b'NOT_FOUND').decode())
                pymem.process.close_handle(handle)
            out += 1
    return out


def translate_stat(histatid, lostatid, value, stat_map):
    stat_row = dict(stat_map[lostatid])
    if lostatid == 83:
        stat_row['Display'] = stat_mappings.CLASSSKILLS[histatid]
    elif lostatid in [97, 107]:
        stat_row['Display'] = stat_mappings.SKILLS[histatid]
    elif lostatid == 126:
        stat_row['Display'] = stat_mappings.ELEMENTALSKILLS.get(histatid, histatid)
    elif lostatid == 151:
        stat_row['Display'] = '%s Aura lvl' % stat_mappings.SKILLS[histatid]
    elif lostatid == 188:
        stat_row['Display'] = stat_mappings.SKILLTABS[histatid]
    elif lostatid == 195:
        stat_row['Display'] = 'Attack: %s (lvl %s)' % (stat_mappings.SKILLS[histatid // 64], histatid % 64)
    elif lostatid == 196:
        stat_row['Display'] = 'Kill: %s (lvl %s)' % (stat_mappings.SKILLS[histatid // 64], histatid % 64)
    elif lostatid == 197:
        stat_row['Display'] = 'Death: %s (lvl %s)' % (stat_mappings.SKILLS[histatid // 64], histatid % 64)
    elif lostatid == 198:
        stat_row['Display'] = 'Striking: %s (lvl %s)' % (stat_mappings.SKILLS[histatid // 64], histatid % 64)
    elif lostatid == 199:
        stat_row['Display'] = 'Level-Up: %s (lvl %s)' % (stat_mappings.SKILLS[histatid // 64], histatid % 64)
    elif lostatid == 201:
        stat_row['Display'] = 'Struck: %s (lvl %s)' % (stat_mappings.SKILLS[histatid // 64], histatid % 64)
    elif lostatid == 204:
        stat_row['Display'] = '%s (lvl %s)' % (stat_mappings.SKILLS[histatid // 64], histatid % 64)
        stat_row['value'] = '%s/%s' % (value % 256, value // 256)
    elif lostatid == 252:
        stat_row['Display'] = 'Repairs 1 durability in seconds'
        stat_row['value'] = str(100//value)
    else:
        stat_row['Display'] = stat_row['Abbr'] if stat_row['Abbr'] else stat_row['Name']

    if int(stat_row['ShowValue']) == 0:
        stat_row['value'] = ''
    else:
        if lostatid not in [204, 252]:
            stat_row['value'] = str(value / int(stat_row['Div']) * int(stat_row['Mul']))
            if stat_row['value'].endswith('.0'):
                stat_row['value'] = stat_row['value'][:-2]

        if int(stat_row['Perc']) == 1:
            stat_row['value'] += '%'

        if int(stat_row['Negate']) == 1:
            stat_row['value'] = '-' + stat_row['value']
    stat_row['histatid'] = histatid
    stat_row['lostatid'] = lostatid

    return stat_row


def group_and_hide_stats(stat_list):
    stat_list = group_one_stat('All Attributes', [0, 1, 2, 3], stat_list)
    stat_list = group_one_stat('All Res', [39, 41, 43, 45], stat_list)
    stat_list = group_one_stat('Min Dmg', [21, 23, 159], stat_list)
    stat_list = group_one_stat('Max Dmg', [22, 24, 160], stat_list)
    stat_list = group_one_stat('Min Dmg', [21, 159], stat_list)
    stat_list = group_one_stat('Max Dmg', [22, 160], stat_list)
    stat_list = group_one_stat('Enh Dmg', [17, 18], stat_list)

    stat_list = group_one_dmg_stat('Fire Damage', 48, 49, stat_list)
    stat_list = group_one_dmg_stat('Light Damage', 50, 51, stat_list)
    stat_list = group_one_dmg_stat('Magic Damage', 52, 53, stat_list)
    stat_list = group_one_dmg_stat('Cold Damage', 54, 55, stat_list)
    stat_list = group_psn_dmg(stat_list)
    stat_list = group_one_dmg_stat('Damage', 21, 22, stat_list)
    stat_list = group_one_dmg_stat('Two-hand Damage', 23, 24, stat_list)
    return [x for x in stat_list if int(x['Show']) == 1]


def group_one_stat(name, id_list, stat_list):
    attrs = False
    attr_val = None
    for stat_id in id_list:
        stat_list_row = next((x for x in stat_list if x['lostatid'] == stat_id), None)
        if stat_list_row is not None:
            if attr_val is None:
                attr_val = dict(stat_list_row)
            elif stat_list_row['value'] == attr_val['value']:
                attrs = True
            else:
                attrs = False
                break
        else:
            attrs = False
            break
    if attrs:
        out = [v for v in stat_list if v['lostatid'] not in id_list]
        tmp = attr_val
        tmp['Display'] = name
        out.append(tmp)
        return out
    else:
        return stat_list


def group_one_dmg_stat(name, min_dmg_id, max_dmg_id, stat_list):
    min_dmg_row = next((x for x in stat_list if x['lostatid'] == min_dmg_id), None)
    max_dmg_row = next((x for x in stat_list if x['lostatid'] == max_dmg_id), None)

    if min_dmg_row is not None and max_dmg_row is not None:
        out = [v for v in stat_list if v['lostatid'] not in [min_dmg_id, max_dmg_id]]
        tmp = dict(min_dmg_row)
        tmp['Display'] = name
        tmp['lostatid'] = 999
        if min_dmg_row['value'] == max_dmg_row['value']:
            tmp['value'] = min_dmg_row['value']
        else:
            tmp['value'] = min_dmg_row['value'] + '-' + max_dmg_row['value']
        out.append(tmp)
        return out
    else:
        return stat_list


def group_psn_dmg(stat_list):
    psn_dmg_min = next((x for x in stat_list if x['lostatid'] == 57), None)
    psn_dmg_max = next((x for x in stat_list if x['lostatid'] == 58), None)
    psn_len = next((x for x in stat_list if x['lostatid'] == 59), None)

    if psn_dmg_min is not None and psn_dmg_max is not None and psn_len is not None:
        out = [v for v in stat_list if v['lostatid'] not in [57, 58, 59]]
        tmp = dict(psn_dmg_min)
        tmp['Display'] = 'Psn Damage over %s secs' % (int(psn_len['value'])//25)
        tmp['lostatid'] = 999
        if psn_dmg_min['value'] == psn_dmg_max['value']:
            tmp['value'] = round(int(psn_dmg_min['value']) * int(psn_len['value']) / 256) // 1
        else:
            min_val = round(int(psn_dmg_min['value']) * int(psn_len['value']) / 256) // 1
            max_val = round(int(psn_dmg_max['value']) * int(psn_len['value']) / 256) // 1
            tmp['value'] = '%s-%s' % (min_val, max_val)
        out.append(tmp)
        return out
    else:
        return stat_list