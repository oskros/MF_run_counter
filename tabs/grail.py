from init import *
from utils import tk_dynamic as tkd, tk_utils
from upcoming import herokuapp_controller
import tkinter as tk
from tkinter import ttk
import json
import requests
import csv
from tkinter import messagebox


class Grail(tkd.Frame):
    def __init__(self, main_frame, parent=None, **kw):
        tkd.Frame.__init__(self, parent, kw)
        self.main_frame = main_frame
        self.file_name = 'Profiles/grail.json'
        self.grail = self.load_grail()
        self.username = tk.StringVar(value=self.main_frame.herokuapp_username)
        self.password = tk.StringVar(value=self.main_frame.herokuapp_password)
        self.sync_drops = tk.IntVar()
        self.sync_herokuapp = tk.IntVar()
        self.vars_to_update = []

        self._make_widgets()
        self.update_statistics()

    def _make_widgets(self):
        bfr1 = tkd.LabelFrame(self, height=28)
        bfr1.propagate(False)
        bfr1.pack(expand=False, fill=tk.X, padx=1, pady=1)

        tkd.Button(bfr1, text='Sync', width=6, command=self.sync_local_grail, relief=tk.RIDGE, borderwidth=1).pack(side=tk.LEFT, padx=[1, 15], pady=1)
        tkd.Checkbutton(bfr1, text='Drops', variable=self.sync_drops).pack(side=tk.LEFT)
        tkd.Checkbutton(bfr1, text='Herokuapp', variable=self.sync_herokuapp).pack(side=tk.LEFT)

        bfr2 = tkd.Frame(self)
        bfr2.pack()
        tkd.Button(bfr2, text='Reset local grail', command=self.reset_grail).pack(pady=4, side=tk.LEFT)
        tkd.Button(bfr2, text='Upload to herokuapp', command=self.upload_to_herokuapp).pack(pady=4, side=tk.LEFT)

        browse_btn = tkd.Button(self, text='Browse grail', borderwidth=3, command=self.browse_grail)
        browse_btn.propagate(False)
        browse_btn.pack(side=tk.BOTTOM, fill=tk.X, padx=1, pady=1)

        descr = tkd.ListboxFrame(self)
        descr.propagate(False)
        # tk.Grid.rowconfigure(descr, 0, weight=1)
        tk.Grid.columnconfigure(descr, 0, weight=1)
        descr.pack(side=tk.BOTTOM, fill=tk.X, expand=False)
        for i, l in enumerate(['', 'Exist', 'Owned', 'Left', '%']):
            tkd.ListboxLabel(descr, text=l).grid(row=0, column=i)
        ttk.Separator(descr, orient=tk.HORIZONTAL).grid(row=1, column=0, columnspan=5, sticky='ew')
        # ttk.Separator(descr, orient=tk.VERTICAL).grid(row=0, column=1, rowspan=6, sticky='ns')
        self._make_row(descr, 2, 'Uniq Armor')
        self._make_row(descr, 3, 'Uniq Weapons')
        self._make_row(descr, 4, 'Uniq Other')
        self._make_row(descr, 5, 'Sets')
        self._make_row(descr, 6, 'Runes')
        self._make_row(descr, 7, 'Total')

    def _make_row(self, master, row, text):
        title_str = text.lower().replace(' ', '_')
        self.vars_to_update.append(title_str)
        setattr(self, 'exist_' + title_str, tk.StringVar(value='0'))
        setattr(self, 'owned_' + title_str, tk.StringVar(value='0'))
        setattr(self, 'remaining_' + title_str, tk.StringVar(value='0'))
        setattr(self, 'perc_' + title_str, tk.StringVar(value='0%'))

        tkd.ListboxLabel(master, text=text, justify=tk.LEFT).grid(sticky=tk.W, row=row, column=0)
        tkd.ListboxLabel(master, textvariable=getattr(self, 'exist_' + title_str)).grid(row=row, column=1)
        tkd.ListboxLabel(master, textvariable=getattr(self, 'owned_' + title_str)).grid(row=row, column=2)
        tkd.ListboxLabel(master, textvariable=getattr(self, 'remaining_' + title_str)).grid(row=row, column=3)
        tkd.ListboxLabel(master, textvariable=getattr(self, 'perc_' + title_str)).grid(row=row, column=4)

    def update_statistics(self):
        for v in self.vars_to_update:
            keys = ['Uniques' if x == 'uniq' else x.title() for x in v.split('_') if x != 'total']
            cond = {'Item Group ' + str(i): k for i, k in enumerate(keys)}
            count = self.count_grail(cond)
            # count = herokuapp_controller.count_items(reduce(operator.getitem, keys, self.grail))

            getattr(self, 'exist_' + v).set(count[0])
            getattr(self, 'owned_' + v).set(count[1])
            getattr(self, 'remaining_' + v).set(count[0] - count[1])
            getattr(self, 'perc_' + v).set(str(round(count[1] / count[0] * 100, 1)) + '%' if count[0] != 0 else '0.0%')

    def count_grail(self, conditions=None):
        if conditions is None:
            conditions = dict()

        tot = 0
        owned = 0
        for item in self.grail:
            if all(item.get(k, None) == v for k, v in conditions.items()):
                tot += 1
                if item.get('Found', False):
                    owned += 1

        return tot, owned

    def sync_local_grail(self):
        msg = 'Updated local grail file with:'
        if self.sync_herokuapp.get():
            self.get_grail_from_herokuapp()
            msg += '\n\n- Grail data from d2-holy-grail.herokuapp for user\n  "%s"' % self.username.get()
        if self.sync_drops.get():
            self.get_grail_from_drops()
            msg += '\n\n- Drops from all saved profiles'

        self.update_statistics()
        if self.sync_herokuapp.get() or self.sync_drops.get():
            messagebox.showinfo('Grail update', msg)
        else:
            messagebox.showerror('Grail update', 'No update choices selected')

    def reset_grail(self):
        resp = tk_utils.mbox(msg='Are you sure you want to reset the locally stored grail file?', title='WARNING')
        if resp:
            self.grail = self.create_empty_grail()
            self.update_statistics()

    def create_empty_grail(self):
        lib_path = os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), media_path + 'item_library.csv')
        with open(lib_path, 'r') as fo:
            grail_dict = [dict(row) for row in csv.DictReader(fo)]

        with open(self.file_name, 'w') as fo:
            json.dump(grail_dict, fo, indent=2)
        return grail_dict

    def load_grail(self):
        if not os.path.isfile(self.file_name):
            self.create_empty_grail()

        with open(self.file_name, 'r') as fo:
            state = json.load(fo)

        return state

    def save_grail(self):
        with open(self.file_name, 'w') as fo:
            json.dump(self.grail, fo, indent=2)

        self.main_frame.herokuapp_username = self.username.get()
        self.main_frame.herokuapp_password = self.password.get()

    def get_grail_from_drops(self):
        drops = []

        # Iterate through all saved profiles
        for p in self.main_frame.profiles:
            file = 'Profiles/%s.json' % p
            with open(file, 'r') as fo:
                state = json.load(fo)

            # Iterate through saved keys in each profile
            for key in state:
                # Active state for current profile should be fetched from drop tab, otherwise it might not be updated
                # as the active state is saved 1) every 30 seconds, 2) when profile is changed, 3) when app is closed
                if key == 'active_state' and p == self.main_frame.active_profile:
                    drops.extend(sum(self.main_frame.drops_tab.drops.values(), []))
                else:
                    drops.extend(sum(state[key].get('drops', dict()).values(), []))

        # Iterate through list of drops, ensuring compatibility with old profiles prior to version 1.1.2
        grail_items = [x['item_name'] for x in drops if isinstance(x, dict) and x.get('item_name', None) is not None]

        # Update grail items
        self.update_grail_from_list(grail_items)

    def update_grail_from_list(self, lst):
        for i, item in enumerate(self.grail):
            if item.get('Item', None) in lst:
                self.grail[i].update({'Found': True})

    def get_grail_from_herokuapp(self):
        resp = tk_utils.mebox(entries=['Username'], title='d2-holy-grail.herokuapp', defaults=[self.username.get()], masks=[None])
        if resp is None:
            return
        uid = resp[0]
        try:
            prox = self.main_frame.webproxies if isinstance(self.main_frame.webproxies, dict) else None
            herokuapp_grail = herokuapp_controller.get_grail(uid, proxies=prox)
        except requests.exceptions.HTTPError:
            messagebox.showerror('Username 404', "Username '%s' doesn't exist on d2-holy-grail.herokuapp.com" % uid)
            return

        self.username.set(uid)

        data = herokuapp_grail.get('data', dict())
        upd_lst = herokuapp_controller.build_update_lst(data)
        self.update_grail_from_list(lst=upd_lst)

    def upload_to_herokuapp(self):
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

        upd_dict = {x['Item']: True for x in self.grail if x.get('Found', None) is True}
        herokuapp_grail['data'] = herokuapp_controller.update_grail_dict(dct=herokuapp_grail['data'], item_upg_dict=upd_dict)

        try:
            herokuapp_controller.put_grail(uid=uid, pwd=pwd, data=herokuapp_grail, proxies=prox)
        except requests.exceptions.HTTPError:
            messagebox.showerror('Password 401', "Password incorrect for user '%s', try again" % uid)
            return

        self.username.set(uid)
        self.password.set(pwd)

        messagebox.showinfo('Success', 'Upload to "%s" on d2-holy-grail.herokuapp.com successful!' % uid)

    def browse_grail(self):
        window = tk.Toplevel()
        window.resizable(width=1, height=1)
        cols = ["Item", "Item Group 0", "Item Group 1", "Item Class", "Quality", "Rarity", "Class restriction",
                "Base Item", "TC", "QLVL", "Roll rarity", "Roll chance", "Found"]

        list_frame = tkd.Frame(window)
        vscroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        hscroll = ttk.Scrollbar(window, orient=tk.HORIZONTAL)
        tree = tkd.Treeview(list_frame, selectmode=tk.BROWSE, yscrollcommand=vscroll.set, xscrollcommand=hscroll.set, show='headings', columns=cols)#, activestyle='none', font=('courier', 10))
        hscroll.config(command=tree.xview)
        vscroll.config(command=tree.yview)

        vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        tree['columns'] = cols
        for col in cols:
            tree.column(col, stretch=tk.NO, minwidth=0, width=120)
            tree.heading(col, text=col, sort_by='num' if col in ['TC', 'QLVL', 'Roll rarity', 'Roll chance'] else 'name')

        for item in self.grail:
            tree.insert('', tk.END, values=list(item.values()))

    def treeview_sort_column(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        # reverse sort next time
        tv.heading(col, command=lambda: self.treeview_sort_column(tv, col, not reverse))