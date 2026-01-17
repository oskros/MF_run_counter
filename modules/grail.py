from init import *
from utils import tk_dynamic as tkd, tk_utils, herokuapp_controller, other_utils
from utils.color_themes import Theme
from utils.item_name_lists import get_eth_item_set, get_base_item, is_pd2_item
from utils.herokuapp_json_generator import get_default_data, get_default_eth_data
import tkinter as tk
from tkinter import ttk
import requests
import csv
import win32gui
from tkinter import messagebox
import logging


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
        self._grail_controller_eth_mode = False

        self._make_widgets()
        self.update_statistics()

    def _make_widgets(self):
        bfr1 = tkd.LabelFrame(self, height=28)
        bfr1.propagate(False)
        bfr1.pack(expand=False, fill=tk.X, padx=1, pady=1)

        tkd.Button(bfr1, text='Sync', width=6, command=self.sync_local_grail, relief=tk.RIDGE, borderwidth=1, tooltip='Updates your local grail to include items logged either in your profiles or on herokuapp').pack(side=tk.LEFT, padx=[1, 15], pady=1)
        tkd.Checkbutton(bfr1, text='Profiles', variable=self.sync_drops).pack(side=tk.LEFT)
        tkd.Checkbutton(bfr1, text='Herokuapp', variable=self.sync_herokuapp).pack(side=tk.LEFT)

        bfr2 = tkd.Frame(self)
        bfr2.pack(pady=12, expand=True, fill=tk.X)
        tkd.Button(bfr2, text='Upload grail to herokuapp', command=self.upload_to_herokuapp, borderwidth=3, tooltip='This will not delete already found items on herokuapp if they are not in your local grail, but only add new items').pack(padx=8, side=tk.LEFT, fill=tk.X, expand=True)

        bfr3 = tkd.Frame(self)
        bfr3.pack(side=tk.BOTTOM, expand=tk.YES, fill=tk.X)
        tkd.Button(bfr3, text='Item table', borderwidth=3, command=self.open_grail_table, width=1).pack(side=tk.LEFT, fill=tk.X, padx=[1, 0], pady=1, expand=tk.YES)
        tkd.Button(bfr3, text='Grail controller', borderwidth=3, command=self.open_grail_controller, width=1).pack(side=tk.LEFT, fill=tk.X, padx=1, pady=1, expand=tk.YES)

        descr = tkd.ListboxFrame(self)
        descr.columnconfigure(0, weight=1)
        descr.columnconfigure(1, weight=1)
        descr.columnconfigure(2, weight=1)
        descr.columnconfigure(3, weight=1)
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
            # Filter out PD2 items if PD2 mode is not enabled
            if not self.main_frame.pd2_mode and item.get('PD2 item', False):
                continue
            if all(item.get(k, None) == v for k, v in conditions.items()):
                if eth:
                    if item.get('Item', '') in get_eth_item_set(self.main_frame.pd2_mode):
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
        resp = None
        if self.sync_herokuapp.get():
            resp = tk_utils.MultiEntryBox(entries=['Username'], title='d2-holy-grail.herokuapp', defaults=[self.username.get()], masks=[None]).returning
            if resp:
                uid = resp[0]
                resp_data = self.get_grail_from_herokuapp(uid)
                if resp_data is None:
                    return
                heroku_grail, heroku_ethgrail = resp_data
                self.update_grail_from_list(heroku_ethgrail, eth=True)
                item_lst.extend(heroku_grail)
                msg += f'\n\n- Grail data from d2-holy-grail.herokuapp for user\n  "{self.username.get()}"'
        if self.sync_drops.get():
            item_lst.extend(self.get_grail_from_drops())
            msg += '\n\n- Drops from all saved profiles'

        if self.sync_drops.get() == self.sync_herokuapp.get() == 0:
            messagebox.showerror('Grail update', 'No update choices selected')
        elif item_lst:
            self.update_grail_from_list(item_lst)
            self.update_statistics()
            if self.grail_table_open:
                self.select_from_filters()
            messagebox.showinfo('Grail update', msg)
        elif not (self.sync_herokuapp.get() == 1 and resp is None):
            messagebox.showinfo('Grail update', 'No logged items: Nothing to update')

    def reset_grail(self):
        resp = tk_utils.MessageBox(msg='Are you sure you want to reset the locally stored grail file?', title='WARNING', disabled_btn_input='DELETE').returning
        if resp == 'DELETE':
            self.grail = self.create_empty_grail()
            self.update_statistics()
            if self.grail_table_open:
                self.select_from_filters()
            for var in dir(self):
                if var.startswith('grail_item'):
                    getattr(self, var).set(0)

    def create_empty_grail(self):
        # Use item_library.csv which contains all items (regular + PD2)
        grail_dict = []
        with open(media_path + 'item_library.csv', 'r') as fo:
            for row in csv.DictReader(fo):
                item_dict = {**row, 'Found': False}
                # Check if item can be ethereal (considering PD2 mode)
                if row['Item'] in get_eth_item_set(self.main_frame.pd2_mode):
                    item_dict['FoundEth'] = False
                # Set PD2 item attribute based on the CSV column
                item_dict['PD2 item'] = row.get('PD2 item', '').upper() == 'TRUE'
                grail_dict.append(item_dict)

        other_utils.atomic_json_dump(self.file_name, grail_dict)
        return grail_dict

    def load_grail(self):
        if not os.path.isfile(self.file_name):
            self.create_empty_grail()

        state = other_utils.json_load_err(self.file_name)
        
        # Only repopulate if PD2 items are missing (backwards compatibility)
        pd2_items_in_state = any(item.get('PD2 item', False) for item in state)
        if not pd2_items_in_state:
            state = self.repopulate_grail_for_pd2(state)
        
        return state

    def repopulate_grail_for_pd2(self, state):
        """Backwards compatibility: merge in PD2 items if they're missing from existing grail files."""
        existing_items = {item.get('Item', '') for item in state}
        eth_item_set = get_eth_item_set(self.main_frame.pd2_mode)
        
        # Load PD2 items and add missing ones
        with open(media_path + 'item_library.csv', 'r') as fo:
            for row in csv.DictReader(fo):
                if row.get('PD2 item', '').upper() == 'TRUE' and row['Item'] not in existing_items:
                    item_dict = {**row, 'Found': False}
                    if row['Item'] in eth_item_set:
                        item_dict['FoundEth'] = False
                    item_dict['PD2 item'] = True
                    state.append(item_dict)
        
        # Ensure all items have the PD2 item attribute and correct eth property
        for item in state:
            item_name = item.get('Item', '')
            if 'PD2 item' not in item:
                item['PD2 item'] = is_pd2_item(item_name)
            
            # Add FoundEth property if item can be ethereal in current PD2 mode
            if item_name in eth_item_set and 'FoundEth' not in item:
                item['FoundEth'] = False
        
        return state

    def save_grail(self):
        other_utils.atomic_json_dump(self.file_name, self.grail)

        self.main_frame.herokuapp_username = self.username.get()
        self.main_frame.herokuapp_password = self.password.get()

    def get_grail_from_drops(self):
        drops = []

        # Iterate through all saved profiles
        for p in self.main_frame.profiles:
            file = f'Profiles/{p}.json'
            state = other_utils.json_load_err(file)

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
                    item_name = item.get('Item', None)
                    if item_name and hasattr(self, 'grail_item_' + self.fix_name(item_name)):
                        getattr(self, 'grail_item_' + self.fix_name(item_name)).set(1)

    def update_grail_from_name(self, name):
        # Check if we're in eth mode (set when grail controller is opened)
        update_key = 'FoundEth' if self._grail_controller_eth_mode else 'Found'
        
        for i, item in enumerate(self.grail):
            if item.get('Item', None) == name:
                found_value = not item.get(update_key, False)
                self.grail[i].update({update_key: found_value})
                self.update_statistics()
                if self.grail_table_open:
                    self.select_from_filters()
                return

    def update_grail_from_index(self, idx):
        self.grail[idx].update({'Found': True})
        self.update_statistics()
        if self.grail_table_open:
            self.select_from_filters()
        if hasattr(self, f"grail_item_{self.fix_name(self.grail[idx]['Item'])}"):
            getattr(self, f"grail_item_{self.fix_name(self.grail[idx]['Item'])}").set(1)

    def get_grail_from_herokuapp(self, uid):
        try:
            prox = self.main_frame.webproxies if isinstance(self.main_frame.webproxies, dict) else None
            herokuapp_grail = herokuapp_controller.get_grail(uid, proxies=prox, pd2_mode=self.main_frame.pd2_mode)
        except requests.exceptions.HTTPError:
            messagebox.showerror('Username 404', f"Username '{uid}' doesn't exist on d2-holy-grail.herokuapp.com")
            return

        self.username.set(uid)

        data = herokuapp_grail.get('data', dict())
        eth_data = herokuapp_grail.get('ethData', dict())
        upd_lst = herokuapp_controller.build_update_lst(data)
        eth_lst = herokuapp_controller.build_update_lst(eth_data, eth=True)
        return upd_lst, eth_lst

    def upload_to_herokuapp(self, upd_dict=None, show_confirm=True, pop_up_msg=None, pop_up_title='d2-holy-grail.herokuapp', eth_dict=None):
        resp = tk_utils.MultiEntryBox(entries=['Username', 'Password'], title=pop_up_title, defaults=[self.username.get(), self.password.get()], masks=[None, "*"], msg=pop_up_msg).returning
        if resp is None:
            return None
        uid, pwd = resp
        try:
            prox = self.main_frame.webproxies if isinstance(self.main_frame.webproxies, dict) else None
            herokuapp_grail = herokuapp_controller.get_grail(uid, proxies=prox, pd2_mode=self.main_frame.pd2_mode)
        except requests.exceptions.HTTPError:
            messagebox.showerror('Username 404', f"Username '{uid}' doesn't exist on d2-holy-grail.herokuapp. Try again")
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
            messagebox.showerror('Password 401', f"Password incorrect for user '{uid}', try again")
            return self.upload_to_herokuapp(upd_dict=upd_dict, show_confirm=show_confirm, pop_up_msg=pop_up_msg, pop_up_title=pop_up_title)

        self.username.set(uid)
        self.password.set(pwd)

        if show_confirm:
            messagebox.showinfo('Success', f'Upload to "{uid}" on d2-holy-grail.herokuapp.com successful!')
        return True

    def open_grail_controller(self):
        def rec_checkbox_add(master, frame, dct, rows=4, depth=None):
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
                        i_name = f'Rainbow Facet ({k} {depth[-1].title()})'
                        var_name = f'grail_item_{self.fix_name(i_name)}'
                    else:
                        # Replace characters that cannot be used in variable names
                        var_name = f'grail_item_{self.fix_name(k)}'
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
                        new_frame.pack(side=tk.TOP, expand=True, anchor=tk.NW, fill=tk.Y, pady=(0, 30))
                        cnt += 1
                    else:
                        new_frame = tkd.Frame(frame)
                        new_frame.pack(side=tk.LEFT, expand=True, anchor=tk.N)

                    # .title() function bugs out with apostrophes. Handle the specific issues hardcoded here
                    # Also, there is a spelling mistake in herokuapp that we fix: Hsaru's -> Hsarus'
                    txt = k.title().replace("'S", "'s").replace("'A", "'a").replace("Hsaru's", "Hsarus'")
                    tkd.Label(new_frame, text=txt, font='Arial 15 bold').pack(expand=True, anchor=tk.N)
                    rec_checkbox_add(master, new_frame, v, rows, depth + [k])

        # We don't allow more than one open window of the grail controller
        if win32gui.FindWindow(None, 'Grail controller'):
            return

        # Store eth mode state for use in update_grail_from_name
        eth_mode = self.show_eth_grail.get()
        self._grail_controller_eth_mode = eth_mode
        
        # Initialise the TopLevel window (important we use TopLevel instead of Tk, to pass over information between
        # the defined widgets and the main app)
        window = tkd.Toplevel()
        window.title('Grail controller' + (' (Eth)' if eth_mode else ''))
        window.resizable(True, True)
        window.iconbitmap(media_path + 'icon.ico')

        # Build nested dict with information from the current grail
        # Filter items based on PD2 mode - include PD2 items when PD2 mode is active
        visible_grail = [x for x in self.grail if self.main_frame.pd2_mode or not x.get('PD2 item', False)]
        
        # Filter to eth-capable items and use FoundEth when in eth mode
        if eth_mode:
            eth_item_set = get_eth_item_set(self.main_frame.pd2_mode)
            visible_grail = [x for x in visible_grail if x.get('Item', '') in eth_item_set]
            upd_dict = {x['Item']: True for x in visible_grail if x.get('FoundEth', None) is True}
            default_data = get_default_eth_data(pd2_mode=self.main_frame.pd2_mode)
        else:
            upd_dict = {x['Item']: True for x in visible_grail if x.get('Found', None) is True}
            default_data = get_default_data(pd2_mode=self.main_frame.pd2_mode)
        
        nested_grail = herokuapp_controller.update_grail_dict(
            dct=default_data,
            item_upg_dict=upd_dict
        )

        # Revert patches for display: Kira's Guardian should show under Exceptional, not Elite
        try:
            nested_grail['uniques']['armor']['circlet'].setdefault('exceptional', {})["Kira's Guardian"] = nested_grail['uniques']['armor']['circlet']['elite'].pop("Kira's Guardian")
        except (KeyError, AttributeError) as e:
            logging.warning(f"Failed to revert Kira's Guardian patch in grail controller: {e}")

        # Fix quality ordering for groups where items are processed out of quality order
        def fix_quality_ordering(group_path):
            """Reorder quality keys to: normal → exceptional → elite."""
            ordered = [(q, group_path[q]) for q in ('normal', 'exceptional', 'elite') if q in group_path]

            group_path.clear()
            group_path.update(ordered)
        
        # Fix ordering for known problematic groups
        fix_quality_ordering(nested_grail['uniques']['armor']['circlet'])
        fix_quality_ordering(nested_grail['uniques']['weapons']['throwing'])

        tabcontrol = ttk.Notebook(window)
        tabcontrol.pack(expand=True, fill=tk.BOTH)

        # Build the new tabs
        unique_armor = tkd.Frame(tabcontrol)
        unique_weapons = tkd.Frame(tabcontrol)
        unique_other = tkd.Frame(tabcontrol)
        tabcontrol.add(unique_armor, text='Unique Armor')
        tabcontrol.add(unique_weapons, text='Unique Weapons')
        tabcontrol.add(unique_other, text='Unique Other')
        
        # Only show sets and runes tabs when not in eth mode (they can't be ethereal)
        if not eth_mode:
            sets = tkd.Frame(tabcontrol)
            runes = tkd.Frame(tabcontrol)
            tabcontrol.add(sets, text='Sets')
            tabcontrol.add(runes, text='Runes')

        rec_checkbox_add(self, unique_armor, nested_grail['uniques']['armor'], 3)
        rec_checkbox_add(self, unique_weapons, nested_grail['uniques']['weapons'], 4)
        rec_checkbox_add(self, unique_other, nested_grail['uniques']['other'], 3)
        if not eth_mode:
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

        # Add PD2 item column if PD2 mode is active
        cols = list(self.cols)
        if self.main_frame.pd2_mode:
            cols.append('PD2 item')

        tree_frame = tkd.Frame(window)
        vscroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        hscroll = ttk.Scrollbar(window, orient=tk.HORIZONTAL)
        self.tree = tkd.Treeview(tree_frame, selectmode=tk.BROWSE, yscrollcommand=vscroll.set, xscrollcommand=hscroll.set, show='headings', columns=cols)
        hscroll.config(command=self.tree.xview)
        vscroll.config(command=self.tree.yview)

        combofr = tkd.Frame(tree_frame)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        combofr.pack(fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.tree['columns'] = cols
        self.filters = []
        # Create mapping from filter names to column names to handle underscores in column names
        filter_col_map = {}
        for col in cols:
            self.tree.column(col, stretch=tk.YES, minwidth=0, width=80)
            if col in ['TC', 'QLVL', 'Roll rarity', 'Roll chance']:
                sort_by = 'num'
                sort_key = lambda x: other_utils.numeric_sort_key(x, empty_first=True)
            else:
                sort_by = 'name'
                sort_key = lambda x: x
            self.tree.heading(col, text=col, sort_by=sort_by)

            name = 'combofilter_' + col
            filter_col_map[name] = col
            self.filters.append(name)
            # Only include values from items visible based on PD2 mode
            visible_items = [x for x in self.grail if self.main_frame.pd2_mode or not x.get('PD2 item', False)]
            # Use _get_column_value to get transformed values (e.g., Base Item in PD2 mode)
            setattr(self, name, tkd.Combobox(combofr, values=sorted(set(str(self._get_column_value(x, col)) for x in visible_items).union({''}), key=sort_key), state="readonly", width=1))
            getattr(self, name).pack(side=tk.LEFT, expand=True, fill=tk.X)
            getattr(self, name).bind('<<ComboboxSelected>>', self.select_from_filters)
        
        self.filter_col_map = filter_col_map

        for item in self.grail:
            # Filter out PD2 items if PD2 mode is not enabled
            if not self.main_frame.pd2_mode and item.get('PD2 item', False):
                continue
            tag = 'Owned' if item.get('Found', False) else 'Missing'
            values = [self._get_column_value(item, col) for col in cols]
            self.tree.insert('', tk.END, values=values, tags=(tag,))

        self.tree.tag_configure('Owned', background='#e6ffe6')
        self.tree.tag_configure('Missing', background='peach puff')

        self.grail_table_open = True

    def _get_column_value(self, item, col):
        """Get the value for a column, handling special cases like Base Item in PD2 mode"""
        if col == 'Base Item':
            return get_base_item(item, self.main_frame.pd2_mode)
        return item.get(col, '')
    
    def select_from_filters(self, event=None):
        self.tree.delete(*self.tree.get_children())

        filter_fn = tk_utils.create_treeview_filter(
            self.filters,
            lambda f: getattr(self, f).get(),
            lambda f: self.filter_col_map[f],  # Use mapping to handle underscores in column names
            get_data_value=self._get_column_value  # Use transformed values (e.g., Base Item in PD2 mode)
        )
        
        # Get the columns list (including PD2 item if PD2 mode is active)
        cols = list(self.cols)
        if self.main_frame.pd2_mode:
            cols.append('PD2 item')
        
        for item in self.grail:
            # Filter out PD2 items if PD2 mode is not enabled
            if not self.main_frame.pd2_mode and item.get('PD2 item', False):
                continue
            if filter_fn(item):
                tag = 'Owned' if item.get('Found', False) else 'Missing'
                values = [self._get_column_value(item, col) for col in cols]
                self.tree.insert('', tk.END, values=values, tags=(tag,))

    def close_grail_table(self, window):
        self.grail_table_open = False
        window.destroy()

    @staticmethod
    def fix_name(name):
        return name.replace("'", "1").replace(' ', '_')


