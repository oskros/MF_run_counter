from init import *
from utils import tk_utils, other_utils, tk_dynamic as tkd
from tkinter import ttk, filedialog, font
import tkinter as tk
import csv


class ArchiveBrowser(tkd.Toplevel):
    def __init__(self, main_frame, **kw):
        tkd.Toplevel.__init__(self, **kw)
        self.main_frame = main_frame

        self.title('Archive Browser')
        self.wm_attributes('-topmost', self.main_frame.always_on_top)

        disp_coords = tk_utils.get_displaced_geom(self.main_frame, 800, 500)
        self.geometry(disp_coords)
        self.focus_force()

        self.iconbitmap(media_path + 'icon.ico')
        self.minsize(802, 500)

        tkd.Label(self, text='Archive browser', font='Helvetica 14').pack()

        self.tabcontrol = ttk.Notebook(self)
        self.tabcontrol.pack(expand=True, fill=tk.BOTH)

        collected_data = self.collect_data()

        self.statistics(**collected_data)
        self.run_table(laps=collected_data['laps'])
        self.drop_table(drops=collected_data['drops'])
        self.map_evaluation(laps=collected_data['laps'])

        self.main_frame.theme.update_colors()

        self.last_src = None
        self.last_pos = None
        self.bind('<Control-f>', lambda _: self.search_statistics())

    @staticmethod
    def _add_laps(laps_list, source_laps, session_name):
        """Add normalized laps from source to laps list."""
        for lap in source_laps:
            normalized = (
                {**lap, 'Session': session_name}
                if isinstance(lap, dict)
                else {'Run time': lap, 'Session': session_name}
            )
            laps_list.append(normalized)

    @staticmethod
    def _add_drops(drops_dict, source_drops, session_name, run_offset=0):
        """Add normalized drops from source to drops dict with optional run number offset."""
        for run_no, run_drops in source_drops.items():
            adjusted_run_no = str(int(run_no) + run_offset) if run_offset else run_no
            for run_drop in run_drops:
                normalized = (
                    {**run_drop, 'Session': session_name}
                    if isinstance(run_drop, dict)
                    else {'item_name': None, 'input': run_drop, 'extra': '', 'Session': session_name}
                )
                drops_dict.setdefault(adjusted_run_no, []).append(normalized)

    def collect_data(self):
        laps = []
        drops = dict()
        chosen = self.main_frame.profile_tab.archive_dropdown.get()
        
        if chosen == 'Active session':
            session_time = self.main_frame.timer_tab.session_time
            self._add_laps(laps, self.main_frame.timer_tab.laps, chosen)
            self._add_drops(drops, self.main_frame.drops_tab.drops, chosen)
        elif chosen == 'Profile history':
            active = self.main_frame.load_state_file()
            session_time = 0
            for sess in [x for x in active.keys() if x not in ['active_state', 'extra_data']]:
                session_time += active[sess].get('session_time', 0)
                self._add_drops(drops, active[sess].get('drops', dict()), sess, run_offset=len(laps))
                self._add_laps(laps, active[sess].get('laps', []), sess)
            self._add_drops(drops, self.main_frame.drops_tab.drops, 'Active session', run_offset=len(laps))
            self._add_laps(laps, self.main_frame.timer_tab.laps, 'Active session')
            session_time += self.main_frame.timer_tab.session_time
        else:
            active = self.main_frame.load_state_file()
            chosen_archive = active.get(chosen, dict())
            session_time = chosen_archive.get('session_time', 0)
            self._add_laps(laps, chosen_archive.get('laps', []), chosen)
            self._add_drops(drops, chosen_archive.get('drops', dict()), chosen)

        return {'session_time': session_time, 'laps': laps, 'drops': drops}

    def search_statistics(self):
        if not self.tabcontrol.select().endswith('frame'):
            return
        search_inp = tk_utils.MessageBox(msg="Search", entry=True).returning
        if search_inp is not None:
            cvar = tk.StringVar()
            start_pos = self.last_pos if self.last_src == search_inp else 1.0
            pos = self.txt_list.search(search_inp, start_pos, stopindex=tk.END, count=cvar)
            if pos:
                line = int(pos.split('.')[0])
                self.txt_list.see(pos)

                self.txt_list.tag_remove("search", 1.0, tk.END)
                self.txt_list.tag_add("search", f'{line}.0', f'{line+1}.0')
                self.last_src = search_inp
                self.last_pos = str(float(pos) + 0.1)

    def statistics(self, laps, drops, session_time):
        statistics_fr = tkd.Frame(self.tabcontrol)
        self.tabcontrol.add(statistics_fr, text='Statistics')

        sum_laps = sum(x['Run time'] for x in laps)
        avg_lap = sum_laps / len(laps) if laps else 0
        pct = sum_laps * 100 / session_time if session_time > 0 else 0

        # Kill averages
        list_uniques = [int(x['Uniques kills']) for x in laps if x.get('Uniques kills')]
        list_champs = [int(x['Champions kills']) for x in laps if x.get('Champions kills')]
        avg_uniques = sum(list_uniques) / len(list_uniques) if list_uniques else 0
        avg_champs = sum(list_champs) / len(list_champs) if list_champs else 0
        avg_packs = avg_uniques + avg_champs / 2.534567
        seconds_per_pack = avg_lap / avg_packs if avg_packs > 0 else 0

        # Configure the list frame with scrollbars which displays the archive of the chosen session
        list_win = tkd.Frame(statistics_fr)
        list_frame = tkd.Frame(list_win)
        vscroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        hscroll = ttk.Scrollbar(list_win, orient=tk.HORIZONTAL)
        self.txt_list = tkd.Text(list_frame, yscrollcommand=vscroll.set, xscrollcommand=hscroll.set, font='courier 10',
                            wrap=tk.WORD, state=tk.NORMAL, cursor='', exportselection=1, name='archivebrowser')
        self.txt_list.tag_configure("search", background='green', foreground='white')
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.txt_list.tag_configure("HEADER", font=font.Font(family='courier', size=12, weight='bold', underline=True))
        hscroll.config(command=self.txt_list.xview)
        vscroll.config(command=self.txt_list.yview)

        # Build header for output file with information and descriptive statistics
        self.txt_list.insert(tk.END, 'Statistics', tag='HEADER')
        self.txt_list.insert(tk.END, '\nCharacter name: %s' % self.main_frame.profile_tab.extra_data.get('Character name', ''))
        self.txt_list.insert(tk.END, '\nRun type:       %s' % self.main_frame.profile_tab.extra_data.get('Run type', ''))

        self.txt_list.insert(tk.END, '\n\nTotal session time: %s' % self.build_padded_str(session_time))
        self.txt_list.insert(tk.END, '\nTotal run time:     %s' % self.build_padded_str(sum_laps))
        self.txt_list.insert(tk.END, '\nAverage run time:   %s' % self.build_padded_str(avg_lap))
        self.txt_list.insert(tk.END, '\nFastest run time:   %s' % self.build_padded_str(min([x['Run time'] for x in laps], default=0)))
        self.txt_list.insert(tk.END, '\nNumber of runs:       %s' % str(len(laps)))
        self.txt_list.insert(tk.END, '\nTime spent in runs:   %s%%' % str(round(pct, 2)))

        self.txt_list.insert(tk.END, '\n\nAvg unique kills:     %s' % str(round(avg_uniques, 2)))
        self.txt_list.insert(tk.END, '\nAvg champion kills:   %s' % str(round(avg_champs, 2)))
        self.txt_list.insert(tk.END, '\nAvg pack kills:       %s' % str(round(avg_packs, 2)))
        self.txt_list.insert(tk.END, '\nAvg seconds/pack:     %s' % str(round(seconds_per_pack, 2)))

        # List all drops collected
        width = len(str(len(laps)))
        if drops and any(drops.values()):
            self.txt_list.insert(tk.END, '\n\nCollected drops', tag='HEADER')

            for run_no, drop in drops.items():
                if drop:
                    str_n = str(run_no).rjust(width)
                    items = ', '.join(x['input'].strip() for x in drop)
                    self.txt_list.insert(tk.END, f'\nRun {str_n} - {items}')

        if laps:
            self.txt_list.insert(tk.END, '\n\nRun times', tag='HEADER')

        # Loop through all runs and add run times and drops for each run
        for n, lap in enumerate(laps, 1):
            run_info = [f'\nRun {str(n).rjust(width)}: {other_utils.build_time_str(lap["Run time"])}']

            if drops.get(str(n)):
                run_info.append(", ".join(d["input"].strip() for d in drops.get(str(n))))

            self.txt_list.insert(tk.END, " - ".join(run_info))

        # Disable modifications to the Text widget after all lines have been inserted
        self.txt_list.config(state=tk.DISABLED)

        btn_frame1 = tkd.Frame(statistics_fr)
        tkd.Button(btn_frame1, text='Copy to clipboard', command=lambda: self.copy_to_clipboard(self.txt_list.get(1.0, tk.END))).pack(side=tk.LEFT, fill=tk.X)
        tkd.Button(btn_frame1, text='Save as .txt', command=lambda: self.save_to_txt(self.txt_list.get(1.0, tk.END))).pack(side=tk.LEFT, fill=tk.X)

        # Packs all the buttons and UI in the archive browser. Packing order is important
        list_win.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        btn_frame1.pack(side=tk.BOTTOM)

    @staticmethod
    def _normalize_lap(lap: dict, run: int) -> dict:
        tmp = dict(lap)

        run_time_seconds = tmp.get('Run time') or 0
        tmp['Run'] = run
        tmp['Run time'] = other_utils.build_time_str(run_time_seconds)

        # kills/min
        total_kills_raw = tmp.get('Total kills') or 0
        try:
            total_kills = int(total_kills_raw)
        except (TypeError, ValueError):
            total_kills = 0

        tmp['Kills/min'] = (
            f"{(total_kills * 60) / run_time_seconds:.2f}" if run_time_seconds > 0 else ''
        )

        # Areas visited -> comma-separated
        areas = tmp.get('Areas visited')
        tmp['Areas visited'] = ', '.join(areas) if isinstance(areas, list) and areas else ''

        return tmp

    def _build_treeview(self, parent_frame, columns, enable_filters=False, tags=None):
        """
        Builds a treeview with scrollbars and optional filtering.
        
        Args:
            parent_frame: The parent frame to add the treeview to
            columns: List of column dicts with keys: key, label, width, sort, and optionally cb_width
            enable_filters: If True, creates filter_frame and filters list for filter comboboxes
            tags: Dict of tag names to tag configurations (e.g., {'Grail': {'background': '#e6ffe6'}})
        
        Returns:
            tuple: (tree, filter_frame, filters_list)
            filter_frame and filters_list are None if enable_filters=False
        """
        display_cols = [c["label"] for c in columns]

        tree_frame = tkd.Frame(parent_frame)
        btn_frame = tkd.Frame(parent_frame)
        btn_frame.pack(side=tk.BOTTOM)

        vscroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        hscroll = ttk.Scrollbar(parent_frame, orient=tk.HORIZONTAL)

        tree = tkd.Treeview(
            tree_frame,
            selectmode=tk.BROWSE,
            yscrollcommand=vscroll.set,
            xscrollcommand=hscroll.set,
            show='headings',
            columns=display_cols,
            alternate_colour=True,
        )
        vscroll.config(command=tree.yview)
        hscroll.config(command=tree.xview)

        tkd.Button(btn_frame, text='Save as .csv', command=lambda: self.save_to_csv(tree)).pack(
            side=tk.LEFT, fill=tk.X
        )

        filter_frame = None
        filters = None

        if enable_filters:
            filter_frame = tkd.Frame(tree_frame)
            filters = []

        vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        if enable_filters:
            filter_frame.pack(fill=tk.X)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Configure tags if provided
        if tags:
            for tag_name, tag_config in tags.items():
                tree.tag_configure(tag_name, **tag_config)

        # Configure columns/headings
        for col in columns:
            label = col["label"]
            tree.column(label, stretch=tk.NO, minwidth=0, width=col["width"])
            tree.heading(label, text=label, sort_by=col["sort"])

        return tree, filter_frame, filters

    def run_table(self, laps):
        run_table_fr = tkd.Frame(self.tabcontrol)
        self.tabcontrol.add(run_table_fr, text='Run table')

        # One source of truth: order + label + width + sorting + data-key mapping
        columns = [
            {"key": "Run", "label": "Run", "width": 35, "sort": "num"},
            {"key": "Run time", "label": "Run time", "width": 60, "sort": "name"},
            {"key": "Real time", "label": "Real time", "width": 115, "sort": "name"},
            {"key": "Name", "label": "Name", "width": 60, "sort": "name"},
            {"key": "MF", "label": "MF", "width": 42, "sort": "num"},
            {"key": "Players X", "label": "Players X", "width": 58, "sort": "num"},
            {"key": "Level", "label": "Level", "width": 45, "sort": "num"},
            {"key": "XP Gained", "label": "XP Gained", "width": 75, "sort": "num"},
            {"key": "Uniques kills", "label": "Unique kills", "width": 71, "sort": "num"},
            {"key": "Champions kills", "label": "Champion kills", "width": 89, "sort": "num"},
            {"key": "Minion kills", "label": "Minion kills", "width": 71, "sort": "num"},
            {"key": "Total kills", "label": "Total kills", "width": 59, "sort": "num"},
            {"key": "Kills/min", "label": "Kills/min", "width": 70, "sort": "num"},
            {"key": "Session", "label": "Session", "width": 80, "sort": "name"},
            {"key": "Map seed", "label": "Map seed", "width": 70, "sort": "name"},
            {"key": "Areas visited", "label": "Areas visited", "width": 200, "sort": "name"},
        ]

        tree, _, _ = self._build_treeview(run_table_fr, columns)

        # Insert rows
        for run, lap in enumerate(laps, start=1):
            tmp_lap = self._normalize_lap(lap, run)
            tree.insert('', tk.END, values=[tmp_lap.get(col["key"], '') for col in columns])

    def drop_table(self, drops):
        flat_drops = []
        for n, drop_list in drops.items():
            for drop in drop_list:
                item_name = drop.get('input', '') if drop.get('item_name') is None else drop.get('item_name')
                flat_drops.append({**drop, 'Run': n, 'Item name': item_name, 'Extra input': drop.get('extra', '')})

        drop_table_fr = tkd.Frame(self.tabcontrol)
        self.tabcontrol.add(drop_table_fr, text='Drop table')

        # One source of truth: order + label + width + sorting + data-key mapping
        columns = [
            {"key": "Run", "label": "Run", "width": 35, "sort": "num", "cb_width": 3},
            {"key": "Item name", "label": "Item name", "width": 200, "sort": "name", "cb_width": 30},
            {"key": "Extra input", "label": "Extra input", "width": 140, "sort": "name", "cb_width": 20},
            {"key": "Real time", "label": "Real time", "width": 120, "sort": "name", "cb_width": 16},
            {"key": "TC", "label": "TC", "width": 35, "sort": "num", "cb_width": 3},
            {"key": "QLVL", "label": "QLVL", "width": 38, "sort": "num", "cb_width": 3},
            {"key": "Item Class", "label": "Item Class", "width": 100, "sort": "name", "cb_width": 13},
            {"key": "Grailer", "label": "Grailer", "width": 47, "sort": "name", "cb_width": 5},
            {"key": "Eth Grailer", "label": "Eth Grailer", "width": 65, "sort": "name", "cb_width": 7},
            {"key": "Session", "label": "Session", "width": 80, "sort": "name", "cb_width": 10},
            {"key": "Rarity", "label": "Rarity", "width": 80, "sort": "name", "cb_width": 10},
        ]

        tags = {
            'Grail': {'background': '#e6ffe6'},
            'EthGrail': {'background': 'light goldenrod yellow'}
        }
        tree, filter_frame, filters = self._build_treeview(
            drop_table_fr, columns, enable_filters=True, tags=tags
        )

        # Create mapping from filter names to data keys
        filter_key_map = {f: col["key"] for f, col in zip(filters, columns)}
        
        def select_drops_from_filters(event=None):
            tree.delete(*tree.get_children())

            filter_fn = tk_utils.create_treeview_filter(
                filters,
                lambda f: getattr(self, f).get(),
                lambda f: filter_key_map[f]
            )
            
            for drop in flat_drops:
                if filter_fn(drop):
                    values = [drop.get(col["key"], '') for col in columns]
                    if drop.get('Grailer', False) == 'True':
                        tree.insert('', tk.END, values=values, tag='Grail')
                    elif drop.get('Eth Grailer', False) == 'True':
                        tree.insert('', tk.END, values=values, tag='EthGrail')
                    else:
                        tree.insert('', tk.END, values=values)

        for col in columns:
            label = col["label"]
            key = col["key"]

            # Determine sort key for combobox values
            sort_key = lambda x: (
                other_utils.numeric_sort_key(x, empty_first=True)
                if col["sort"] == "num"
                else x
            )

            name = 'combofilter_' + label
            filters.append(name)
            setattr(self, name, tkd.Combobox(
                filter_frame,
                values=sorted(set(str(x.get(key, '')) for x in flat_drops).union({''}), key=sort_key),
                state="readonly",
                width=col["cb_width"]
            ))
            getattr(self, name).pack(side=tk.LEFT)
            getattr(self, name).bind('<<ComboboxSelected>>', select_drops_from_filters)

        select_drops_from_filters()

    @staticmethod
    def group_laps(laps):
        seed_dict = dict()
        for lap in laps:
            seed = lap.get('Map seed', 0)
            seed_dict.setdefault(seed, []).append(lap)

        out = []
        for k, v in seed_dict.items():
            run_count = len(v)

            run_times = [x['Run time'] for x in v if 'Run time' in x]
            avg_run_time = other_utils.safe_avg(run_times, decimals=2)

            mf_items = other_utils.filter_items(v, 'MF')
            mfs = [int(str(x['MF']).replace('%', '')) for x in mf_items]
            u_mfs = [1 + x*250 // (x + 250) / 100 for x in mfs]
            avg_u_mfs = other_utils.safe_avg(u_mfs, decimals=2)

            weighted_mf = [
                int(x.get('Max MF', x['MF'].replace('%', '')))*0.645 +
                int(x.get('Min MF', x['MF'].replace('%', '')))*0.355
                for x in mf_items
            ]
            avg_wgt_mf = other_utils.safe_avg(weighted_mf, decimals=2)
            weighted_u_mf = [1 + x*250 // (x + 250) / 100 for x in weighted_mf]
            avg_weighted_u_mf = other_utils.safe_avg(weighted_u_mf, decimals=2)

            player_items = other_utils.filter_items(v, 'Players X')
            players = [int(x['Players X']) for x in player_items]
            avg_players = other_utils.safe_avg(players, decimals=2)

            pack_kills = [
                int(x['Uniques kills'])+int(x['Champions kills'])/2.534567
                for x in other_utils.filter_items(v, 'Uniques kills')
            ]
            avg_packs = other_utils.safe_avg(pack_kills, decimals=2)
            avg_packs_hork = avg_packs*1.55
            avg_packs_joined = f'{avg_packs}   ({avg_packs_hork})' if avg_packs else ''

            secs_pack = other_utils.safe_divide(avg_run_time, avg_packs, decimals=2)
            secs_pack_hork = other_utils.safe_divide(avg_run_time, avg_packs*1.55, decimals=2)
            secs_packs_joined = f'{secs_pack}   ({secs_pack_hork})' if avg_packs else ''

            adjeff = other_utils.safe_divide(secs_pack, avg_u_mfs, decimals=2)
            adjeff_hork = other_utils.safe_divide(secs_pack_hork, avg_weighted_u_mf, decimals=2)
            adjeff_joined = f'{adjeff}   ({adjeff_hork})' if adjeff else ''

            out.append({'Map seed': k, 'Run count': run_count, 'Avg run time': avg_run_time, 'Avg MF': avg_wgt_mf,
                        'Avg players X': avg_players, 'Avg packs (55% hork)': avg_packs_joined,
                        'Avg secs/pack (55% hork)': secs_packs_joined, 'Adjeff (55% hork)': adjeff_joined})
        return out

    def map_evaluation(self, laps):
        map_eval_fr = tkd.Frame(self.tabcontrol)
        self.tabcontrol.add(map_eval_fr, text='Map evaluation')

        # One source of truth: order + label + width + sorting + data-key mapping
        columns = [
            {"key": "Map", "label": "Map", "width": 35, "sort": "num"},
            {"key": "Map seed", "label": "Map seed", "width": 70, "sort": "num"},
            {"key": "Run count", "label": "Run count", "width": 70, "sort": "num"},
            {"key": "Avg run time", "label": "Avg run time", "width": 80, "sort": "num"},
            {"key": "Avg MF", "label": "Avg MF", "width": 55, "sort": "num"},
            {"key": "Avg players X", "label": "Avg players X", "width": 85, "sort": "num"},
            {"key": "Avg packs (55% hork)", "label": "Avg packs (55% hork)", "width": 130, "sort": "name"},
            {"key": "Avg secs/pack (55% hork)", "label": "Avg secs/pack (55% hork)", "width": 150, "sort": "name"},
            {"key": "Adjeff (55% hork)", "label": "Adjeff (55% hork)", "width": 105, "sort": "name"},
        ]

        tree, _, _ = self._build_treeview(map_eval_fr, columns)

        grouped = self.group_laps(laps=laps)

        # Insert rows
        for n, smap in enumerate(grouped, 1):
            tmp_lap = dict(smap)
            tmp_lap['Map'] = n
            tree.insert('', tk.END, values=[tmp_lap.get(col["key"], '') for col in columns])

    def copy_to_clipboard(self, string):
        """
        Clears current clipboard and adds the string instead
        """
        self.clipboard_clear()
        self.clipboard_append(string)

    @staticmethod
    def save_to_txt(string):
        """
        Writes a string to text file. Adds a line break every time '\n' is encountered in the string.
        'asksaveasfile' returns a writable object that then passes information on to the .txt file
        """
        f = tk.filedialog.asksaveasfile(mode='w', defaultextension='.txt',
                                        filetypes=(('.txt', '*.txt'), ('All Files', '*.*')))
        if not f:
            return
        f.write(string)
        f.close()

    @staticmethod
    def save_to_csv(tree):
        """
        Writes the treeview rows to a .csv file

        Here we use asksaveasfilename in order to just return a path instead of writable object, because then we can
        initiate our own csv writer object with the newline='' option, which ensures we don't have double line breaks
        """
        f = tk.filedialog.asksaveasfilename(defaultextension='.csv',
                                            filetypes=(('.csv', '*.csv'), ('All Files', '*.*')))
        if not f:
            return
        with open(f, newline='', mode='w') as fo:
            writer = csv.writer(fo, delimiter=',')
            writer.writerow(tree['columns'])
            for row_id in tree.get_children():
                row = tree.item(row_id)['values']
                writer.writerow(row)

    @staticmethod
    def build_padded_str(inp):
        inp = other_utils.build_time_str(inp)
        return ' '*(12-len(inp)) + inp