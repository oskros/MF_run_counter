import utils.other_utils
from init import *
import csv
import json
import os
import sys
import time
import tkinter as tk
from utils import tk_dynamic as tkd, tk_utils
from utils.color_themes import Theme
from tkinter import ttk, messagebox, filedialog
from tkinter.font import Font as tkFont


class Profile(tkd.Frame):
    def __init__(self, main_frame, parent=None, **kw):
        tkd.Frame.__init__(self, parent, kw)
        self.root = parent
        self.main_frame = main_frame
        self.active_profile = tk.StringVar()
        self.tot_laps = 0

        if self.main_frame.active_profile == '':
            self._add_new_profile(first_profile=True)
            self.main_frame.active_profile = self.active_profile.get()
        state = self.main_frame.load_state_file()
        self.available_archive = ['Profile history', 'Active session'] + [x for x in state.keys() if x not in ['active_state', 'extra_data']]
        self.selected_archive = tk.StringVar()
        self.selected_archive.set('Profile history')
        self.extra_data = state.get('extra_data', dict())

        self._make_widgets()

    def _make_widgets(self):
        tkd.Label(self, text='Select active profile', justify=tk.LEFT).pack(anchor=tk.W)

        profile_dropdown_frame = tkd.Frame(self, height=28, width=238, pady=2, padx=2)
        profile_dropdown_frame.propagate(False)
        profile_dropdown_frame.pack()

        self.active_profile.set(self.main_frame.active_profile)
        self.profile_dropdown = ttk.Combobox(profile_dropdown_frame, textvariable=self.active_profile, state='readonly', values=self.main_frame.profiles)
        self.profile_dropdown.bind("<<ComboboxSelected>>", lambda e: self._change_active_profile())
        self.profile_dropdown.bind("<FocusOut>", lambda e: self.profile_dropdown.selection_clear())
        self.profile_dropdown.pack(side=tk.LEFT, expand=True, fill=tk.X)

        tkd.Button(profile_dropdown_frame, text='New...', command=self._add_new_profile).pack(side=tk.LEFT)
        tkd.Button(profile_dropdown_frame, text='Delete', command=self._delete_profile).pack(side=tk.LEFT)

        self.run_type = tk.StringVar(self, value=self.extra_data.get('Run type', ''))
        self.game_mode = tk.StringVar(self, value=self.extra_data.get('Game mode', 'Single Player'))
        self.char_name = tk.StringVar(self, value=self.extra_data.get('Character name', ''))
        self._extra_info_label('Run type', self.run_type)
        self._extra_info_label('Game mode', self.game_mode)
        self._extra_info_label('Character name', self.char_name)

        tkd.Label(self, text='Select an archived run for this profile', justify=tk.LEFT).pack(anchor=tk.W, pady=(6, 0))
        sel_frame = tkd.Frame(self, height=28, width=238, pady=2, padx=2)
        sel_frame.propagate(False)
        sel_frame.pack()
        self.archive_dropdown = ttk.Combobox(sel_frame, textvariable=self.selected_archive, state='readonly', values=self.available_archive)
        self.archive_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_descriptive_statistics())
        self.archive_dropdown.bind("<FocusOut>", lambda e: self.archive_dropdown.selection_clear())
        self.archive_dropdown.pack(side=tk.LEFT, expand=True, fill=tk.X)

        tkd.Button(sel_frame, text='Open', command=self.open_archive_browser).pack(side=tk.LEFT)
        tkd.Button(sel_frame, text='Delete', command=self.delete_archived_session).pack(side=tk.LEFT)

        self.descr = tkd.Listbox2(self, selectmode=tk.EXTENDED, height=7, activestyle='none', font=('courier', 8))
        self.descr.bind('<FocusOut>', lambda e: self.descr.selection_clear(0, tk.END))
        self.descr.pack(side=tk.BOTTOM, fill=tk.X, expand=1)

    def _extra_info_label(self, text, var):
        frame = tkd.Frame(self, height=12, width=238)
        frame.propagate(False)
        frame.pack(expand=True, fill=tk.X)

        tkd.Label(frame, text='%s:' % text, font='helvetica 8', anchor=tk.W, justify=tk.LEFT).pack(side=tk.LEFT)
        tkd.Label(frame, textvariable=var, font='helvetica 8 bold', anchor=tk.W, justify=tk.LEFT).pack(side=tk.LEFT)

    def _add_new_profile(self, first_profile=False):
        # Ensure the pop-up is centered over the main program window
        xc = self.root.winfo_rootx() + self.root.winfo_width()//8
        yc = self.root.winfo_rooty() + self.root.winfo_height()//3
        profile = tk_utils.registration_form(root=self.root, coords=(xc, yc), first_profile=first_profile)
        if profile:
            profile_name = profile.pop('Profile name')
            profile['Game mode'] = 'Single Player' if profile['Game mode'] == '' else profile['Game mode']
            # Handle non-allowed profile names
            if profile_name == '':
                messagebox.showerror('No profile name', 'No profile name was entered. Please try again')
                return self._add_new_profile(first_profile=first_profile)
            elif profile_name.lower() == 'grail':
                messagebox.showerror('Reserved name', '"%s" is a reserved profile name, please choose another one.' % profile_name)
                return self._add_new_profile(first_profile=first_profile)
            if not first_profile and profile_name.lower() in [x.lower() for x in self.profile_dropdown['values']]:
                messagebox.showerror('Duplicate name', 'Profile name already in use - please choose another name.')
                return self._add_new_profile(first_profile=first_profile)

            # Add new profile to profile tab
            self.main_frame.profiles.append(profile_name)
            if not first_profile:
                self.profile_dropdown['values'] = self.main_frame.sorted_profiles()

            # Change active profile to the newly created profile
            self.active_profile.set(profile_name)

            # Create a save file for the new profile
            file = 'Profiles/%s.json' % self.active_profile.get()
            with open(file, 'w') as fo:
                json.dump({'extra_data': {**profile, 'Last update': time.time()}}, fo, indent=2)

            # Update active profile
            if not first_profile:
                self._change_active_profile()
        # Exit program if nothing is entered for first profile
        elif first_profile:
            sys.exit()

    def _change_active_profile(self):
        # Save state before changing profile, such that no information is lost. By design choice, if a run is currently
        # active, it will carry over to the next profile instead of being stopped first.
        self.main_frame.SaveActiveState()
        act = self.active_profile.get()
        self.main_frame.active_profile = act

        # Load extra data, defaulting to empty strings if no extra data is found in the new profile
        profile_cache = self.main_frame.load_state_file()
        self.extra_data = profile_cache.get('extra_data', dict())
        self.game_mode.set(self.extra_data.get('Game mode', 'Single Player'))
        self.run_type.set(self.extra_data.get('Run type', ''))
        self.char_name.set(self.extra_data.get('Character name', ''))

        # Update archive dropdown, and set selected archive to 'Active session'
        self.available_archive = ['Profile history', 'Active session'] + [x for x in profile_cache.keys() if x not in ['active_state', 'extra_data']]
        self.archive_dropdown['values'] = self.available_archive
        self.selected_archive.set('Profile history')

        # Load the new profile into the timer and drop module, and update the descriptive statistics
        self.main_frame.LoadActiveState(profile_cache)
        self.update_descriptive_statistics()
        if self.main_frame.automode:
            self.main_frame.toggle_automode(self.char_name.get())
        self.main_frame.options_tab.tab3.char_var.set(self.char_name.get())
        self.main_frame.options_tab.tab3.game_mode.set(self.game_mode.get())
        self.main_frame.timer_tab._set_laps(add_lap=self.main_frame.timer_tab.is_running)
        self.profile_dropdown['values'] = self.main_frame.sorted_profiles()

        self.auto_reset_session()

    def auto_reset_session(self):
        if self.main_frame.auto_archive_hours > 0:
            last_upd = float(self.extra_data.get('Last update', time.time()))
            elap_since = (time.time() - last_upd) / 3600
            if elap_since > self.main_frame.auto_archive_hours:
                self.main_frame.ArchiveReset(
                    confirm_msg='You have set auto archive to %s hours and %s hours has\n'
                                'passed since last change to the active session of this profile\n\n'
                                'Would you like to archive the active session?' % (self.main_frame.auto_archive_hours, round(elap_since, len(str(self.main_frame.auto_archive_hours).split('.')[-1]))),
                    stamp_from_epoch=last_upd
                )

    def _delete_profile(self):
        chosen = self.profile_dropdown.get()
        if chosen == '':
            # If nothing is selected the function returns
            return
        if len(self.profile_dropdown['values']) <= 1:
            tk.messagebox.showerror('Error', 'You need to have at least one profile, create a new profile before deleting this one.')
            return

        resp1 = tk_utils.mbox(msg='Are you sure you want to delete the profile "%s"?\nThis will permanently delete all records stored for the profile.' % chosen, title='WARNING')
        if resp1 is True:
            resp2 = tk_utils.mbox(msg='Are you really really sure you want to delete the profile "%s"?\nFinal warning!' % chosen, b1='Cancel', b2='OK', title='WARNING')
            if resp2 is False:  # False here because we switch buttons around in second confirmation
                file = 'Profiles/%s.json' % chosen
                os.remove(file)
                self.main_frame.profiles.remove(chosen)

                # We change active profile to an existing profile
                self.main_frame.active_profile = self.main_frame.profiles[0]
                self.active_profile.set(self.main_frame.profiles[0])
                self.profile_dropdown['values'] = self.main_frame.profiles
                self._change_active_profile()

    def delete_archived_session(self):
        chosen = self.archive_dropdown.get()
        if chosen == '':
            # If nothing is selected the function returns
            return
        if chosen == 'Profile history':
            tk.messagebox.showerror('Error', 'You cannot delete profile history from here. Please delete all sessions manually, or delete the profile instead')
            return

        resp = tk_utils.mbox(msg='Do you really want to delete the session "%s" from archive? It will be permanently deleted' % chosen, title='WARNING')
        if resp:
            if chosen == 'Active session':
                # Here we simply reset the timer module
                self.main_frame.ResetSession()
                self.main_frame.SaveActiveState()
                self.selected_archive.set('Profile history')
                self.update_descriptive_statistics()
            else:
                # Load the profile .json, delete the selected session and save the modified dictionary back to the .json
                cache = self.main_frame.load_state_file()
                # cache.setdefault('extra_data', dict())['Last update'] = time.time()
                removed = cache.pop(chosen, None)
                file = 'Profiles/%s.json' % self.active_profile.get()
                with open(file, 'w') as fo:
                    json.dump(cache, fo, indent=2)

                # Update archive dropdown and descriptive statistics
                self.available_archive.remove(chosen)
                self.archive_dropdown['values'] = self.available_archive
                self.selected_archive.set('Profile history')
                self.tot_laps -= len(removed.get('laps', []))
                self.main_frame.timer_tab._set_laps(self.main_frame.timer_tab.is_running)
                self.update_descriptive_statistics()
            self.profile_dropdown['values'] = self.main_frame.sorted_profiles()

    def update_descriptive_statistics(self):
        active = self.main_frame.load_state_file()
        chosen = self.archive_dropdown.get()
        self.tot_laps = len(sum([v.get('laps', []) for k, v in active.items() if k not in ['active_state', 'extra_data']], []))
        if chosen == 'Profile history':
            laps = []
            session_time = 0
            dropcount = 0
            # Concatenate information from each available session
            for key in [x for x in active.keys() if x not in ['active_state', 'extra_data']]:
                laps.extend(active[key].get('laps', []))
                session_time += active[key].get('session_time', 0)
                drops = active[key].get('drops', dict())
                for drop, val in drops.items():
                    dropcount += len(val)

            # Append data for active session from timer module
            laps.extend(self.main_frame.timer_tab.laps)
            session_time += self.main_frame.timer_tab.session_time
            for drop, val in self.main_frame.drops_tab.drops.items():
                dropcount += len(val)
        elif chosen == 'Active session':
            laps = self.main_frame.timer_tab.laps.copy()
            session_time = self.main_frame.timer_tab.session_time
            dropcount = sum(len(val) for val in self.main_frame.drops_tab.drops.values())
        else:
            laps = active[chosen].get('laps', [])
            session_time = active[chosen].get('session_time', 0)
            dropcount = sum(len(val) for val in active[chosen].get('drops', dict()).values())

        # Ensure no division by zero errors by defaulting to displaying 0
        sum_laps = sum(x['Run time'] if isinstance(x, dict) else x for x in laps)
        avg_lap = sum_laps / len(laps) if laps else 0
        pct = sum_laps * 100 / session_time if session_time > 0 else 0
        no_laps = len(laps) + 1 if self.main_frame.timer_tab.is_running and chosen in ['Active session', 'Profile history'] else len(laps)

        # (re-)Populate the listbox with descriptive statistics
        self.descr.delete(0, tk.END)
        self.descr.insert(tk.END, 'Total session time:   ' + utils.other_utils.build_time_str(session_time))
        self.descr.insert(tk.END, 'Total run time:       ' + utils.other_utils.build_time_str(sum_laps))
        self.descr.insert(tk.END, 'Average run time:     ' + utils.other_utils.build_time_str(avg_lap))
        self.descr.insert(tk.END, 'Fastest run time:     ' + utils.other_utils.build_time_str(min([x['Run time'] if isinstance(x, dict) else x for x in laps], default=0)))
        self.descr.insert(tk.END, 'Number of runs:       ' + str(no_laps))
        self.descr.insert(tk.END, 'Time spent in runs:   ' + str(round(pct, 2)) + '%')
        self.descr.insert(tk.END, 'Drops logged:         ' + str(dropcount))

    def open_archive_browser(self):
        chosen = self.archive_dropdown.get()
        if chosen == '':
            # If nothing is selected the function returns
            return

        # We build the new tkinter window to be opened
        new_win = tkd.Toplevel()
        new_win.title('Archive browser')
        new_win.wm_attributes('-topmost', 1)

        disp_coords = tk_utils.get_displaced_geom(self.main_frame.root, 400, 500)
        new_win.geometry(disp_coords)
        new_win.focus_get()
        new_win.iconbitmap(os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), media_path + 'icon.ico'))
        new_win.minsize(400, 500)
        tkd.Label(new_win, text='Archive browser', font='Helvetica 14').pack()

        tabcontrol = ttk.Notebook(new_win)
        tabcontrol.pack(expand=True, fill=tk.BOTH)

        statistics_fr = tkd.Frame(tabcontrol)
        tabcontrol.add(statistics_fr, text='Statistics')

        run_table_fr = tkd.Frame(tabcontrol)
        tabcontrol.add(run_table_fr, text='Run table')

        # Handle how loading of session data should be treated in the 3 different cases
        if chosen == 'Active session':
            # Load directly from timer module
            session_time = self.main_frame.timer_tab.session_time
            laps = self.main_frame.timer_tab.laps
            drops = self.main_frame.drops_tab.drops
        elif chosen == 'Profile history':
            # Load everything from profile .json, and append data from timer module
            active = self.main_frame.load_state_file()
            laps = []
            session_time = 0
            drops = dict()
            # Concatenate information from each available session
            for key in [x for x in active.keys() if x not in ['active_state', 'extra_data']]:
                session_drops = active[key].get('drops', dict())
                for run_no, run_drop in session_drops.items():
                    drops[str(int(run_no)+len(laps))] = run_drop
                laps.extend(active[key].get('laps', []))
                session_time += active[key].get('session_time', 0)

            # Append data for active session from timer module
            for run_no, run_drop in self.main_frame.drops_tab.drops.items():
                drops[str(int(run_no) + len(laps))] = run_drop
            laps.extend(self.main_frame.timer_tab.laps)
            session_time += self.main_frame.timer_tab.session_time
        else:
            # Load selected session data from profile .json
            active = self.main_frame.load_state_file()
            chosen_archive = active.get(chosen, dict())
            session_time = chosen_archive.get('session_time', 0)
            laps = chosen_archive.get('laps', [])
            drops = chosen_archive.get('drops', dict())

        cols = ["Run", "Run time", "Real time", "MF", "Players X", "XP Gained", "Uniques kills", "Champions kills", "Total kills"]
        tree_frame = tkd.Frame(run_table_fr)
        btn_frame2 = tkd.Frame(run_table_fr)
        btn_frame2.pack(side=tk.BOTTOM)

        vscroll_tree = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        hscroll_tree = ttk.Scrollbar(run_table_fr, orient=tk.HORIZONTAL)
        tree = tkd.Treeview(tree_frame, selectmode=tk.BROWSE, yscrollcommand=vscroll_tree.set, xscrollcommand=hscroll_tree.set, show='headings', columns=cols)
        hscroll_tree.config(command=tree.xview)
        vscroll_tree.config(command=tree.yview)
        tkd.Button(btn_frame2, text='Save as .csv', command=lambda: self.save_to_csv(tree)).pack(side=tk.LEFT, fill=tk.X)

        vscroll_tree.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        hscroll_tree.pack(side=tk.BOTTOM, fill=tk.X)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        tree['columns'] = cols
        for col in cols:
            tree.column(col, stretch=tk.YES, minwidth=0, width=80)
            if col in ['Run', 'XP Gained']:
                sort_by = 'num'
            else:
                sort_by = 'name'
            tree.heading(col, text=col, sort_by=sort_by)

        for n, lap in enumerate(laps, 1):
            compatible_lap = dict(lap) if isinstance(lap, dict) else {'Run time': lap}
            compatible_lap['Run time'] = utils.other_utils.build_time_str(compatible_lap['Run time'])
            compatible_lap['Run'] = n
            tree.insert('', tk.END, values=[compatible_lap.get(col, '') for col in cols])

        # Ensure no division by zero errors by defaulting to displaying 0
        sum_laps = sum(x['Run time'] if isinstance(x, dict) else x for x in laps)
        avg_lap = sum_laps / len(laps) if laps else 0
        pct = sum_laps * 100 / session_time if session_time > 0 else 0

        # Configure the list frame with scrollbars which displays the archive of the chosen session
        list_win = tkd.Frame(statistics_fr)
        list_frame = tkd.Frame(list_win)
        vscroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        hscroll = ttk.Scrollbar(list_win, orient=tk.HORIZONTAL)
        txt_list = tkd.Text(list_frame, yscrollcommand=vscroll.set, xscrollcommand=hscroll.set, font='courier 10', wrap=tk.WORD, state=tk.NORMAL, cursor='', exportselection=1, name='archivebrowser')
        # txt_list.bind('<FocusOut>', lambda e: txt_list.tag_remove(tk.SEL, "1.0", tk.END))  # Lose selection when shifting focus
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        txt_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        txt_list.tag_configure("HEADER", font=tkFont(family='courier', size=12, weight='bold', underline=True))
        hscroll.config(command=txt_list.xview)
        vscroll.config(command=txt_list.yview)

        # Build header for output file with information and descriptive statistics
        output = [['Statistics'],
                  ['Character name: ', self.extra_data.get('Character name', '')],
                  ['Run type:       ', self.extra_data.get('Run type', '')],
                  ['Game mode:      ', self.extra_data.get('Game mode', 'Single Player')],
                  [''],
                  ['Total session time:   ', utils.other_utils.build_time_str(session_time)],
                  ['Total run time:       ', utils.other_utils.build_time_str(sum_laps)],
                  ['Average run time:     ', utils.other_utils.build_time_str(avg_lap)],
                  ['Fastest run time:     ', utils.other_utils.build_time_str(min([x['Run time'] if isinstance(x, dict) else x for x in laps], default=0))],
                  ['Number of runs:       ', str(len(laps))],
                  ['Time spent in runs:   ', str(round(pct, 2)) + '%'],
                  ['']]

        # Backwards compatibility with old drop format
        for k, v in drops.items():
            for i in range(len(v)):
                if not isinstance(v[i], dict):
                    drops[k][i] = {'item_name': None, 'input': v[i], 'extra': ''}

        # List all drops collected
        if drops:
            if any(drop for drop in drops.values()):
                output.append(['Collected drops'])
            for run_no, drop in drops.items():
                if drop:
                    str_n = ' ' * max(len(str(len(laps))) - len(str(run_no)), 0) + str(run_no)
                    output.append(['Run ' + str_n, '', *[x['input'] for x in drop]])
            output.append([''])

        if laps:
            output.append(['Run times'])

        # Loop through all runs and add run times and drops for each run
        for n, lap in enumerate(laps, 1):
            run_time = lap['Run time'] if isinstance(lap, dict) else lap
            str_n = ' ' * max(len(str(len(laps))) - len(str(n)), 0) + str(n)
            droplst = drops.get(str(n), [])
            tmp = ['Run ' + str_n + ': ', utils.other_utils.build_time_str(run_time)]
            if droplst:
                tmp += [d['input'] for d in droplst]
            output.append(tmp)

        # Format string list to be shown in the archive browser
        for i, op in enumerate(output, 1):
            tmpstr = ''.join(op[:2])
            if len(op) > 2:
                tmpstr += ' --- ' + ', '.join(op[2:])
            if txt_list.get('1.0', tk.END) != '\n':
                tmpstr = '\n' + tmpstr
            txt_list.insert(tk.END, tmpstr)
            if op[0] in ['Statistics', 'Collected drops', 'Run times']:
                txt_list.tag_add("HEADER", str(i) + ".0", str(i) + ".0 lineend")

        # Add bold tags
        # txt_list.tag_add("BOLD", "1.0", "1.15")
        # txt_list.tag_add("BOLD", "2.0", "2.9")
        # txt_list.tag_add("BOLD", "3.0", "3.10")
        # txt_list.tag_add("BOLD", "5.0", "5.19")
        # txt_list.tag_add("BOLD", "6.0", "6.15")
        # txt_list.tag_add("BOLD", "7.0", "7.17")
        # txt_list.tag_add("BOLD", "8.0", "8.17")
        # txt_list.tag_add("BOLD", "9.0", "9.15")
        # txt_list.tag_add("BOLD", "10.0", "10.19")
        # txt_list.tag_add("BOLD", "1.16", "1.0 lineend")
        # txt_list.tag_add("BOLD", "2.16", "2.0 lineend")
        # txt_list.tag_add("BOLD", "3.16", "3.0 lineend")
        # txt_list.tag_add("BOLD", "5.20", "5.0 lineend")
        # txt_list.tag_add("BOLD", "6.20", "6.0 lineend")
        # txt_list.tag_add("BOLD", "7.20", "7.0 lineend")
        # txt_list.tag_add("BOLD", "8.20", "8.0 lineend")
        # txt_list.tag_add("BOLD", "9.20", "9.0 lineend")
        # txt_list.tag_add("BOLD", "10.20", "10.0 lineend")

        txt_list.tag_add("HEADER", "12.0", "12.0 lineend")

        txt_list.config(state=tk.DISABLED)

        btn_frame1 = tkd.Frame(statistics_fr)
        tkd.Button(btn_frame1, text='Copy to clipboard', command=lambda: self.copy_to_clipboard(new_win, txt_list.get(1.0, tk.END))).pack(side=tk.LEFT, fill=tk.X)
        tkd.Button(btn_frame1, text='Save as .txt', command=lambda: self.save_to_txt(txt_list.get(1.0, tk.END))).pack(side=tk.LEFT, fill=tk.X)

        # Packs all the buttons and UI in the archive browser. Packing order is very important:
        # TOP: Title first (furthest up), then list frame
        # BOTTOM: Buttons first (furthest down) and then horizontal scrollbar
        list_win.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        btn_frame1.pack(side=tk.BOTTOM)


        theme = Theme(self.main_frame.active_theme)
        theme.update_colors()

    @staticmethod
    def copy_to_clipboard(obj, string):
        """
        Clears current clipboard and adds the string instead
        """
        obj.clipboard_clear()
        obj.clipboard_append(string)

    @staticmethod
    def save_to_txt(string):
        """
        Writes a string to text file. Adds a line break every time '\n' is encountered in the string.
        'asksaveasfile' returns a writable object that then passes information on to the .txt file
        """
        f = tk.filedialog.asksaveasfile(mode='w', defaultextension='.txt', filetypes=(('.txt', '*.txt'), ('All Files', '*.*')))
        if not f:
            return
        f.write(string)
        f.close()

    @staticmethod
    def save_to_csv(tree):
        """
        Writes the run table to a .csv file

        Here we use asksaveasfilename in order to just return a path instead of writable object, because then we can
        initiate our own csv writer object with the newline='' option, which ensures we don't have double line breaks
        """
        f = tk.filedialog.asksaveasfilename(defaultextension='.csv', filetypes=(('.csv', '*.csv'), ('All Files', '*.*')))
        if not f:
            return
        with open(f, newline='', mode='w') as fo:
            writer = csv.writer(fo, delimiter=',')
            writer.writerow(tree['columns'])
            for row_id in tree.get_children():
                row = tree.item(row_id)['values']
                writer.writerow(row)
