import requests
import json
from copy import deepcopy

api_page = 'http://d2-holy-grail.herokuapp.com/api/grail/'


def get_grail(uid, proxies=None):
    try:
        req = requests.get(url=api_page + uid, proxies=proxies)
        if req.status_code == 200:
            return json.loads(req.content)
        else:
            raise requests.exceptions.RequestException("Failed to extract information from d2-holy-grail with status code code: %s" % req.status_code)
    except Exception as e:
        raise e


def update_grail_dict(dct, item_upg_dict):
    if not item_upg_dict:
        return dct
    for k, v in dct.items():
        if k in item_upg_dict:
            dct[k] = {'wasFound': item_upg_dict.pop(k)}
        elif isinstance(v, dict):
            dct[k] = update_grail_dict(v, item_upg_dict)
    return dct


def put_grail(uid, pwd, data, proxies=None):
    data['password'] = pwd
    data['grail'] = data['data']
    del data['data']
    del data['address']

    try:
        req = requests.put(url=api_page + uid, data=json.dumps(data).encode(), headers={"Content-Type": "application/json"}, proxies=proxies)
        if req.status_code != 200:
            raise requests.exceptions.RequestException("Failed to push updated information to d2-holy-grail, with status code code: %s" % req.status_code)
    except Exception as e:
        raise e
    return req.status_code


if __name__ == '__main__':
    p_addresses = None
    username = input('username')
    password = input('password')
    grail = get_grail(uid=username, proxies=p_addresses)
    updated_grail = update_grail_dict(dct=deepcopy(grail), item_upg_dict={'Stormshield': False, 'Shadow Dancer': False})
    put_grail(uid=username, pwd=password, data=updated_grail, proxies=p_addresses)