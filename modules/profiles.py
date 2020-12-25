import utils.other_utils
import json
import os
import sys
import time
import tkinter as tk
from modules import archive_browser
from utils import tk_dynamic as tkd, tk_utils, other_utils
from tkinter import ttk, messagebox


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
        self.available_archive = ['Profile history', 'Active session'] + sorted([x for x in state.keys() if x not in ['active_state', 'extra_data']], reverse=True)
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
        self.profile_dropdown = tkd.Combobox(profile_dropdown_frame, textvariable=self.active_profile, state='readonly', values=self.main_frame.profiles)
        self.profile_dropdown.bind("<<ComboboxSelected>>", lambda e: self._change_active_profile())
        self.profile_dropdown.bind("<FocusOut>", lambda e: self.profile_dropdown.selection_clear())
        self.profile_dropdown.pack(side=tk.LEFT, expand=True, fill=tk.X)

        tkd.Button(profile_dropdown_frame, text='New...', command=self._add_new_profile).pack(side=tk.LEFT)
        tkd.Button(profile_dropdown_frame, text='Delete', command=self._delete_profile).pack(side=tk.LEFT)

        self.run_type = tk.StringVar(self, value=self.extra_data.get('Run type', ''))
        self.game_mode = tk.StringVar(self, value=self.extra_data.get('Game mode', 'Single Player'))
        self.char_name = tk.StringVar(self, value=self.extra_data.get('Character name', ''))
        self._extra_info_label('Run type', self.run_type)
        # self._extra_info_label('Game mode', self.game_mode)
        self._extra_info_label('Character name', self.char_name)

        tkd.Label(self, text='Select an archived run for this profile', justify=tk.LEFT).pack(anchor=tk.W, pady=(6, 0))
        sel_frame = tkd.Frame(self, height=28, width=238, pady=2, padx=2)
        sel_frame.propagate(False)
        sel_frame.pack()
        self.archive_dropdown = tkd.Combobox(sel_frame, textvariable=self.selected_archive, state='readonly', values=self.available_archive)
        self.archive_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_descriptive_statistics())
        self.archive_dropdown.bind("<FocusOut>", lambda e: self.archive_dropdown.selection_clear())
        self.archive_dropdown.pack(side=tk.LEFT, expand=True, fill=tk.X)

        tkd.Button(sel_frame, text='Open', command=lambda: archive_browser.ArchiveBrowser(self.main_frame)).pack(side=tk.LEFT)
        tkd.Button(sel_frame, text='Delete', command=self.delete_archived_session).pack(side=tk.LEFT)

        self.descr = tkd.Listbox(self, selectmode=tk.EXTENDED, height=8, activestyle='none', font=('courier', 8))
        self.descr.bind('<FocusOut>', lambda e: self.descr.selection_clear(0, tk.END))
        self.descr.pack(side=tk.BOTTOM, fill=tk.X, expand=1, anchor=tk.S)

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
        profile = tk_utils.registration_form(master=self.main_frame, coords=(xc, yc), first_profile=first_profile)
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
            other_utils.atomic_json_dump(file, {'extra_data': {**profile, 'Last update': time.time()}})

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
        self.available_archive = ['Profile history', 'Active session'] + sorted([x for x in profile_cache.keys() if x not in ['active_state', 'extra_data']], reverse=True)
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

        resp = tk_utils.mbox(msg='Type "DELETE" to confirm you wish to delete the profile "%s"\n\nThis will permanently delete all records stored for the profile.' % chosen, title='WARNING', disabled_btn_input='DELETE')
        if resp == 'DELETE':
            file = 'Profiles/%s.json' % chosen
            os.remove(file)
            self.main_frame.profiles.remove(chosen)
            self.profile_dropdown['values'] = self.main_frame.profiles

            # We change active profile to an existing profile
            self.active_profile.set(self.main_frame.profiles[0])
            self._change_active_profile()

    def delete_archived_session(self):
        chosen = self.archive_dropdown.get()
        if chosen == '':
            # If nothing is selected the function returns
            return
        if chosen == 'Profile history':
            tk.messagebox.showerror('Error', 'You cannot delete profile history from here. Please delete all sessions manually, or delete the profile instead')
            return

        resp = tk_utils.mbox(msg='Type "DELETE" to confirm you wish to delete the session "%s" from archive\n\nIt will be permanently deleted' % chosen, title='WARNING', disabled_btn_input='DELETE')
        if resp == 'DELETE':
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
                other_utils.atomic_json_dump(file, cache)

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
                for drops in drops.values():
                    dropcount += len(drops)

            # Append data for active session from timer module
            laps.extend(self.main_frame.timer_tab.laps)
            session_time += self.main_frame.timer_tab.session_time
            for drops in self.main_frame.drops_tab.drops.values():
                dropcount += len(drops)
        elif chosen == 'Active session':
            laps = self.main_frame.timer_tab.laps.copy()
            session_time = self.main_frame.timer_tab.session_time
            dropcount = sum(len(drops) for drops in self.main_frame.drops_tab.drops.values())
        else:
            laps = active[chosen].get('laps', [])
            session_time = active[chosen].get('session_time', 0)
            dropcount = sum(len(drops) for drops in active[chosen].get('drops', dict()).values())

        # Ensure no division by zero errors by defaulting to displaying 0
        sum_laps = sum(x['Run time'] if isinstance(x, dict) else x for x in laps)
        avg_lap = sum_laps / len(laps) if laps else 0
        min_lap = min([x['Run time'] if isinstance(x, dict) else x for x in laps], default=0)
        pct = sum_laps * 100 / session_time if session_time > 0 else 0
        no_laps = len(laps) + 1 if self.main_frame.timer_tab.is_running and chosen in ['Active session', 'Profile history'] else len(laps)

        list_uniques = [int(x.get('Uniques kills', '')) for x in laps if isinstance(x, dict) and x.get('Uniques kills', '')]
        list_champs = [int(x.get('Champions kills', '')) for x in laps if isinstance(x, dict) and x.get('Uniques kills', '')]
        avg_uniques = sum(list_uniques) / len(list_uniques) if list_uniques else 0
        avg_champs = sum(list_champs) / len(list_champs) if list_champs else 0
        avg_packs = avg_uniques + avg_champs / 2.534567

        # (re-)Populate the listbox with descriptive statistics
        self.descr.delete(0, tk.END)
        self.descr.insert(tk.END, 'Total session time: ' + self.build_padded_str(session_time))
        self.descr.insert(tk.END, 'Total run time:     ' + self.build_padded_str(sum_laps))
        self.descr.insert(tk.END, 'Average run time:   ' + self.build_padded_str(avg_lap))
        self.descr.insert(tk.END, 'Fastest run time:   ' + self.build_padded_str(min_lap))
        self.descr.insert(tk.END, 'Time spent in runs:   ' + str(round(pct, 2)) + '%')
        self.descr.insert(tk.END, 'Number of runs:       ' + str(no_laps))
        self.descr.insert(tk.END, 'Average packs:        ' + str(round(avg_packs, 2)))
        self.descr.insert(tk.END, 'Drops logged:         ' + str(dropcount))

    @staticmethod
    def build_padded_str(inp):
        inp = utils.other_utils.build_time_str(inp)
        return ' '*(12-len(inp)) + inp
