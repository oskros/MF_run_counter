from init import *
from utils import tk_dynamic as tkd, tk_utils, herokuapp_controller, other_utils
from utils.color_themes import Theme
from utils.item_name_lists import ETH_ITEM_LIST
import tkinter as tk
from tkinter import ttk
import json
import requests
import csv
import win32gui
from tkinter import messagebox


class Grail(tkd.Frame):
    def __init__(self, main_frame, parent=None, **kw):
        tkd.Frame.__init__(self, parent, kw)
        self.main_frame = main_frame
        self.file_name = 'Profiles/grail.json'
        self.show_eth_grail = tk.IntVar(value=0)
        self.grail = self.load_grail()
        self.username = tk.StringVar(value=self.main_frame.herokuapp_username)
        self.password = tk.StringVar(value=self.main_frame.herokuapp_password)
        self.sync_drops = tk.IntVar()
        self.sync_herokuapp = tk.IntVar()
        self.reset_local_grail = tk.IntVar()
        self.vars_to_update = []
        self.cols = ["Item", "Base Item", "Item Class", "Quality", "Rarity", "Class restriction", "TC", "QLVL",
                     "Roll rarity", "Roll chance", "Drop Andariel", "Drop Mephisto", "Drop Diablo", "Drop Pindleskin",
                     "Found", "FoundEth"]
        self.grail_table_open = False

        self._make_widgets()
        self.update_statistics()

    def _make_widgets(self):
        bfr1 = tkd.LabelFrame(self, height=28)
        bfr1.propagate(False)
        bfr1.pack(expand=False, fill=tk.X, padx=1, pady=1)

        tkd.Button(bfr1, text='Sync', width=6, command=self.sync_local_grail, relief=tk.RIDGE, borderwidth=1, tooltip='Updates your local grail to include items logged either\nin your profiles or on herokuapp').pack(side=tk.LEFT, padx=[1, 15], pady=1)
        tkd.Checkbutton(bfr1, text='Profiles', variable=self.sync_drops).pack(side=tk.LEFT)
        tkd.Checkbutton(bfr1, text='Herokuapp', variable=self.sync_herokuapp).pack(side=tk.LEFT)

        bfr2 = tkd.Frame(self)
        bfr2.pack(pady=12, expand=True, fill=tk.X)
        tkd.Button(bfr2, text='Upload grail to herokuapp', command=self.upload_to_herokuapp, borderwidth=3, tooltip='This will not delete already found items on herokuapp if they are not\nin your local grail, but only add new items').pack(padx=8, side=tk.LEFT, fill=tk.X, expand=True)

        bfr3 = tkd.Frame(self)
        bfr3.pack(side=tk.BOTTOM, expand=tk.YES, fill=tk.X)
        tkd.Button(bfr3, text='Item table', borderwidth=3, command=self.open_grail_table, width=1).pack(side=tk.LEFT, fill=tk.X, padx=[1, 0], pady=1, expand=tk.YES)
        tkd.Button(bfr3, text='Grail controller', borderwidth=3, command=self.open_grail_controller, width=1).pack(side=tk.LEFT, fill=tk.X, padx=1, pady=1, expand=tk.YES)

        descr = tkd.ListboxFrame(self)
        # descr.propagate(False)
        tk.Grid.columnconfigure(descr, 0, weight=1)
        tk.Grid.columnconfigure(descr, 1, weight=1)
        tk.Grid.columnconfigure(descr, 2, weight=1)
        tk.Grid.columnconfigure(descr, 3, weight=1)
        descr.pack(side=tk.BOTTOM, fill=tk.X, expand=True)
        tkd.EthGrailCheckbutton(descr, text='Eth grail', font=('Segoe UI', 9), variable=self.show_eth_grail, command=self.update_statistics).grid(row=0, column=0, sticky=tk.W)
        for i, l in enumerate(['Exist', 'Left', '%    '], 1):
            tkd.ListboxLabel(descr, text=l, font=('Segoe UI', 9, 'bold')).grid(row=0, column=i, sticky=tk.E)
        ttk.Separator(descr, orient=tk.HORIZONTAL).grid(row=1, column=0, columnspan=4, sticky='ew')
        self._make_row(descr, 2, 'Uniq Armor')
        self._make_row(descr, 3, 'Uniq Weapons')
        self._make_row(descr, 4, 'Uniq Other')
        self._make_row(descr, 5, 'Sets')
        self._make_row(descr, 6, 'Runes')
        self._make_row(descr, 7, 'Total', font=('Segoe UI', 9, 'bold'))

    def _make_row(self, master, row, text, **kwargs):
        font = kwargs.pop('font', ('Segoe UI', 9))
        title_str = text.lower().replace(' ', '_')
        self.vars_to_update.append(title_str)
        setattr(self, 'exist_' + title_str, tk.StringVar(value='0'))
        setattr(self, 'remaining_' + title_str, tk.StringVar(value='0'))
        setattr(self, 'perc_' + title_str, tk.StringVar(value='0%'))

        tkd.ListboxLabel(master, text=text, justify=tk.LEFT, font=font).grid(sticky=tk.W, row=row, column=0)
        tkd.ListboxLabel(master, textvariable=getattr(self, 'exist_' + title_str), font=font, justify=tk.RIGHT).grid(row=row, column=1, sticky=tk.E)
        tkd.ListboxLabel(master, textvariable=getattr(self, 'remaining_' + title_str), font=font, justify=tk.RIGHT).grid(row=row, column=2, sticky=tk.E)
        tkd.ListboxLabel(master, textvariable=getattr(self, 'perc_' + title_str), font=font, justify=tk.RIGHT).grid(row=row, column=3, sticky=tk.E)

    def update_statistics(self, eth=None):
        if eth is None:
            eth = self.show_eth_grail.get()
        else:
            self.show_eth_grail.set(int(eth))
        for v in self.vars_to_update:
            keys = [] if v == 'total' else [v.replace('_', ' ').replace('uniq', 'Unique').title()]
            cond = {'Item Group ' + str(i): k for i, k in enumerate(keys)}
            count = self.count_grail(cond, eth)

            getattr(self, 'exist_' + v).set(count[0])
            getattr(self, 'remaining_' + v).set(count[0] - count[1])
            getattr(self, 'perc_' + v).set(str(round(count[1] / count[0] * 100, 1)) + '%' if count[0] != 0 else '0.0%')

    def count_grail(self, conditions=None, eth=False):
        if conditions is None:
            conditions = dict()

        tot = 0
        owned = 0
        for item in self.grail:
            if all(item.get(k, None) == v for k, v in conditions.items()):
                if eth:
                    if item.get('Item', '') in ETH_ITEM_LIST:
                        tot += 1
                        if item.get('FoundEth', False):
                            owned += 1
                else:
                    tot += 1
                    if item.get('Found', False):
                        owned += 1

        return tot, owned

    def sync_local_grail(self):
        item_lst = []
        msg = 'Updated local grail file with:'
        if self.sync_herokuapp.get():
            resp = tk_utils.mebox(entries=['Username'], title='d2-holy-grail.herokuapp', defaults=[self.username.get()], masks=[None])
            if resp:
                uid = resp[0]
                heroku_grail, heroku_ethgrail = self.get_grail_from_herokuapp(uid)
                self.update_grail_from_list(heroku_ethgrail, eth=True)
                item_lst.extend(heroku_grail)
                msg += '\n\n- Grail data from d2-holy-grail.herokuapp for user\n  "%s"' % self.username.get()
        if self.sync_drops.get():
            item_lst.extend(self.get_grail_from_drops())
            msg += '\n\n- Drops from all saved profiles'

        if item_lst:
            self.update_grail_from_list(item_lst)
            self.update_statistics()
            if self.grail_table_open:
                self.select_from_filters()
            messagebox.showinfo('Grail update', msg)
        else:
            messagebox.showerror('Grail update', 'No update choices selected')

    def reset_grail(self):
        resp = tk_utils.mbox(msg='Are you sure you want to reset the locally stored grail file?', title='WARNING', disabled_btn_input='DELETE')
        if resp == 'DELETE':
            self.grail = self.create_empty_grail()
            self.update_statistics()
            if self.grail_table_open:
                self.select_from_filters()
            for var in dir(self):
                if var.startswith('grail_item'):
                    getattr(self, var).set(0)

    def create_empty_grail(self):
        with open(media_path + 'item_library.csv', 'r') as fo:
            grail_dict = [{**row, 'Found': False, 'FoundEth': False} if row['Item'] in ETH_ITEM_LIST else {**row, 'Found': False} for row in csv.DictReader(fo)]

        other_utils.atomic_json_dump(self.file_name, grail_dict)
        return grail_dict

    def load_grail(self):
        if not os.path.isfile(self.file_name):
            self.create_empty_grail()

        with open(self.file_name, 'r') as fo:
            state = json.load(fo)

        return state

    def save_grail(self):
        other_utils.atomic_json_dump(self.file_name, self.grail)

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
        return grail_items

    def update_grail_from_list(self, lst, eth=False):
        update_key = 'FoundEth' if eth else 'Found'
        for i, item in enumerate(self.grail):
            if item.get('Item', None) in lst:
                self.grail[i].update({update_key: True})
                if not eth:
                    if hasattr(self, 'grail_item_' + item.get('Item', '').replace("'", "1").replace(' ', '_')):
                        getattr(self, 'grail_item_' + item.get('Item', '').replace("'", "1").replace(' ', '_')).set(1)

    def update_grail_from_name(self, name):
        for i, item in enumerate(self.grail):
            if item.get('Item', None) == name:
                found_value = not item.get('Found', False)
                self.grail[i].update({'Found': found_value})
                self.update_statistics()
                if self.grail_table_open:
                    self.select_from_filters()
                return

    def update_grail_from_index(self, idx):
        self.grail[idx].update({'Found': True})
        self.update_statistics()
        if self.grail_table_open:
            self.select_from_filters()
        if hasattr(self, 'grail_item_' + self.grail[idx]['Item'].replace("'", "1").replace(' ', '_')):
            getattr(self, 'grail_item_' + self.grail[idx]['Item'].replace("'", "1").replace(' ', '_')).set(1)

    def get_grail_from_herokuapp(self, uid):
        try:
            prox = self.main_frame.webproxies if isinstance(self.main_frame.webproxies, dict) else None
            herokuapp_grail = herokuapp_controller.get_grail(uid, proxies=prox)
        except requests.exceptions.HTTPError:
            messagebox.showerror('Username 404', "Username '%s' doesn't exist on d2-holy-grail.herokuapp.com" % uid)
            return

        self.username.set(uid)

        data = herokuapp_grail.get('data', dict())
        eth_data = herokuapp_grail.get('ethData', dict())
        upd_lst = herokuapp_controller.build_update_lst(data)
        eth_lst = herokuapp_controller.build_update_lst(eth_data, eth=True)
        return upd_lst, eth_lst

    def upload_to_herokuapp(self, upd_dict=None, show_confirm=True, pop_up_msg=None, pop_up_title='d2-holy-grail.herokuapp', eth_dict=None):
        resp = tk_utils.mebox(entries=['Username', 'Password'], title=pop_up_title, defaults=[self.username.get(), self.password.get()], masks=[None, "*"], msg=pop_up_msg)
        if resp is None:
            return None
        uid, pwd = resp
        try:
            prox = self.main_frame.webproxies if isinstance(self.main_frame.webproxies, dict) else None
            herokuapp_grail = herokuapp_controller.get_grail(uid, proxies=prox)
        except requests.exceptions.HTTPError:
            messagebox.showerror('Username 404', "Username '%s' doesn't exist on d2-holy-grail.herokuapp.com. Try again" % uid)
            return self.upload_to_herokuapp(upd_dict=upd_dict, show_confirm=show_confirm, pop_up_msg=pop_up_msg, pop_up_title=pop_up_title)

        if upd_dict is None and eth_dict is None:
            upd_dict = {x['Item']: True for x in self.grail if x.get('Found', None) is True}
            eth_dict = {x['Item']: True for x in self.grail if x.get('FoundEth', None) is True}
        if upd_dict is not None:
            herokuapp_grail['data'] = herokuapp_controller.update_grail_dict(dct=herokuapp_grail['data'], item_upg_dict=upd_dict)
        if eth_dict is not None:
            herokuapp_grail['ethData'] = herokuapp_controller.update_grail_dict(dct=herokuapp_grail['ethData'], item_upg_dict=eth_dict)

        try:
            herokuapp_controller.put_grail(uid=uid, pwd=pwd, data=herokuapp_grail, proxies=prox)
        except requests.exceptions.HTTPError:
            messagebox.showerror('Password 401', "Password incorrect for user '%s', try again" % uid)
            return self.upload_to_herokuapp(upd_dict=upd_dict, show_confirm=show_confirm, pop_up_msg=pop_up_msg, pop_up_title=pop_up_title)

        self.username.set(uid)
        self.password.set(pwd)

        if show_confirm:
            messagebox.showinfo('Success', 'Upload to "%s" on d2-holy-grail.herokuapp.com successful!' % uid)
        return True

    def open_grail_controller(self):
        def rec_checkbox_add(master, frame, dct, rows=4, depth=None):
            # Default arguments cannot be mutable
            if depth is None:
                depth = []

            # Init count to determine number of rows before adding a new column
            cnt = 0
            for k, v in dct.items():
                # Bottom of tree nodes are either empty dicts or has the 'wasFound' key
                if v == dict() or 'wasFound' in v:
                    found = v.get('wasFound', False)

                    # Due to weird handling of rainbow facets in herokuapp, we utilise the saved stack of keys (in the
                    # 'depth' variable) to determine the appropriate item name
                    if k in ['Cold', 'Fire', 'Light', 'Poison']:
                        i_name = 'Rainbow Facet (%s %s)' % (k, depth[-1].title())
                        var_name = 'grail_item_' + i_name.replace("'", "1").replace(' ', '_')
                    else:
                        # Replace characters that cannot be used in variable names
                        var_name = 'grail_item_' + k.replace("'", "1").replace(' ', '_')
                        i_name = k

                    # Define an IntVar as a class attribute that we can later call when needed. Then build the
                    # checkbutton, noting that the lambda needs to be passed a default argument, otherwise it will
                    # overwrite its own definition at each iteration
                    setattr(master, var_name, tk.IntVar(value=found))
                    tkd.Checkbutton(frame, text=k, variable=getattr(master, var_name), command=lambda _k=i_name: master.update_grail_from_name(_k)).pack(expand=True, anchor=tk.W)
                # We are not at the bottom of tree node, thus we will create a child node and call recursively
                else:
                    # When at top node, determine if a new column should be made or not, based on number of rows
                    if len(depth) == 0:
                        if cnt % rows == 0:
                            topframe = tkd.Frame(frame)
                            topframe.pack(side=tk.LEFT, expand=True, anchor=tk.NW)
                        new_frame = tkd.Frame(topframe)
                        new_frame.pack(side=tk.TOP, expand=True, anchor=tk.NW, fill=tk.Y, pady=[0, 30])
                        cnt += 1
                    else:
                        new_frame = tkd.Frame(frame)
                        new_frame.pack(side=tk.LEFT, expand=True, anchor=tk.N)

                    # .title() function bugs out with apostrophes. Handle the specific issues hardcoded here
                    # Also, there is a spelling mistake in herokuapp that we fix: Hsaru's -> Hsarus'
                    txt = k.title().replace("'S", "'s").replace("'A", "'a").replace("Hsaru's", "Hsarus'")
                    tkd.Label(new_frame, text=txt, font='Arial 15 bold').pack(expand=True, anchor=tk.N)
                    rec_checkbox_add(master, new_frame, v, rows, depth + [k])

        # We dont allow more than one open window of the grail controller
        if win32gui.FindWindow(None, 'Grail controller'):
            return

        if self.show_eth_grail.get():
            messagebox.showinfo('Eth grail', 'Grail controller cannot be used to modify your eth grail as of right now.\nInstead you can do this on herokuapp, and then sync to the application afterwards')
            self.update_statistics(eth=False)

        # Initialise the TopLevel window (important we use TopLevel instead of Tk, to pass over information between
        # the defined widgets and the main app)
        window = tkd.Toplevel()
        window.title('Grail controller')
        window.resizable(True, True)
        window.iconbitmap(media_path + 'icon.ico')

        # Build nested dict with information from the current grail
        upd_dict = {x['Item']: True for x in self.grail if x.get('Found', None) is True}
        nested_grail = herokuapp_controller.update_grail_dict(dct=herokuapp_controller.default_data, item_upg_dict=upd_dict)

        tabcontrol = ttk.Notebook(window)
        tabcontrol.pack(expand=True, fill=tk.BOTH)

        # Build the new tabs
        unique_armor = tkd.Frame(tabcontrol)
        unique_weapons = tkd.Frame(tabcontrol)
        unique_other = tkd.Frame(tabcontrol)
        sets = tkd.Frame(tabcontrol)
        runes = tkd.Frame(tabcontrol)

        tabcontrol.add(unique_armor, text='Unique Armor')
        tabcontrol.add(unique_weapons, text='Unique Weapons')
        tabcontrol.add(unique_other, text='Unique Other')
        tabcontrol.add(sets, text='Sets')
        tabcontrol.add(runes, text='Runes')

        rec_checkbox_add(self, unique_armor, nested_grail['uniques']['armor'], 3)
        rec_checkbox_add(self, unique_weapons, nested_grail['uniques']['weapons'], 4)
        rec_checkbox_add(self, unique_other, nested_grail['uniques']['other'], 3)
        rec_checkbox_add(self, sets, nested_grail['sets'], 5)
        rec_checkbox_add(self, runes, nested_grail['runes'], 1)

        # Make sure to update the theme for the newly created widgets
        theme = Theme(self.main_frame.active_theme)
        theme.update_colors()

    def open_grail_table(self):
        if win32gui.FindWindow(None, 'Item table'):
            return
        window = tk.Toplevel()
        window.title('Item table')
        window.state('zoomed')
        window.resizable(True, True)
        window.iconbitmap(media_path + 'icon.ico')
        window.protocol("WM_DELETE_WINDOW", lambda: self.close_grail_table(window))

        tree_frame = tkd.Frame(window)
        vscroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        hscroll = ttk.Scrollbar(window, orient=tk.HORIZONTAL)
        self.tree = tkd.Treeview(tree_frame, selectmode=tk.BROWSE, yscrollcommand=vscroll.set, xscrollcommand=hscroll.set, show='headings', columns=self.cols)
        hscroll.config(command=self.tree.xview)
        vscroll.config(command=self.tree.yview)

        combofr = tkd.Frame(tree_frame)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        combofr.pack(fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.tree['columns'] = self.cols
        self.filters = []
        for col in self.cols:
            self.tree.column(col, stretch=tk.YES, minwidth=0, width=80)
            if col in ['TC', 'QLVL', 'Roll rarity', 'Roll chance']:
                sort_by = 'num'
                sort_key = lambda x: float('-inf') if x == '' else float(x.replace('%', ''))
            else:
                sort_by = 'name'
                sort_key = lambda x: x
            self.tree.heading(col, text=col, sort_by=sort_by)

            name = 'combofilter_' + col
            self.filters.append(name)
            setattr(self, name, tkd.Combobox(combofr, values=sorted(set(str(x.get(col, '')) for x in self.grail).union({''}), key=sort_key), state="readonly", width=1))
            getattr(self, name).pack(side=tk.LEFT, expand=True, fill=tk.X)
            getattr(self, name).bind('<<ComboboxSelected>>', self.select_from_filters)

        for item in self.grail:
            tag = 'Owned' if item.get('Found', False) else 'Missing'
            self.tree.insert('', tk.END, values=[item.get(col, '') for col in self.cols], tags=(tag,))

        self.tree.tag_configure('Owned', background='#e6ffe6')
        self.tree.tag_configure('Missing', background='peach puff')

        self.grail_table_open = True

    def select_from_filters(self, event=None):
        self.tree.delete(*self.tree.get_children())

        # The filtering function breaks if column name has underscore in it - potential issue that could be fixed..
        all_filter = lambda x: all(str(x.get(f.split('_')[-1], '')) == getattr(self, f).get() or getattr(self, f).get() == '' for f in self.filters)
        for item in self.grail:
            if all_filter(item):
                tag = 'Owned' if item.get('Found', False) else 'Missing'
                self.tree.insert('', tk.END, values=[v for k, v in item.items() if k in self.cols], tags=(tag,))

    def close_grail_table(self, window):
        self.grail_table_open = False
        window.destroy()


