from init import *
import csv
import json
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tk_utils


class Profile(tk.Frame):
    def __init__(self, main_frame, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
        self.config(bg=main_frame.frame_color)
        self.root = parent
        self.main_frame = main_frame

        state = self.main_frame.load_state_file()
        self.available_archive = ['Active session', 'Profile history'] + [x for x in state.keys() if x not in ['active_state', 'extra_data']]
        self.selected_archive = tk.StringVar()
        self.selected_archive.set('Active session')
        self.extra_data = self.main_frame.load_state_file().get('extra_data', dict())

        self._make_widgets()

    def _make_widgets(self):
        tk.Label(self, text='Select active profile', justify=tk.LEFT, bg=self.main_frame.label_color, fg=self.main_frame.text_color).pack(anchor=tk.W)

        profile_frame = tk.Frame(self, height=28, width=238, pady=2, padx=2, bg=self.main_frame.frame_color)
        profile_frame.propagate(False)
        profile_frame.pack()

        if self.main_frame.active_theme != 'default':
            self.option_add("*TCombobox*Listbox*Background", self.main_frame.entry_color)
            self.option_add("*TCombobox*Listbox*Foreground", 'black')
            self.option_add("*TCombobox*Listbox*selectBackground", 'black')
            self.option_add("*TCombobox*Listbox*selectForeground", 'white')
        self.active_profile = tk.StringVar()
        self.active_profile.set(self.main_frame.active_profile)
        self.profile_dropdown = ttk.Combobox(profile_frame, textvariable=self.active_profile, state='readonly', values=self.main_frame.profiles)
        self.profile_dropdown.bind("<<ComboboxSelected>>", lambda e: self._change_active_profile())
        self.profile_dropdown.bind("<FocusOut>", lambda e: self.profile_dropdown.selection_clear())
        self.profile_dropdown.pack(side=tk.LEFT, expand=True, fill=tk.X)

        tk.Button(profile_frame, text='New...', command=self._add_new_profile, bg=self.main_frame.button_color, fg=self.main_frame.text_color).pack(side=tk.LEFT)
        tk.Button(profile_frame, text='Delete', command=self._delete_profile, bg=self.main_frame.button_color, fg=self.main_frame.text_color).pack(side=tk.LEFT)

        extra_info1 = tk.Frame(self, height=12, width=238, bg=self.main_frame.frame_color)
        extra_info1.propagate(False)
        extra_info1.pack(expand=True, fill=tk.X)
        extra_info2 = tk.Frame(self, height=12, width=238, bg=self.main_frame.frame_color)
        extra_info2.propagate(False)
        extra_info2.pack(expand=True, fill=tk.X)

        self.run_type = tk.StringVar(extra_info1, value=self.extra_data.get('Run type', ''))
        tk.Label(extra_info1, text='Run type:', font='helvetica 8', anchor=tk.W, justify=tk.LEFT, bg=self.main_frame.label_color, fg=self.main_frame.text_color).pack(side=tk.LEFT)
        tk.Label(extra_info1, textvariable=self.run_type, font='helvetica 8 bold', anchor=tk.W, justify=tk.LEFT, bg=self.main_frame.label_color, fg=self.main_frame.text_color).pack(side=tk.LEFT)

        self.mf_amount = tk.StringVar(extra_info1, value=self.extra_data.get('Active MF %', ''))
        tk.Label(extra_info1, textvariable=self.mf_amount, font='helvetica 8 bold', anchor=tk.E, justify=tk.RIGHT, bg=self.main_frame.label_color, fg=self.main_frame.text_color).pack(side=tk.RIGHT)
        tk.Label(extra_info1, text='MF amount %:', font='helvetica 8', anchor=tk.W, justify=tk.RIGHT, bg=self.main_frame.label_color, fg=self.main_frame.text_color).pack(side=tk.RIGHT)

        self.char_name = tk.StringVar(extra_info1, value=self.extra_data.get('Character name', ''))
        tk.Label(extra_info2, text='Character:', font='helvetica 8', anchor=tk.W, justify=tk.LEFT, bg=self.main_frame.label_color, fg=self.main_frame.text_color).pack(side=tk.LEFT)
        tk.Label(extra_info2, textvariable=self.char_name, font='helvetica 8 bold', anchor=tk.W, justify=tk.LEFT, bg=self.main_frame.label_color, fg=self.main_frame.text_color).pack(side=tk.LEFT)

        tk.Label(self, text='Select an archived run for this profile', justify=tk.LEFT, bg=self.main_frame.label_color, fg=self.main_frame.text_color).pack(anchor=tk.W, pady=(6,0))
        sel_frame = tk.Frame(self, height=28, width=238, pady=2, padx=2, bg=self.main_frame.frame_color)
        sel_frame.propagate(False)
        sel_frame.pack()
        self.archive_dropdown = ttk.Combobox(sel_frame, textvariable=self.selected_archive, state='readonly', values=self.available_archive)
        self.archive_dropdown.bind("<FocusOut>", lambda e: self.archive_dropdown.selection_clear())
        self.archive_dropdown.pack(side=tk.LEFT)

        tk.Button(sel_frame, text='Open', command=self.open_archive_browser, bg=self.main_frame.button_color, fg=self.main_frame.text_color).pack(side=tk.LEFT)
        tk.Button(sel_frame, text='Delete', command=self.delete_archived_session, bg=self.main_frame.button_color, fg=self.main_frame.text_color).pack(side=tk.LEFT)

        tk.Label(self, text='Descriptive statistics for current profile', justify=tk.LEFT, bg=self.main_frame.label_color, fg=self.main_frame.text_color).pack(anchor=tk.W, pady=(6,0))

        self.descr = tk.Listbox(self, selectmode=tk.EXTENDED, height=7, activestyle='none', font=('courier', 8), bg=self.main_frame.listbox_color, fg=self.main_frame.listbox_text, highlightbackground=self.main_frame.border_color)
        self.descr.bind('<FocusOut>', lambda e: self.descr.selection_clear(0, tk.END))
        self.descr.pack(side=tk.BOTTOM, fill=tk.X, expand=1)
        self.update_descriptive_statistics()

    def _add_new_profile(self):
        # Ensure the pop-up is centered over the main program window
        xc = self.root.winfo_rootx() + self.root.winfo_width()//8
        yc = self.root.winfo_rooty() + self.root.winfo_height()//3
        profile = tk_utils.registration_form((xc, yc))
        if profile:
            profile_name = profile.pop('Profile name')
            # Handle non-allowed profile names
            if profile_name == '':
                messagebox.showerror('No profile name', 'No profile name was entered. Please try again')
                return
            if profile_name in self.profile_dropdown['values']:
                messagebox.showerror('Duplicate name', 'Profile name already in use - please choose another name.')
                return

            # Add new profile to profile tab
            self.main_frame.profiles.append(profile_name)
            self.profile_dropdown['values'] = self.main_frame.profiles

            # Change active profile to the newly created profile
            self.active_profile.set(profile_name)
            self._change_active_profile()

            # Create a save file for the new profile
            file = 'Profiles/%s.json' % self.active_profile.get()
            with open(file, 'w') as fo:
                json.dump({'extra_data': profile}, fo, indent=2)

    def _change_active_profile(self):
        # Save state before changing profile, such that no information is lost. By design choice, if a run is currently
        # active, it will carry over to the next profile instead of being stopped first.
        self.main_frame.SaveActiveState()
        act = self.active_profile.get()
        self.main_frame.active_profile = act

        # Load extra data, defaulting to empty strings if no extra data is found in the new profile
        profile_cache = self.main_frame.load_state_file()
        self.extra_data = profile_cache.get('extra_data', dict())
        self.mf_amount.set(self.extra_data.get('Active MF %', ''))
        self.run_type.set(self.extra_data.get('Run type', ''))
        self.char_name.set(self.extra_data.get('Character name', ''))

        # Update archive dropdown, and set selected archive to 'Active session'
        self.available_archive = ['Active session', 'Profile history'] + [x for x in profile_cache.keys() if x not in ['active_state', 'extra_data']]
        self.archive_dropdown['values'] = self.available_archive
        self.selected_archive.set('Active session')

        # Load the new profile into the timer and drop module, and update the descriptive statistics
        self.main_frame.LoadActiveState(profile_cache)
        self.update_descriptive_statistics()

    def _delete_profile(self):
        chosen = self.profile_dropdown.get()
        if chosen == '':
            # If nothing is selected the function returns
            return
        if len(self.profile_dropdown['values']) <= 1:
            tk.messagebox.showerror('Error', 'You need to have at least one profile, create a new profile before deleting this one.')
            return

        # Open window at the center of the application
        xc = self.root.winfo_rootx() + self.root.winfo_width()//8
        yc = self.root.winfo_rooty() + self.root.winfo_height()//3
        resp1 = tk_utils.mbox(msg='Are you sure you want to delete this profile? This will permanently delete all records stored for the profile.', title='WARNING', coords=(xc, yc))
        if resp1 is True:
            resp2 = tk_utils.mbox(msg='Are you really really sure you want to delete the profile? Final warning!', b1='Cancel', b2='OK', title='WARNING', coords=(xc,yc))
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

        # Open window at the center of the application
        xc = self.root.winfo_rootx() + self.root.winfo_width()//8
        yc = self.root.winfo_rooty() + self.root.winfo_height()//3
        resp = tk_utils.mbox(msg='Do you really want to delete this session from archive? It will be permanently deleted', title='WARNING', coords=(xc, yc))
        if resp:
            if chosen == 'Active session':
                # Here we simply reset the timer module
                self.main_frame.ResetSession()
                self.main_frame.SaveActiveState()
                self.selected_archive.set('Active session')
                return

            # Load the profile .json, delete the selected session and save the modified dictionary back to the .json
            cache = self.main_frame.load_state_file()
            cache.pop(chosen, None)
            file = 'Profiles/%s.json' % self.active_profile.get()
            with open(file, 'w') as fo:
                json.dump(cache, fo, indent=2)

            # Update archive dropdown and descriptive statistics
            self.available_archive.remove(chosen)
            self.archive_dropdown['values'] = self.available_archive
            self.selected_archive.set('Active session')
            self.update_descriptive_statistics()

    def update_descriptive_statistics(self):
        active = self.main_frame.load_state_file()
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
        laps.extend(self.main_frame.tab1.laps)
        session_time += self.main_frame.tab1.session_time
        for drop, val in self.main_frame.tab2.drops.items():
            dropcount += len(val)

        # Ensure no division by zero errors by defaulting to displaying 0
        avg_lap = sum(laps) / len(laps) if laps else 0
        pct = sum(laps) * 100 / session_time if session_time > 0 else 0

        # (re-)Populate the listbox with descriptive statistics
        self.descr.delete(0, tk.END)
        self.descr.insert(tk.END, 'Total session time:   ' + tk_utils.build_time_str(session_time))
        self.descr.insert(tk.END, 'Total run time:       ' + tk_utils.build_time_str(sum(laps)))
        self.descr.insert(tk.END, 'Average run time:     ' + tk_utils.build_time_str(avg_lap))
        self.descr.insert(tk.END, 'Fastest run time:     ' + tk_utils.build_time_str(min(laps, default=0)))
        self.descr.insert(tk.END, 'Time spent in runs: ' + str(round(pct, 2)) + '%')
        self.descr.insert(tk.END, 'Number of runs: ' + str(len(laps)))
        self.descr.insert(tk.END, 'Drops logged: ' + str(dropcount))

    def open_archive_browser(self):
        chosen = self.archive_dropdown.get()
        if chosen == '':
            # If nothing is selected the function returns
            return

        # We build the new tkinter window to be opened
        new_win = tk.Toplevel()
        new_win.config(bg=self.main_frame.frame_color)
        new_win.title('Archive browser')
        new_win.wm_attributes('-topmost', 1)
        new_win.geometry('450x450')
        new_win.geometry('+%d+%d' % (self.main_frame.root.winfo_rootx(), self.main_frame.root.winfo_rooty()))
        new_win.focus_get()
        new_win.iconbitmap(os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), media_path + 'icon.ico'))
        title = tk.Label(new_win, text='Archive browser', font='Helvetica 14', bg=self.main_frame.label_color, fg=self.main_frame.text_color)

        # Handle how loading of session data should be treated in the 3 different cases
        if chosen == 'Active session':
            # Load directly from timer module
            session_time = self.main_frame.tab1.session_time
            laps = self.main_frame.tab1.laps
            drops = self.main_frame.tab2.drops
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
            for run_no, run_drop in self.main_frame.tab2.drops.items():
                drops[str(int(run_no) + len(laps))] = run_drop
            laps.extend(self.main_frame.tab1.laps)
            session_time += self.main_frame.tab1.session_time
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
        list_frame = tk.Frame(new_win, bg=self.main_frame.frame_color)
        vscroll = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        hscroll = tk.Scrollbar(new_win, orient=tk.HORIZONTAL)
        txt_list = tk.Listbox(list_frame, selectmode=tk.EXTENDED, yscrollcommand=vscroll.set, xscrollcommand=hscroll.set, activestyle='none', font=('courier', 10), bg=self.main_frame.listbox_color, fg=self.main_frame.listbox_text, highlightbackground=self.main_frame.border_color)
        txt_list.bind('<FocusOut>', lambda e: txt_list.selection_clear(0, tk.END))  # Lose selection when shifting focus
        txt_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        hscroll.config(command=txt_list.xview)
        vscroll.config(command=txt_list.yview)
        vscroll.pack(side=tk.LEFT, fill=tk.Y)

        # Build header for output file with information and descriptive statistics
        output = [['Character name: ', self.extra_data.get('Character name', '')],
                  ['Run type: ', self.extra_data.get('Run type', '')],
                  ['Active MF %: ', self.extra_data.get('Active MF %', '')],
                  [''],
                  ['Total session time:   ', tk_utils.build_time_str(session_time)],
                  ['Total run time:       ', tk_utils.build_time_str(sum(laps))],
                  ['Average run time:     ', tk_utils.build_time_str(avg_lap)],
                  ['Fastest run time:     ', tk_utils.build_time_str(min(laps, default=0))],
                  ['Time spent in runs: ', str(round(pct, 2)) + '%'],
                  ['']]

        # If drops were added before first run is started, we make sure to include them in output anyway
        if '0' in drops.keys():
            output.append(['Run 0: ', 'NO_TIME', *drops['0']])

        # Loop through all runs and add run times and drops for each run
        for n, lap in enumerate(laps, 1):
            str_n = ' ' * max(len(str(len(laps))) - len(str(n)), 0) + str(n)
            droplst = drops.get(str(n), [])
            tmp = ['Run ' + str_n + ': ', tk_utils.build_time_str(lap)]
            if droplst:
                tmp += droplst
            output.append(tmp)

        # Format string list to be shown in the archive browser
        for op in output:
            tmpstr = ''.join(op[:2])
            if len(op) > 2:
                tmpstr += ' --- ' + ', '.join(op[2:])
            txt_list.insert(tk.END, tmpstr)

        button_frame = tk.Frame(new_win, bg=self.main_frame.frame_color)
        tk.Button(button_frame, text='Copy to clipboard', command=lambda: self.copy_to_clipboard(new_win, '\n'.join(txt_list.get(0, tk.END))), bg=self.main_frame.button_color, fg=self.main_frame.text_color).pack(side=tk.LEFT, fill=tk.X)
        tk.Button(button_frame, text='Save as .txt', command=lambda: self.save_to_txt('\n'.join(txt_list.get(0, tk.END))), bg=self.main_frame.button_color, fg=self.main_frame.text_color).pack(side=tk.LEFT, fill=tk.X)
        tk.Button(button_frame, text='Save as .csv', command=lambda: self.save_to_csv(output), bg=self.main_frame.button_color, fg=self.main_frame.text_color).pack(side=tk.LEFT, fill=tk.X)

        # Packs all the buttons and UI in the archive browser. Packing order is very important:
        # TOP: Title first (furthest up), then list frame
        # BOTTOM: Buttons first (furthest down) and then horizontal scrollbar
        title.pack(side=tk.TOP)
        list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        button_frame.pack(side=tk.BOTTOM)
        hscroll.pack(side=tk.BOTTOM, fill=tk.X)

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
        initiate our own csv writer opbject with the newline='' option, which ensures we don't have double line breaks
        """
        f = tk.filedialog.asksaveasfilename(defaultextension='.csv', filetypes=(('.csv', '*.csv'), ('All Files', '*.*')))
        if not f:
            return
        with open(f, newline='', mode='w') as fo:
            writer = csv.writer(fo, delimiter=',')
            writer.writerows(string_lst)