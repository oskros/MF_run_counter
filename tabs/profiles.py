import utils.other_utils
from init import *
import csv
import json
import os
import sys
import tkinter as tk
from utils import tk_dynamic as tkd, tk_utils
from utils.color_themes import Theme
from tkinter import ttk, messagebox, filedialog


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

        profile_frame = tkd.Frame(self, height=28, width=238, pady=2, padx=2)
        profile_frame.propagate(False)
        profile_frame.pack()

        # if self.main_frame.active_theme != 'default':
        #     self.option_add("*TCombobox*Listbox*Background", self.main_frame.entry_color)
        #     self.option_add("*TCombobox*Listbox*Foreground", self.main_frame.combo_listbox_foreground)
        #     self.option_add("*TCombobox*Listbox*selectBackground", self.main_frame.combo_listbox_selectbackground)
        #     self.option_add("*TCombobox*Listbox*selectForeground", self.main_frame.combo_listbox_selectforeground)
        self.active_profile.set(self.main_frame.active_profile)
        self.profile_dropdown = ttk.Combobox(profile_frame, textvariable=self.active_profile, state='readonly', values=self.main_frame.profiles)
        self.profile_dropdown.bind("<<ComboboxSelected>>", lambda e: self._change_active_profile())
        self.profile_dropdown.bind("<FocusOut>", lambda e: self.profile_dropdown.selection_clear())
        self.profile_dropdown.pack(side=tk.LEFT, expand=True, fill=tk.X)

        tkd.Button(profile_frame, text='New...', command=self._add_new_profile).pack(side=tk.LEFT)
        tkd.Button(profile_frame, text='Delete', command=self._delete_profile).pack(side=tk.LEFT)

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
        # self.archive_dropdown.bind("<Right>", lambda e: self.archive_dropdown.set(self.archive_dropdown.current()+1))
        self.archive_dropdown.pack(side=tk.LEFT)

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
                self._add_new_profile(first_profile=first_profile)
                return
            elif profile_name == 'grail':
                messagebox.showerror('Reserved name', '"grail" is a reserved profile name, please choose another one.')
                self._add_new_profile(first_profile=first_profile)
                return
            if not first_profile and profile_name in self.profile_dropdown['values']:
                messagebox.showerror('Duplicate name', 'Profile name already in use - please choose another name.')
                self._add_new_profile(first_profile=first_profile)
                return

            # Add new profile to profile tab
            self.main_frame.profiles.append(profile_name)
            if not first_profile:
                self.profile_dropdown['values'] = self.main_frame.profiles

            # Change active profile to the newly created profile
            self.active_profile.set(profile_name)

            # Create a save file for the new profile
            file = 'Profiles/%s.json' % self.active_profile.get()
            with open(file, 'w') as fo:
                json.dump({'extra_data': profile}, fo, indent=2)

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
            self.main_frame.toggle_automode(self.char_name.get(), self.game_mode.get())
        self.main_frame.options_tab.tab3.char_var.set(self.char_name.get())
        self.main_frame.options_tab.tab3.game_mode.set(self.game_mode.get())
        self.main_frame.timer_tab._set_laps(add_lap=self.main_frame.timer_tab.is_running)

    def _delete_profile(self):
        chosen = self.profile_dropdown.get()
        if chosen == '':
            # If nothing is selected the function returns
            return
        if len(self.profile_dropdown['values']) <= 1:
            tk.messagebox.showerror('Error', 'You need to have at least one profile, create a new profile before deleting this one.')
            return

        resp1 = tk_utils.mbox(msg='Are you sure you want to delete this profile?\nThis will permanently delete all records stored for the profile.', title='WARNING')
        if resp1 is True:
            resp2 = tk_utils.mbox(msg='Are you really really sure you want to delete the profile?\nFinal warning!', b1='Cancel', b2='OK', title='WARNING')
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

        resp = tk_utils.mbox(msg='Do you really want to delete this session from archive? It will be permanently deleted', title='WARNING')
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
            if self.main_frame.timer_tab.is_running:
                laps.extend([0])
            session_time += self.main_frame.timer_tab.session_time
            for drop, val in self.main_frame.drops_tab.drops.items():
                dropcount += len(val)
        elif chosen == 'Active session':
            laps = self.main_frame.timer_tab.laps.copy()
            if self.main_frame.timer_tab.is_running:
                laps.extend([0])
            session_time = self.main_frame.timer_tab.session_time
            dropcount = sum(len(val) for val in self.main_frame.tab2.drops.values())
        else:
            laps = active[chosen].get('laps', [])
            session_time = active[chosen].get('session_time', 0)
            dropcount = sum(len(val) for val in active[chosen].get('drops', dict()))

        # Ensure no division by zero errors by defaulting to displaying 0
        avg_lap = sum(laps) / len(laps) if laps else 0
        pct = sum(laps) * 100 / session_time if session_time > 0 else 0

        # (re-)Populate the listbox with descriptive statistics
        self.descr.delete(0, tk.END)
        self.descr.insert(tk.END, 'Total session time:   ' + utils.other_utils.build_time_str(session_time))
        self.descr.insert(tk.END, 'Total run time:       ' + utils.other_utils.build_time_str(sum(laps)))
        self.descr.insert(tk.END, 'Average run time:     ' + utils.other_utils.build_time_str(avg_lap))
        self.descr.insert(tk.END, 'Fastest run time:     ' + utils.other_utils.build_time_str(min(laps, default=0)))
        self.descr.insert(tk.END, 'Time spent in runs: ' + str(round(pct, 2)) + '%')
        self.descr.insert(tk.END, 'Number of runs: ' + str(len(laps)))
        self.descr.insert(tk.END, 'Drops logged: ' + str(dropcount))

    def open_archive_browser(self):
        chosen = self.archive_dropdown.get()
        if chosen == '':
            # If nothing is selected the function returns
            return

        # We build the new tkinter window to be opened
        new_win = tkd.Toplevel()
        new_win.title('Archive browser')
        new_win.wm_attributes('-topmost', 1)

        disp_coords = tk_utils.get_displaced_geom(self.main_frame.root, 450, 450)
        new_win.geometry(disp_coords)
        new_win.focus_get()
        new_win.iconbitmap(os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), media_path + 'icon.ico'))
        title = tkd.Label(new_win, text='Archive browser', font='Helvetica 14')

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

        # Ensure no division by zero errors by defaulting to displaying 0
        avg_lap = sum(laps) / len(laps) if laps else 0
        pct = sum(laps) * 100 / session_time if session_time > 0 else 0

        # Configure the list frame with scrollbars which displays the archive of the chosen session
        list_frame = tkd.Frame(new_win)
        vscroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        hscroll = ttk.Scrollbar(new_win, orient=tk.HORIZONTAL)
        txt_list = tkd.Listbox(list_frame, selectmode=tk.EXTENDED, yscrollcommand=vscroll.set, xscrollcommand=hscroll.set, activestyle='none', font=('courier', 10))
        txt_list.bind('<FocusOut>', lambda e: txt_list.selection_clear(0, tk.END))  # Lose selection when shifting focus
        txt_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        hscroll.config(command=txt_list.xview)
        vscroll.config(command=txt_list.yview)
        vscroll.pack(side=tk.LEFT, fill=tk.Y)

        # Build header for output file with information and descriptive statistics
        output = [['Character name: ', self.extra_data.get('Character name', '')],
                  ['Run type: ', self.extra_data.get('Run type', '')],
                  ['Game mode: ', self.extra_data.get('Game mode', 'Single Player')],
                  [''],
                  ['Total session time:   ', utils.other_utils.build_time_str(session_time)],
                  ['Total run time:       ', utils.other_utils.build_time_str(sum(laps))],
                  ['Average run time:     ', utils.other_utils.build_time_str(avg_lap)],
                  ['Fastest run time:     ', utils.other_utils.build_time_str(min(laps, default=0))],
                  ['Number of runs:       ', str(len(laps))],
                  ['Time spent in runs: ', str(round(pct, 2)) + '%'],
                  ['']]

        # Backwards compatibility with old drop format
        for k, v in drops.items():
            for i in range(len(v)):
                if not isinstance(v[i], dict):
                    drops[k][i] = {'item_name': None, 'input': v[i], 'extra': ''}

        # If drops were added before first run is started, we make sure to include them in output anyway
        if '0' in drops.keys():
            output.append(['Run 0: ', 'NO_TIME', *[d['input'] for d in drops['0']]])

        # Loop through all runs and add run times and drops for each run
        for n, lap in enumerate(laps, 1):
            str_n = ' ' * max(len(str(len(laps))) - len(str(n)), 0) + str(n)
            droplst = drops.get(str(n), [])
            tmp = ['Run ' + str_n + ': ', utils.other_utils.build_time_str(lap)]
            if droplst:
                tmp += [d['input'] for d in droplst]
            output.append(tmp)

        # List all drops collected and show them below the individual runs (good for doing data work on output file)
        out_drops = sorted(sum(drops.values(), []), key=lambda x: x['input'])
        if out_drops:
            output.append([''])
            output.append(['All listed drops:'])
            for drop in out_drops:
                output.append([drop['input']])
            # for drop in drops:
            #     output.append(['Run ' + str(drop['Run']) + ': ', drop['Name'] + ' ' + drop['Stats']])

        # Format string list to be shown in the archive browser
        for op in output:
            tmpstr = ''.join(op[:2])
            if len(op) > 2:
                tmpstr += ' --- ' + ', '.join(op[2:])
            txt_list.insert(tk.END, tmpstr)

        button_frame = tkd.Frame(new_win)
        tkd.Button(button_frame, text='Copy to clipboard', command=lambda: self.copy_to_clipboard(new_win, '\n'.join(txt_list.get(0, tk.END)))).pack(side=tk.LEFT, fill=tk.X)
        tkd.Button(button_frame, text='Save as .txt', command=lambda: self.save_to_txt('\n'.join(txt_list.get(0, tk.END)))).pack(side=tk.LEFT, fill=tk.X)
        tkd.Button(button_frame, text='Save as .csv', command=lambda: self.save_to_csv(output)).pack(side=tk.LEFT, fill=tk.X)

        # Packs all the buttons and UI in the archive browser. Packing order is very important:
        # TOP: Title first (furthest up), then list frame
        # BOTTOM: Buttons first (furthest down) and then horizontal scrollbar
        title.pack(side=tk.TOP)
        list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        button_frame.pack(side=tk.BOTTOM)
        hscroll.pack(side=tk.BOTTOM, fill=tk.X)

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
    def save_to_csv(string_lst):
        """
        Writes a list of lists of strings to a .csv file

        Here we use asksaveasfilename in order to just return a path instead of writable object, because then we can
        initiate our own csv writer object with the newline='' option, which ensures we don't have double line breaks
        """
        string_lst_corr = list()
        for s in string_lst:
            if s[0].lower().startswith('run'):
                tmp = [s[0][:s[0].find(':')]] + s[1:]
                string_lst_corr.append([' '.join(x.split()) for x in tmp])
            else:
                string_lst_corr.append([' '.join(x.split()) for x in s])
        f = tk.filedialog.asksaveasfilename(defaultextension='.csv', filetypes=(('.csv', '*.csv'), ('All Files', '*.*')))
        if not f:
            return
        with open(f, newline='', mode='w') as fo:
            writer = csv.writer(fo, delimiter=',')
            writer.writerows(string_lst_corr)
