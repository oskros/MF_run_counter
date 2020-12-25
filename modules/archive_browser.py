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
        self.focus_get()

        self.iconbitmap(media_path + 'icon.ico')
        self.minsize(802, 500)

        tkd.Label(self, text='Archive browser', font='Helvetica 14').pack()

        self.tabcontrol = ttk.Notebook(self)
        self.tabcontrol.pack(expand=True, fill=tk.BOTH)

        collected_data = self.collect_data()

        self.statistics(**collected_data)
        self.run_table(laps=collected_data['laps'])
        self.drop_table(drops=collected_data['drops'])

        self.main_frame.theme.update_colors()

    def collect_data(self):
        laps = []
        drops = dict()
        chosen = self.main_frame.profile_tab.archive_dropdown.get()
        # Handle how loading of session data should be treated in the 3 different cases
        if chosen == 'Active session':
            # Load directly from timer module
            session_time = self.main_frame.timer_tab.session_time
            for lap in self.main_frame.timer_tab.laps:
                laps.append({**lap, 'Session': chosen} if isinstance(lap, dict) else {'Run time': lap, 'Session': chosen})
            for run_no, run_drops in self.main_frame.drops_tab.drops.items():
                for run_drop in run_drops:
                    drops.setdefault(run_no, []).append({**run_drop, 'Session': chosen} if isinstance(run_drop, dict) else {'item_name': None, 'input': run_drop, 'extra': '', 'Session': chosen})
        elif chosen == 'Profile history':
            # Load everything from profile .json, and append data from timer module
            active = self.main_frame.load_state_file()
            session_time = 0
            # Concatenate information from each available session
            for sess in [x for x in active.keys() if x not in ['active_state', 'extra_data']]:
                session_time += active[sess].get('session_time', 0)
                for run_no, run_drops in active[sess].get('drops', dict()).items():
                    for run_drop in run_drops:
                        drops.setdefault(str(int(run_no) + len(laps)), []).append({**run_drop, 'Session': sess} if isinstance(run_drop, dict) else {'item_name': None, 'input': run_drop, 'extra': '', 'Session': sess})
                for lap in active[sess].get('laps', []):
                    laps.append({**lap, 'Session': sess} if isinstance(lap, dict) else {'Run time': lap, 'Session': sess})

            # Append data for active session from timer module
            for run_no, run_drops in self.main_frame.drops_tab.drops.items():
                for run_drop in run_drops:
                    drops.setdefault(str(int(run_no) + len(laps)), []).append({**run_drop, 'Session': 'Active session'} if isinstance(run_drop, dict) else {'item_name': None, 'input': run_drop, 'extra': '', 'Session': 'Active session'})
            for lap in self.main_frame.timer_tab.laps:
                laps.append({**lap, 'Session': 'Active session'} if isinstance(lap, dict) else {'Run time': lap, 'Session': 'Active session'})
            session_time += self.main_frame.timer_tab.session_time
        else:
            # Load selected session data from profile .json
            active = self.main_frame.load_state_file()
            chosen_archive = active.get(chosen, dict())
            session_time = chosen_archive.get('session_time', 0)
            for lap in chosen_archive.get('laps', []):
                laps.append({**lap, 'Session': chosen} if isinstance(lap, dict) else {'Run time': lap, 'Session': chosen})
            for run_no, run_drops in chosen_archive.get('drops', dict()).items():
                for run_drop in run_drops:
                    drops.setdefault(run_no, []).append({**run_drop, 'Session': chosen} if isinstance(run_drop, dict) else {'item_name': None, 'input': run_drop, 'extra': '', 'Session': chosen})

        return {'session_time': session_time, 'laps': laps, 'drops': drops}

    def statistics(self, laps, drops, session_time):
        statistics_fr = tkd.Frame(self.tabcontrol)
        self.tabcontrol.add(statistics_fr, text='Statistics')

        sum_laps = sum(x['Run time'] for x in laps)
        avg_lap = sum_laps / len(laps) if laps else 0
        pct = sum_laps * 100 / session_time if session_time > 0 else 0

        # Kill averages
        list_uniques = [int(x['Uniques kills']) for x in laps if x.get('Uniques kills')]
        list_champs = [int(x['Champions kills']) for x in laps if x.get('Uniques kills')]
        avg_uniques = sum(list_uniques) / len(list_uniques) if list_uniques else 0
        avg_champs = sum(list_champs) / len(list_champs) if list_champs else 0
        avg_packs = avg_uniques + avg_champs / 2.534567
        seconds_per_pack = avg_lap / avg_packs if avg_packs > 0 else 0

        # Configure the list frame with scrollbars which displays the archive of the chosen session
        list_win = tkd.Frame(statistics_fr)
        list_frame = tkd.Frame(list_win)
        vscroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        hscroll = ttk.Scrollbar(list_win, orient=tk.HORIZONTAL)
        txt_list = tkd.Text(list_frame, yscrollcommand=vscroll.set, xscrollcommand=hscroll.set, font='courier 10',
                            wrap=tk.WORD, state=tk.NORMAL, cursor='', exportselection=1, name='archivebrowser')
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        txt_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        txt_list.tag_configure("HEADER", font=font.Font(family='courier', size=12, weight='bold', underline=True))
        hscroll.config(command=txt_list.xview)
        vscroll.config(command=txt_list.yview)

        # Build header for output file with information and descriptive statistics
        txt_list.insert(tk.END, 'Statistics', tag='HEADER')
        txt_list.insert(tk.END, '\nCharacter name: %s' % self.main_frame.profile_tab.extra_data.get('Character name', ''))
        txt_list.insert(tk.END, '\nRun type:       %s' % self.main_frame.profile_tab.extra_data.get('Run type', ''))
        txt_list.insert(tk.END, '\nGame mode:      %s' % self.main_frame.profile_tab.extra_data.get('Game mode', 'Single Player'))

        txt_list.insert(tk.END, '\n\nTotal session time: %s' % self.build_padded_str(session_time))
        txt_list.insert(tk.END, '\nTotal run time:     %s' % self.build_padded_str(sum_laps))
        txt_list.insert(tk.END, '\nAverage run time:   %s' % self.build_padded_str(avg_lap))
        txt_list.insert(tk.END, '\nFastest run time:   %s' % self.build_padded_str(min([x['Run time'] for x in laps], default=0)))
        txt_list.insert(tk.END, '\nNumber of runs:       %s' % str(len(laps)))
        txt_list.insert(tk.END, '\nTime spent in runs:   %s%%' % str(round(pct, 2)))

        txt_list.insert(tk.END, '\n\nAvg unique kills:     %s' % str(round(avg_uniques, 2)))
        txt_list.insert(tk.END, '\nAvg champion kills:   %s' % str(round(avg_champs, 2)))
        txt_list.insert(tk.END, '\nAvg pack kills:       %s' % str(round(avg_packs, 2)))
        txt_list.insert(tk.END, '\nAvg seconds/pack:     %s' % str(round(seconds_per_pack, 2)))

        # List all drops collected
        if drops:
            if any(drop for drop in drops.values()):
                txt_list.insert(tk.END, '\n\nCollected drops', tag='HEADER')
            for run_no, drop in drops.items():
                if drop:
                    str_n = ' ' * max(len(str(len(laps))) - len(str(run_no)), 0) + str(run_no)
                    txt_list.insert(tk.END, '\nRun ' + str_n + ' - ' + ', '.join(x['input'].strip() for x in drop))

        if laps:
            txt_list.insert(tk.END, '\n\nRun times', tag='HEADER')

        # Loop through all runs and add run times and drops for each run
        for n, lap in enumerate(laps, 1):
            run_time = lap['Run time']
            str_n = ' ' * max(len(str(len(laps))) - len(str(n)), 0) + str(n)
            droplst = drops.get(str(n), [])
            tmp = '\nRun ' + str_n + ': ' + other_utils.build_time_str(run_time)
            if droplst:
                tmp += ' - ' + ', '.join([d['input'].strip() for d in droplst])
            txt_list.insert(tk.END, tmp)

        # Disable modifications to the Text widget after all lines have been inserted
        txt_list.config(state=tk.DISABLED)

        btn_frame1 = tkd.Frame(statistics_fr)
        tkd.Button(btn_frame1, text='Copy to clipboard', command=lambda: self.copy_to_clipboard(txt_list.get(1.0, tk.END))).pack(side=tk.LEFT, fill=tk.X)
        tkd.Button(btn_frame1, text='Save as .txt', command=lambda: self.save_to_txt(txt_list.get(1.0, tk.END))).pack(side=tk.LEFT, fill=tk.X)

        # Packs all the buttons and UI in the archive browser. Packing order is important
        list_win.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        btn_frame1.pack(side=tk.BOTTOM)

    def run_table(self, laps):
        run_table_fr = tkd.Frame(self.tabcontrol)
        self.tabcontrol.add(run_table_fr, text='Run table')

        cols = ["Run", "Run time", "Real time", "Name", "MF", "Players X", "Level", "XP Gained", "Uniques kills",
                "Champions kills", "Minion kills", "Total kills", "Session"]
        tree_frame = tkd.Frame(run_table_fr)
        btn_frame2 = tkd.Frame(run_table_fr)
        btn_frame2.pack(side=tk.BOTTOM)

        vscroll_tree = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        hscroll_tree = ttk.Scrollbar(run_table_fr, orient=tk.HORIZONTAL)
        tree = tkd.Treeview(tree_frame, selectmode=tk.BROWSE, yscrollcommand=vscroll_tree.set,
                            xscrollcommand=hscroll_tree.set, show='headings', columns=cols, alternate_colour=True)
        hscroll_tree.config(command=tree.xview)
        vscroll_tree.config(command=tree.yview)
        tkd.Button(btn_frame2, text='Save as .csv', command=lambda: self.save_to_csv(tree)).pack(side=tk.LEFT, fill=tk.X)

        vscroll_tree.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        hscroll_tree.pack(side=tk.BOTTOM, fill=tk.X)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        renamed_cols = [c.replace('Uniques', 'Unique').replace('Champions', 'Champion') for c in cols]
        tree['columns'] = renamed_cols
        widths = [35, 60, 115, 60, 42, 58, 45, 75, 71, 89, 71, 59, 0]
        for i, col in enumerate(renamed_cols):
            tree.column(col, stretch=tk.NO, minwidth=0, width=widths[i])
            if col in ['Run', 'XP Gained', 'Champion kills', 'Unique kills', 'Minion kills', 'Total kills']:
                sort_by = 'num'
            else:
                sort_by = 'name'
            tree.heading(col, text=col, sort_by=sort_by)

        for n, lap in enumerate(laps, 1):
            tmp_lap = dict(lap)
            tmp_lap['Run time'] = other_utils.build_time_str(tmp_lap['Run time'])
            tmp_lap['Run'] = n
            tree.insert('', tk.END, values=[tmp_lap.get(col, '') for col in cols])

    def drop_table(self, drops):
        drop_table_fr = tkd.Frame(self.tabcontrol)
        self.tabcontrol.add(drop_table_fr, text='Drop table')

        cols = ["Run", "Item name", "Extra input", "Real time", "TC", "QLVL", "Item Class", "Grailer", "Eth Grailer", "Session", "Rarity"]
        tree_frame = tkd.Frame(drop_table_fr)
        btn_frame2 = tkd.Frame(drop_table_fr)
        btn_frame2.pack(side=tk.BOTTOM)

        vscroll_tree = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        hscroll_tree = ttk.Scrollbar(drop_table_fr, orient=tk.HORIZONTAL)
        tree = tkd.Treeview(tree_frame, selectmode=tk.BROWSE, yscrollcommand=vscroll_tree.set,
                            xscrollcommand=hscroll_tree.set, show='headings', columns=cols, alternate_colour=True)
        hscroll_tree.config(command=tree.xview)
        vscroll_tree.config(command=tree.yview)
        tkd.Button(btn_frame2, text='Save as .csv', command=lambda: self.save_to_csv(tree)).pack(side=tk.LEFT, fill=tk.X)

        vscroll_tree.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        hscroll_tree.pack(side=tk.BOTTOM, fill=tk.X)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        tree['columns'] = cols
        widths = [35, 200, 140, 120, 35, 38, 100, 47, 65, 0, 0]
        tree.tag_configure('Grail', background='#e6ffe6')
        tree.tag_configure('EthGrail', background='light goldenrod yellow')

        for i, col in enumerate(cols):
            tree.column(col, stretch=tk.NO, minwidth=0, width=widths[i])
            if col in ['Run', 'TC', 'QLVL']:
                sort_by = 'num'
            else:
                sort_by = 'name'
            tree.heading(col, text=col, sort_by=sort_by)

        for n, drop_list in drops.items():
            for drop in drop_list:
                tmp_drop = dict(drop)
                tmp_drop['Run'] = n
                if drop.get("item_name", ''):
                    tmp_drop["Item name"] = drop["item_name"]
                    tmp_drop["Extra input"] = drop["extra"]
                else:
                    tmp_drop["Item name"] = tmp_drop["input"]
                    tmp_drop["Extra input"] = ""

                if drop.get('Grailer', False) == 'True':
                    tree.insert('', tk.END, values=[tmp_drop.get(col, '') for col in cols], tag='Grail')
                elif drop.get('Eth Grailer', False) == 'True':
                    tree.insert('', tk.END, values=[tmp_drop.get(col, '') for col in cols], tag='EthGrail')
                else:
                    tree.insert('', tk.END, values=[tmp_drop.get(col, '') for col in cols])

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