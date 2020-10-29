import json

pp = 'C:/users/g48606/desktop/personal/counter/profiles/plugy at.json'
gp = 'C:/users/g48606/desktop/personal/counter/profiles/grail.json'


with open(pp, 'r') as fo:
    prof = json.load(fo)

with open(gp, 'r') as fo:
    grail = json.load(fo)

for sess in prof:
    if sess in ['extra_data', 'active_state']:
        continue
    for run_no in prof[sess]['drops']:
        for i, run in enumerate(prof[sess]['drops'][run_no]):
            if isinstance(run, str):
                print(sess, run_no, run)
                continue
            i_name = run.get('item_name', None)
            if i_name is None:
                print("i_name is none", run)
            else:
                g_item = next((x for x in grail if x['Item'] == i_name), None)
                if g_item is None:
                    print("g_item is none", run)
                else:
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