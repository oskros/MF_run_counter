import requests
import json
import os
from copy import deepcopy

abs_file_path = os.path.dirname(__file__)
api_page = 'http://d2-holy-grail.herokuapp.com/api/grail/'
with open(abs_file_path + '/default_grail_data.json', 'r') as fo:
    default_data = json.load(fo)

with open(abs_file_path + '/default_eth_grail_data.json', 'r') as fo:
    default_eth_data = json.load(fo)


def get_grail(uid, proxies=None):
    try:
        req = requests.get(url=api_page + uid, proxies=proxies)
    except Exception as e:
        raise e
    req.raise_for_status()
    out = req.json()
    if out.get('data', None) is None:
        dd = deepcopy(default_data)
        del dd['runes']
        out['data'] = dd
    if out.get('ethData', None) is None:
        out['ethData'] = deepcopy(default_eth_data)
    return out


def update_grail_dict(dct, item_upg_dict):
    def update_items(_dct, _item_upg_dict):
        if not _item_upg_dict:
            return _dct
        for k, v in _dct.items():
            if k in _item_upg_dict:
                _dct[k].update({'wasFound': _item_upg_dict.pop(k)})
            elif isinstance(v, dict):
                _dct[k] = update_items(v, _item_upg_dict)
        return _dct

    # Deepcopy input nested dict to ensure original input is not changed
    dct = deepcopy(dct)

    # Holy grail app handles rainbow facets in a non-standard way compared to all other items, need to align with API
    for key in list(item_upg_dict):  # call "list" to make a copy of keys, since we pop them below
        if key.startswith('Rainbow Facet'):
            rbf = key.replace('(', '').replace(')', '').split(' ')
            dmg_type = rbf[2]
            activate_type = ' '.join(rbf[3:]).lower()
            dct['uniques']['other']['rainbow facet (jewel)'][activate_type][dmg_type] = {'wasFound': item_upg_dict.pop(key)}

    return update_items(dct, item_upg_dict)


def put_grail(uid, pwd, data, proxies=None):
    data['password'] = pwd
    data['grail'] = data['data']
    data['ethGrail'] = data['ethData']
    del data['data']
    del data['ethData']

    try:
        req = requests.put(url=api_page + uid, data=json.dumps(data), headers={"Content-Type": "application/json"}, proxies=proxies)
    except Exception as e:
        raise e
    req.raise_for_status()
    return req.status_code


def build_update_lst(dct, eth=False):
    def recursive_update_list(_dct):
        out = []
        for k, v in _dct.items():
            if k in ['Cold', 'Fire', 'Light', 'Poison']:
                continue
            if isinstance(v, dict):
                if v.get('wasFound', False):
                    out.append(k)
                else:
                    out += recursive_update_list(v)

        return out

    lst = recursive_update_list(dct)
    if not eth:
        for activate_type in ['die', 'level up']:
            for dmg_type in ['Cold', 'Fire', 'Light', 'Poison']:
                if dct['uniques']['other']['rainbow facet (jewel)'][activate_type][dmg_type].get('wasFound', False):
                    lst.append(f'Rainbow Facet ({dmg_type} {activate_type.title()})')

    return lst
