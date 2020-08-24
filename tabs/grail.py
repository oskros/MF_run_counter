from init import *
from utils import tk_dynamic as tkd, tk_utils
from upcoming import herokuapp_controller
import tkinter as tk
from tkinter import ttk
import json
import requests
from tkinter import messagebox


class Grail(tkd.Frame):
    def __init__(self, main_frame, parent=None, **kw):
        tkd.Frame.__init__(self, parent, kw)
        self.main_frame = main_frame
        self.file_name = 'Profiles/grail.json'
        self.grail = self.load_grail()
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.username.set(self.main_frame.herokuapp_username)
        self.password.set(self.main_frame.herokuapp_password)

        self.exist_unique_armor = tk.StringVar()
        self.owned_unique_armor = tk.StringVar()
        self.remaining_unique_armor = tk.StringVar()
        self.perc_unique_armor = tk.StringVar()
        self.exist_unique_weapons = tk.StringVar()
        self.owned_unique_weapons = tk.StringVar()
        self.remaining_unique_weapons = tk.StringVar()
        self.perc_unique_weapons = tk.StringVar()
        self.exist_unique_other = tk.StringVar()
        self.owned_unique_other = tk.StringVar()
        self.remaining_unique_other = tk.StringVar()
        self.perc_unique_other = tk.StringVar()
        self.exist_sets = tk.StringVar()
        self.owned_sets = tk.StringVar()
        self.remaining_sets = tk.StringVar()
        self.perc_sets = tk.StringVar()
        self.exist_total = tk.StringVar()
        self.owned_total = tk.StringVar()
        self.remaining_total = tk.StringVar()
        self.perc_total = tk.StringVar()

        self._make_widgets()
        self.update_statistics()

    def _make_widgets(self):
        tkd.Label(self, text='Update local grail').pack()
        bfr = tkd.Frame(self)
        bfr.pack()

        tkd.Button(bfr, text='From drops', command=self.get_from_drops).pack(side=tk.LEFT)
        tkd.Button(bfr, text='From herokuapp', command=self.download_herokuapp).pack(side=tk.LEFT)
        tkd.Button(bfr, text='Reset', command=self.reset_grail).pack(side=tk.LEFT)

        tkd.Label(self, text='Synchronization').pack()
        tkd.Button(self, text='Add to herokuapp', command=self.upload_herokuapp).pack()

        descr = tkd.ListboxFrame(self)
        # tk.Grid.rowconfigure(descr, 0, weight=1)
        # tk.Grid.columnconfigure(descr, 0, weight=1)
        descr.pack(side=tk.BOTTOM, fill=tk.X, expand=True)
        self._make_row(descr, 0, '', 'Exist', 'Owned', 'Left', '%', only_text=True)
        # ttk.Separator(descr, orient=tk.HORIZONTAL).grid(row=1, column=0, columnspan=6, sticky='ew')
        # ttk.Separator(descr, orient=tk.VERTICAL).grid(row=0, column=1, rowspan=7, sticky='ns')
        self._make_row(descr, 2, 'Uniq Armor', self.exist_unique_armor, self.owned_unique_armor, self.remaining_unique_armor, self.perc_unique_armor)
        self._make_row(descr, 3, 'Uniq Weapons', self.exist_unique_weapons, self.owned_unique_weapons, self.remaining_unique_weapons, self.perc_unique_weapons)
        self._make_row(descr, 4, 'Uniq Other', self.exist_unique_other, self.owned_unique_other, self.remaining_unique_other, self.perc_unique_other)
        self._make_row(descr, 5, 'Sets', self.exist_sets, self.owned_sets, self.remaining_sets, self.perc_sets)
        self._make_row(descr, 6, 'Total', self.exist_total, self.owned_total, self.remaining_total, self.perc_total)

    @staticmethod
    def _make_row(master, row, title, exist, owned, remaining, perc, only_text=False):
        tkd.ListboxLabel(master, text=title, justify=tk.LEFT).grid(sticky=tk.W, row=row, column=0)
        if only_text:
            tkd.ListboxLabel(master, text=exist).grid(row=row, column=2)
            tkd.ListboxLabel(master, text=owned).grid(row=row, column=3)
            tkd.ListboxLabel(master, text=remaining).grid(row=row, column=4)
            tkd.ListboxLabel(master, text=perc).grid(row=row, column=5)
        else:
            tkd.ListboxLabel(master, textvariable=exist).grid(row=row, column=2)
            tkd.ListboxLabel(master, textvariable=owned).grid(row=row, column=3)
            tkd.ListboxLabel(master, textvariable=remaining).grid(row=row, column=4)
            tkd.ListboxLabel(master, textvariable=perc).grid(row=row, column=5)

    def reset_grail(self):
        resp = tk_utils.mbox(msg='Are you sure you want to reset the locally stored grail file?', title='WARNING')
        if resp:
            self.grail = self.load_grail(reset_grail=True)
            self.update_statistics()

    def create_empty_grail(self):
        grail_dict = herokuapp_controller.default_data
        with open(self.file_name, 'w') as fo:
            json.dump(grail_dict, fo, indent=2)

    def load_grail(self, reset_grail=False):
        if not os.path.isfile(self.file_name) or reset_grail:
            self.create_empty_grail()

        with open(self.file_name, 'r') as fo:
            state = json.load(fo)

        return state

    def save_grail(self):
        with open(self.file_name, 'w') as fo:
            json.dump(self.grail, fo, indent=2)

        self.main_frame.herokuapp_username = self.username.get()
        self.main_frame.herokuapp_password = self.password.get()

    def count_items(self, dct):
        tot, owned = 0, 0
        for k in dct.keys():
            if isinstance(dct[k], dict) and dct[k] and 'wasFound' not in dct[k]:
                tmp = self.count_items(dct[k])
                tot += tmp[0]
                owned += tmp[1]
            else:
                tot += 1
                if dct[k].get('wasFound', False):
                    owned += 1
        return tot, owned

    def owned_items(self):
        my_items = []
        def add_items(dct):
            for k in dct:
                if k in ['Cold', 'Fire', 'Light', 'Poison']:
                    continue
                if isinstance(dct[k], dict) and dct[k] and 'wasFound' not in dct[k]:
                    add_items(dct[k])
                elif dct[k].get('wasFound', False):
                    my_items.append(k)
        add_items(self.grail)

        for activate_type in ['die', 'level up']:
            for dmg_type in ['Cold', 'Fire', 'Light', 'Poison']:
                if self.grail['uniques']['other']['rainbow facet (jewel)'][activate_type][dmg_type].get('wasFound', False):
                    my_items.append('Rainbow Facet (%s %s)' % (dmg_type, activate_type.title()))
        return my_items

    def update_statistics(self):
        ua = self.count_items(self.grail['uniques']['armor'])
        self.exist_unique_armor.set(ua[0])
        self.owned_unique_armor.set(ua[1])
        self.remaining_unique_armor.set(ua[0] - ua[1])
        self.perc_unique_armor.set(str(round(ua[1]/ua[0]*100, 1)) + '%' if ua[0] != 0 else '0.0%')

        uw = self.count_items(self.grail['uniques']['weapons'])
        self.exist_unique_weapons.set(uw[0])
        self.owned_unique_weapons.set(uw[1])
        self.remaining_unique_weapons.set(uw[0] - uw[1])
        self.perc_unique_weapons.set(str(round(uw[1]/uw[0]*100, 1)) + '%' if uw[0] != 0 else '0.0%')

        uo = self.count_items(self.grail['uniques']['other'])
        self.exist_unique_other.set(uo[0])
        self.owned_unique_other.set(uo[1])
        self.remaining_unique_other.set(uo[0] - uo[1])
        self.perc_unique_other.set(str(round(uo[1]/uo[0]*100, 1)) + '%' if uo[0] != 0 else '0.0%')

        s = self.count_items(self.grail['sets'])
        self.exist_sets.set(s[0])
        self.owned_sets.set(s[1])
        self.remaining_sets.set(s[0] - s[1])
        self.perc_sets.set(str(round(s[1]/s[0]*100, 1)) + '%' if s[0] != 0 else '0.0%')

        t = self.count_items(self.grail)
        self.exist_total.set(t[0])
        self.owned_total.set(t[1])
        self.remaining_total.set(t[0] - t[1])
        self.perc_total.set(str(round(t[1]/t[0]*100, 1)) + '%' if t[0] != 0 else '0.0%')

    def get_from_drops(self):
        drops = []
        for p in self.main_frame.profiles:
            file = 'Profiles/%s.json' % p
            with open(file, 'r') as fo:
                state = json.load(fo)

            for key in state:
                if key == 'extra_data':
                    continue
                elif key == 'active_state' and p == self.main_frame.active_profile:
                    drops.extend(sum(self.main_frame.drops_tab.drops.values(), []))
                else:
                    drops.extend(sum(state[key]['drops'].values(), []))

        grail_items = {x['item_name']: True for x in drops if isinstance(x, dict) and x.get('item_name', None) is not None}
        print(grail_items)
        self.grail = herokuapp_controller.update_grail_dict(self.grail, grail_items)
        self.update_statistics()

    def download_herokuapp(self):
        resp = tk_utils.mebox(entries=['Username', 'Password'], title='d2-holy-grail.herokuapp', defaults=[self.username.get(), self.password.get()], masks=[None, "*"])
        if resp is None:
            return
        uid, pwd = resp
        try:
            prox = self.main_frame.webproxies if isinstance(self.main_frame.webproxies, dict) else None
            herokuapp_grail = herokuapp_controller.get_grail(uid, proxies=prox)
        except requests.exceptions.HTTPError:
            messagebox.showerror('Username 404', "Username '%s' doesn't exist on d2-holy-grail.herokuapp.com" % uid)
            return

        self.username.set(uid)
        self.password.set(pwd)

        data = herokuapp_grail.get('data', dict())
        upd_dict = {x: True for x in herokuapp_controller.build_update_list(data)}
        for activate_type in ['die', 'level up']:
            for dmg_type in ['Cold', 'Fire', 'Light', 'Poison']:
                if data['uniques']['other']['rainbow facet (jewel)'][activate_type][dmg_type].get('wasFound', False):
                    upd_dict.update({'Rainbow Facet (%s %s)' % (dmg_type, activate_type.title()): True})
        self.grail = herokuapp_controller.update_grail_dict(self.grail, upd_dict)
        self.update_statistics()

    def upload_herokuapp(self):
        resp = tk_utils.mebox(entries=['Username', 'Password'], title='d2-holy-grail.herokuapp', defaults=[self.username.get(), self.password.get()], masks=[None, "*"])
        if resp is None:
            return
        uid, pwd = resp
        try:
            prox = self.main_frame.webproxies if isinstance(self.main_frame.webproxies, dict) else None
            herokuapp_grail = herokuapp_controller.get_grail(uid, proxies=prox)
        except requests.exceptions.HTTPError:
            messagebox.showerror('Username 404', "Username '%s' doesn't exist on d2-holy-grail.herokuapp.com" % uid)
            return

        upd_dict = {x: True for x in self.owned_items()}
        herokuapp_grail['data'] = herokuapp_controller.update_grail_dict(dct=herokuapp_grail['data'], item_upg_dict=upd_dict)

        try:
            herokuapp_controller.put_grail(uid=uid, pwd=pwd, data=herokuapp_grail, proxies=prox)
        except requests.exceptions.HTTPError:
            messagebox.showerror('Password 401', "Password incorrect for user '%s', try again" % uid)

        self.username.set(uid)
        self.password.set(pwd)

        messagebox.showinfo('Success', "Upload to '%s' on d2-holy-grail.herokuapp.com successful!" % uid)
