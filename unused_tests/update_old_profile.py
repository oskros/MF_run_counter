import json
import re
from utils.item_name_lists import FULL_ITEM_LIST, ITEM_ALIASES, ETH_ITEM_LIST


def detect_iname(inp):
    wrds = inp.split(' ')
    if wrds[0] == '(*)':
        wrds = wrds[1:]
        prefix = '(*)'
    else:
        prefix = ''

    for i in range(len(wrds), 0, -1):
        is_eth = wrds[0].lower() == 'eth' and 'rune' not in [x.lower() for x in wrds]
        if is_eth:
            sub = ' '.join(wrds[1:][:i])
        else:
            sub = ' '.join(wrds[:i])
        rem = ' '.join(wrds[i:])
        if is_eth:
            rem = ('Eth ' + rem).strip()
        candidates = list(comparison(sub, eth=is_eth))

        if candidates:
            print('Input: %s' % inp)
            for idx, c in enumerate(candidates):
                print('\t [%s]: %s' % (idx, c))
            print('\t[-1]: <TRY FEWER WORDS>')
            print('\t[-2]: <SKIP>')
            choice = provide_choice(-2, len(candidates))
            if choice == -2:
                return {'item_name': None, 'input': inp, 'extra': ""}
            elif choice >= 0:

                if rem:
                    print('Keep extra: %s\n\t[0]: NO\n\t[1]: YES\n\t[2]: MANUAL INPUT' % rem)
                    inp = provide_choice(0, 3)
                    if inp == 0:
                        rem = ''
                    elif inp == 2:
                        rem = input('Manual input (extra): ')
                fin_out = {'item_name': candidates[choice], 'input': ' '.join([prefix, candidates[choice], rem]).strip(), 'extra': rem}
                if is_eth:
                    fin_out['eth'] = True
                return fin_out
    print('Failed to recognize input: <<< %s >>>' % inp)
    man = input('Type manual input or press <ENTER> to IGNORE and continue: ')
    if man == "":
        return {'item_name': None, 'input': inp, 'extra': ""}
    else:
        return detect_iname(man)


def provide_choice(min_n, max_n, invalid=False):
    msg = 'Invalid choice - select input: ' if invalid else 'Select input: '
    choice = input(msg)
    try:
        choice = int(choice)
        assert choice in range(min_n, max_n)
    except (ValueError, AssertionError):
        choice = provide_choice(min_n, max_n, invalid=True)
    return choice


def comparison(var, eth=False):
    out = set()
    # regex to append a [']? after all letters, which is an optional argument for adding a hyphen
    # this means that for example typing in "mavinas" and "m'avina's" will yield the same results
    hyphen_escape = re.sub('([^a-zA-Z]*)', "\\1[']?", re.escape(var))
    # encapsulating with \b ensures that searches are done only at the start of each word
    # ".*" allows anything to follow after the already typed letters
    pattern = re.compile(r"\b" + hyphen_escape + r".*\b", flags=re.IGNORECASE)

    for w in FULL_ITEM_LIST + list(ITEM_ALIASES.keys()):
        if re.search(pattern, w):
            # Append true entry from the alias list - if none are found, add the match from original list
            i_name = ITEM_ALIASES.get(w, w)
            if eth:
                if i_name in ETH_ITEM_LIST:
                    out.add(i_name)
            else:
                out.add(i_name)
    return sorted(out)


if __name__ == '__main__':
    import os
    pp = os.path.join(os.path.abspath('..'), 'Profiles/PlugY LK.json')
    gp = os.path.join(os.path.abspath('..'), 'Profiles/grail.json')

    with open(pp, 'r') as fo:
        prof = json.load(fo)

    with open(gp, 'r') as fo:
        grail = json.load(fo)

    for sess in prof:
        if sess in ['extra_data']:
            continue
        for run_no in prof[sess]['drops']:
            for i, run in enumerate(prof[sess]['drops'][run_no]):
                detected = None
                if isinstance(run, str):
                    detected = detect_iname(run)
                    if detected['item_name'] is not None:
                        print("Successfully detected i_name in item library\n\told: %s\n\tnew: %s" % (run, detected))
                    else:
                        print("Failed to detect i_name in item library\n\told: %s\n\tnew: %s" % (run, detected))
                    run = detected
                    prof[sess]['drops'][run_no][i] = detected

                if detected is None and run.get('item_name', None) is None:
                    detected = detect_iname(run.get('input', ""))
                    if detected['item_name'] is not None:
                        print("Successfully detected i_name in item library\n\told: %s\n\tnew: %s" % (run, detected))
                    else:
                        print("Failed to detect i_name in item library\n\told: %s\n\tnew: %s" % (run, detected))
                    run = detected
                    prof[sess]['drops'][run_no][i] = detected

                g_item = next((x for x in grail if x['Item'] == run.get('item_name', None)), None)
                if g_item is None:
                    if run.get('item_name', None) is not None:
                        print("%s: Couldn't find [%s] in item library" % (run, run.get('item_name', None)))
                    if detected is not None:
                        print('')
                elif 'TC' not in run:
                    print('Updating item info (TC, QLVL, Item Class, Grailer) for %s' % run.get('item_name', None))
                    if detected is not None:
                        print('')
                    prof[sess]['drops'][run_no][i]['TC'] = g_item['TC']
                    prof[sess]['drops'][run_no][i]['QLVL'] = g_item['QLVL']
                    prof[sess]['drops'][run_no][i]['Item Class'] = g_item['Item Class']
                    if run.get('input', '').startswith('(*)'):
                        grailer = "True"
                    else:
                        grailer = "False"
                    prof[sess]['drops'][run_no][i]['Grailer'] = grailer

    with open(pp, 'w') as fo:
        json.dump(prof, fo, indent=2)