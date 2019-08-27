from init import *
from options import Options
from config import Config
import github_releases
import tk_utils
import win32con
import win32gui
import win32api
import traceback
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import queue
import sound
import sys
import time
import os
import webbrowser
import json
import csv
exec(blocks[1])


class MFRunTimer(tk.Frame):
    def __init__(self, main_frame, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
        self.main_frame = main_frame
        self._start = 0.0
        self._session_start = time.time()
        self.session_time = 0.0
        self._laptime = 0.0
        self.is_running = False
        self._paused = False
        self.sessionstr = tk.StringVar()
        self.timestr = tk.StringVar()
        self.no_of_laps = tk.StringVar()
        self.min_lap = tk.StringVar()
        self.avg_lap = tk.StringVar()
        self.laps = []
        self._make_widgets()

        exec(blocks[5])

        self._update_session_time()

    def _make_widgets(self):
        flt = tk.Canvas(self)
        flt.pack(fill=tk.X, expand=tk.NO)
        self.c1, self.circ_id = tk_utils.add_circle(flt, 14, 'red')
        self.c1.grid(row=0, column=0, padx=3, pady=3)
        l0 = tk.Label(flt, textvariable=self.sessionstr, font=('arial', 10))
        self._set_time(self.session_time, for_session=True)
        l0.grid(row=0, column=1, sticky=tk.N, padx=20)

        l1 = tk.Label(self, textvariable=self.timestr, font='arial 20')
        self._set_time(0, for_session=False)
        l1.pack(fill=tk.X, expand=tk.NO, pady=4)

        l2f = tk.Frame(self)
        l2f.pack(pady=2)
        l2_1 = tk.Label(l2f, text='---- Run count:', font=('arial', 12))
        l2_1.pack(side=tk.LEFT)
        l2_2 = tk.Label(l2f, textvariable=self.no_of_laps, font='arial 15', fg='red')
        l2_2.pack(side=tk.LEFT)
        l2_3 = tk.Label(l2f, text='----', font=('arial', 12))
        l2_3.pack(side=tk.LEFT)
        self._set_laps(is_running=False)

        l3 = tk.Label(self, textvariable=self.min_lap)
        self._set_fastest()
        l3.pack(fill=tk.X, expand=tk.NO, pady=3, padx=2)
        l3.config(font=('arial', 11))

        l4 = tk.Label(self, textvariable=self.avg_lap)
        self._set_average()
        l4.pack(fill=tk.X, expand=tk.NO, pady=3, padx=2)
        l4.config(font=('arial', 11))

        lf0 = tk.Frame(self)
        lf0.pack()
        scrollbar = tk.Scrollbar(lf0, orient=tk.VERTICAL)
        self.m = tk.Listbox(lf0, selectmode=tk.EXTENDED, height=5, yscrollcommand=scrollbar.set, activestyle='none')
        self.m.bind('<FocusOut>', lambda e: self.m.selection_clear(0, tk.END))
        self.m.bindtags((self.m, self, "all"))
        self.m.config(font=('courier', 12))
        self.m.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, pady=5)
        scrollbar.config(command=self.m.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _update_lap_time(self):
        self._laptime = time.time() - self._start
        self._set_time(self._laptime, for_session=False)
        self._timer = self.after(50, self._update_lap_time)

    def _update_session_time(self):
        self.session_time = time.time() - self._session_start
        self._set_time(self.session_time, for_session=True)
        self._sess_timer = self.after(50, self._update_session_time)

    exec(blocks[6])

    def _set_time(self, elap, for_session):
        time_str = tk_utils.build_time_str(elap)
        if for_session:
            self.session_time_str = time_str
            self.sessionstr.set('Session time: ' + self.session_time_str)
        else:
            self.timestr.set(time_str)

    def _set_laps(self, is_running):
        run_count = len(self.laps)
        if is_running:
            run_count += 1
        self.no_of_laps.set(run_count)

    def _set_fastest(self):
        if self.laps:
            self.min_lap.set('Fastest time: %s' % tk_utils.build_time_str(min(self.laps)))
        else:
            self.min_lap.set('Fastest time: --:--:--.-')

    def _set_average(self):
        if self.laps:
            self.avg_lap.set('Average time: %s' % tk_utils.build_time_str(sum(self.laps) / len(self.laps)))
        else:
            self.avg_lap.set('Average time: --:--:--.-')

    def load_from_state(self, state):
        self.laps = []
        self.m.delete(0, tk.END)
        self.session_time = state.get('session_time', 0)
        self._session_start = time.time() - self.session_time
        for lap in state.get('laps', []):
            self.Lap(lap, force=True)
        self._set_laps(is_running=False)
        self._set_fastest()
        self._set_average()
        self._set_time(self.session_time, for_session=True)

    def Start(self, play_sound=True):
        def update_start():
            if self._paused:
                self.Pause()
            self.c1.itemconfigure(self.circ_id, fill='green3')
            self._start = time.time() - self._laptime
            self._update_lap_time()
            self._set_laps(is_running=True)
            self.is_running = True

        if not self.is_running:
            if play_sound and self.main_frame.enable_sound_effects:
                sound.queue_sound(self)
            delay = self.main_frame.run_timer_delay_seconds
            if delay > 0:
                self.after(int(delay*1000), update_start)
            else:
                update_start()

    def Stop(self, play_sound=True):
        if self.is_running:
            self.Lap(self._laptime)
            self.c1.itemconfigure(self.circ_id, fill='red')
            self._laptime = 0.0
            self.is_running = False
            self._set_time(0, for_session=False)
            self.after_cancel(self._timer)
            if play_sound and self.main_frame.enable_sound_effects:
                sound.queue_sound(self)

    def StopStart(self):
        self.Stop(play_sound=False)
        self.Start(play_sound=False)
        if self.main_frame.enable_sound_effects:
            sound.queue_sound(self)

    def Lap(self, laptime, force=False):
        if self.is_running or force:
            self.laps.append(laptime)
            str_n = ' ' * max(3 - len(str(len(self.laps))), 0) + str(len(self.laps))
            self.m.insert(tk.END, 'Run ' + str_n + ': ' + tk_utils.build_time_str(self.laps[-1]))
            self.m.yview_moveto(1)
            self._set_laps(is_running=False)
            self._set_fastest()
            self._set_average()

    def DeletePrev(self):
        if self.laps:
            self.m.delete(tk.END)
            self.laps.pop()
            self._set_laps(is_running=self.is_running)
            self._set_fastest()
            self._set_average()

    def Pause(self):
        if not self._paused:
            self.pause_lab = tk.Button(self, font='arial 24 bold', text='Resume', bg='deep sky blue', command=self.Pause)
            self.pause_lab.pack()
            self.pause_lab.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

            self.c1.itemconfigure(self.circ_id, fill='red')
            self._set_time(self._laptime, for_session=False)
            self._set_time(self.session_time, for_session=True)
            if self.is_running:
                self.after_cancel(self._timer)
            self.after_cancel(self._sess_timer)
            exec(blocks[7])
            self._paused = True
        else:
            self.pause_lab.destroy()
            self._start = time.time() - self._laptime
            self._session_start = time.time() - self.session_time
            if self.is_running:
                self.c1.itemconfigure(self.circ_id, fill='green3')
                self._update_lap_time()
            self._update_session_time()
            exec(blocks[8])
            self._paused = False

    def ResetLap(self):
        if self.is_running:
            self._start = time.time()
            self._laptime = 0.0
            self._set_time(self._laptime, for_session=False)

    def ResetSession(self):
        if self.is_running:
            self.Stop()
        self._start = time.time()
        self._laptime = 0.0
        self.session_time = 0.0
        self._session_start = time.time()
        self.laps = []
        self.m.delete(0, tk.END)
        self._set_time(self._laptime, for_session=False)
        self._set_time(self.session_time, for_session=True)
        self._set_laps(is_running=self.is_running)
        self._set_fastest()
        self._set_average()

    def SaveState(self):
        return dict(laps=self.laps, session_time=self.session_time)


class Drops(tk.Frame):
    def __init__(self, tab1, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
        self.drops = dict()
        self.tab1 = tab1
        lf = tk.Frame(self)
        lf.pack(expand=1, fill=tk.BOTH)
        scrollbar = tk.Scrollbar(lf, orient=tk.VERTICAL)
        self.m = tk.Listbox(lf, selectmode=tk.EXTENDED, height=5, yscrollcommand=scrollbar.set, activestyle='none')
        self.m.bind('<FocusOut>', lambda e: self.m.selection_clear(0, tk.END))
        self.m.config(font=('courier', 12))
        self.m.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, pady=5, padx=2)
        scrollbar.config(command=self.m.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn = tk.Button(self, text='Delete selection', command=self.delete)
        btn.bind_all('<Delete>', lambda e: self.delete())
        btn.pack(side=tk.BOTTOM)

    def AddDrop(self):
        drop = tk_utils.mbox('Input your drop', entry=True, title='Add drop')
        if not drop:
            return
        run_no = len(self.tab1.laps)
        if self.tab1.is_running:
            run_no += 1
        self.drops.setdefault(str(run_no), []).append(drop)
        self.display_drop(drop=drop, run_no=run_no)

    def display_drop(self, drop, run_no):
        self.m.insert(tk.END, 'Run %s: %s' % (run_no, drop))
        self.m.yview_moveto(1)

    def delete(self):
        selection = self.m.curselection()
        if selection:
            ss = self.m.get(selection[0])
            run_no = ss[4:ss.find(':')]
            drop = ss[ss.find(':')+2:]
            self.drops[run_no].remove(drop)
            self.m.delete(selection[0])

    def save_state(self):
        return self.drops

    def load_from_state(self, state):
        self.m.delete(0, tk.END)
        self.drops = state.get('drops', dict())
        for run in sorted(self.drops.keys(), key=lambda x: int(x)):
            for drop in self.drops[run]:
                self.display_drop(drop=drop, run_no=run)


class Profile(tk.Frame):
    def __init__(self, main_frame, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
        self.root = parent
        self.main_frame = main_frame
        self._make_widgets()

    def _make_widgets(self):
        prof_line = tk.Label(self, text='Select active profile', justify=tk.LEFT)
        prof_line.pack(anchor=tk.W)
        # Choose active profile
        profile_frame = tk.Frame(self, height=28, width=238, pady=2, padx=2)
        profile_frame.propagate(False)
        profile_frame.pack()

        self.active_profile = tk.StringVar()
        self.active_profile.set(self.main_frame.active_profile)
        self.profile_dropdown = ttk.Combobox(profile_frame, textvariable=self.active_profile, state='readonly', values=self.main_frame.profiles)
        self.profile_dropdown.bind("<<ComboboxSelected>>", lambda e: self._change_active_profile())
        self.profile_dropdown.pack(side=tk.LEFT, expand=True, fill=tk.X)

        tk.Button(profile_frame, text='New...', command=self._add_new_profile).pack(side=tk.LEFT)
        tk.Button(profile_frame, text='Delete', command=self._delete_profile).pack(side=tk.LEFT)

        self.extra_data = self.main_frame.load_state_file().get('extra_data', dict())
        extra_info1 = tk.Frame(self, height=12, width=238)
        extra_info1.propagate(False)
        extra_info1.pack(expand=True, fill=tk.X)
        extra_info2 = tk.Frame(self, height=12, width=238)
        extra_info2.propagate(False)
        extra_info2.pack(expand=True, fill=tk.X)
        self.mf_amount = tk.StringVar(extra_info1, value=self.extra_data.get('Active MF %', ''))
        self.run_type = tk.StringVar(extra_info1, value=self.extra_data.get('Run type', ''))
        self.char_name = tk.StringVar(extra_info1, value=self.extra_data.get('Character name', ''))
        tk.Label(extra_info1, text='Run type:', font='helvetica 8', anchor=tk.W, justify=tk.LEFT).pack(side=tk.LEFT)
        tk.Label(extra_info1, textvariable=self.run_type, font='helvetica 8 bold', anchor=tk.W, justify=tk.LEFT).pack(side=tk.LEFT)
        tk.Label(extra_info1, textvariable=self.mf_amount, font='helvetica 8 bold', anchor=tk.E, justify=tk.RIGHT).pack(side=tk.RIGHT)
        tk.Label(extra_info1, text='MF amount %:', font='helvetica 8', anchor=tk.W, justify=tk.RIGHT).pack(side=tk.RIGHT)
        tk.Label(extra_info2, text='Character:', font='helvetica 8', anchor=tk.W, justify=tk.LEFT).pack(side=tk.LEFT)
        tk.Label(extra_info2, textvariable=self.char_name, font='helvetica 8 bold', anchor=tk.W, justify=tk.LEFT).pack(side=tk.LEFT)

        tk.Label(self, text='Select an archived run for this profile', justify=tk.LEFT).pack(anchor=tk.W, pady=(6,0))

        sel_frame = tk.Frame(self, height=28, width=238, pady=2, padx=2)
        sel_frame.propagate(False)
        sel_frame.pack()
        state = self.main_frame.load_state_file()
        self.available_archive = ['Active session', 'Profile history'] + [x for x in state.keys() if x not in ['active_state', 'extra_data']]
        self.selected_archive = tk.StringVar()
        self.selected_archive.set('Active session')
        self.archive_dropdown = ttk.Combobox(sel_frame, textvariable=self.selected_archive, state='readonly', values=self.available_archive)
        self.archive_dropdown.pack(side=tk.LEFT)

        open_archive = tk.Button(sel_frame, text='Open', command=self.open_archive_browser)
        open_archive.pack(side=tk.LEFT)

        delete_archive = tk.Button(sel_frame, text='Delete', command=self.delete_archived_session)
        delete_archive.pack(side=tk.LEFT)

        tk.Label(self, text='Descriptive statistics for current profile', justify=tk.LEFT).pack(anchor=tk.W, pady=(6,0))

        self.descr = tk.Listbox(self, selectmode=tk.EXTENDED, height=7, activestyle='none')
        self.descr.bind('<FocusOut>', lambda e: self.descr.selection_clear(0, tk.END))
        self.descr.config(font=('courier', 8))
        self.descr.pack(side=tk.BOTTOM, fill=tk.X, expand=1)
        self.update_descriptive_statistics()

    def _add_new_profile(self):
        xc = self.root.winfo_rootx() + self.root.winfo_width()//8
        yc = self.root.winfo_rooty() + self.root.winfo_height()//3
        profile = tk_utils.registration_form((xc,yc))
        if profile:
            profile_name = profile.pop('Profile name')
            if profile_name in self.profile_dropdown['values']:
                messagebox.showerror('Duplicate name', 'Profile name already in use - please choose another name.')
                return
            self.main_frame.profiles.append(profile_name)
            self.profile_dropdown['values'] = self.main_frame.profiles
            self.active_profile.set(profile_name)
            cache = dict()
            cache['extra_data'] = profile
            file = 'Profiles/%s.json' % self.active_profile.get()
            with open(file, 'w') as fo:
                json.dump(cache, fo, indent=2)
            self._change_active_profile()

    def _change_active_profile(self):
        self.main_frame.SaveActiveState()
        act = self.active_profile.get()
        self.main_frame.active_profile = act

        profile_cache = self.main_frame.load_state_file()
        self.extra_data = profile_cache.get('extra_data', dict())
        self.mf_amount.set(self.extra_data.get('Active MF %', ''))
        self.run_type.set(self.extra_data.get('Run type', ''))
        self.char_name.set(self.extra_data.get('Character name', ''))
        self.available_archive = ['Active session', 'Profile history'] + [x for x in profile_cache.keys() if x not in ['active_state', 'extra_data']]
        self.archive_dropdown['values'] = self.available_archive
        self.selected_archive.set('')

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
        new_win.title('Archive browser')
        new_win.wm_attributes('-topmost', 1)
        new_win.geometry('450x450')
        new_win.geometry('+%d+%d' % (self.main_frame.root.winfo_rootx(), self.main_frame.root.winfo_rooty()))
        new_win.focus_get()
        new_win.iconbitmap(os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), frozen + 'icon.ico'))
        title = tk.Label(new_win, text='Archive browser', font='Helvetica 14')

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
        list_frame = tk.Frame(new_win)
        vscroll = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        hscroll = tk.Scrollbar(new_win, orient=tk.HORIZONTAL)
        txt_list = tk.Listbox(list_frame, selectmode=tk.EXTENDED, yscrollcommand=vscroll.set, xscrollcommand=hscroll.set, activestyle='none', font=('courier', 10))
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

        button_frame = tk.Frame(new_win)
        tk.Button(button_frame, text='Copy to clipboard', command=lambda: self.copy_to_clipboard(new_win, '\n'.join(txt_list.get(0, tk.END)))).pack(side=tk.LEFT, fill=tk.X)
        tk.Button(button_frame, text='Save as .txt', command=lambda: self.save_to_txt('\n'.join(txt_list.get(0, tk.END)))).pack(side=tk.LEFT, fill=tk.X)
        tk.Button(button_frame, text='Save as .csv', command=lambda: self.save_to_csv(output)).pack(side=tk.LEFT, fill=tk.X)

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


class About(tk.Frame):
    def __init__(self, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
        label0 = tk.Label(self, text="""Run counter for Diablo 2 developed in July 
and August2019 by *oskros on Path of 
Diablo. Please see the README.md file 
available on Github""", justify=tk.LEFT)
        label0.pack()
        link0 = tk.Label(self, text="Open Readme", fg="blue", cursor="hand2")
        link0.pack()
        link0.bind("<Button-1>", lambda e: webbrowser.open_new(release_repo.rstrip('releases') + 'blob/master/README.md'))

        label = tk.Label(self, text="\n\nVisit the page below for new releases")
        label.pack()

        link1 = tk.Label(self, text="Release Hyperlink", fg="blue", cursor="hand2")
        link1.pack()
        link1.bind("<Button-1>", lambda e: webbrowser.open_new(release_repo))

        lab2 = tk.Label(self, text="\n\nCurrent version: %s" % version)
        lab2.pack(side=tk.BOTTOM)


class MainFrame(Config, tk_utils.MovingFrame, tk_utils.TabSwitch):
    def __init__(self):
        # Create root
        self.root = tk.Tk()
        self.root.report_callback_exception = self.report_callback_exception

        # Create hotkey queue and initiate process for monitoring the queue
        self.queue = queue.Queue(maxsize=1)
        self.process_queue()

        # Build/load config file
        self.cfg = self.load_config_file()
        self.always_on_top = eval(self.cfg['OPTIONS']['always_on_top'])
        self.tab_switch_keys_global = eval(self.cfg['OPTIONS']['tab_switch_keys_global'])
        self.check_for_new_version = eval(self.cfg['OPTIONS']['check_for_new_version'])
        self.enable_sound_effects = eval(self.cfg['OPTIONS']['enable_sound_effects'])
        self.run_timer_delay_seconds = eval(self.cfg['DEFAULT']['run_timer_delay_seconds'])

        # Check for version update
        if self.check_for_new_version:
            github_releases.check_newest_version()

        # Load profile info
        self.active_profile = self.cfg['DEFAULT']['active_profile']
        self.profiles = {(self.active_profile)}
        active_state = self.load_state_file()
        self.profiles.update({x.rstrip('json').rstrip('.') for x in os.listdir('Profiles')})
        self.profiles = sorted(self.profiles)

        # Modify root window
        self.root.title('MF run counter')
        self.clickthrough = False
        self.root.resizable(False, False)
        self.root.config(borderwidth=3, relief='raised', height=405, width=240)
        self.root.geometry('+%d+%d' % eval(self.cfg['DEFAULT']['window_start_position']))
        self.root.wm_attributes("-topmost", self.always_on_top)
        self.root.focus_get()
        self.root.protocol("WM_DELETE_WINDOW", self.Quit)
        self.root.iconbitmap(os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), frozen + 'icon.ico'))
        self.root.pack_propagate(False)

        # Build banner image and make window draggable on the banner
        d2icon = os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), frozen + 'd2icon.png')
        img = tk.PhotoImage(file=d2icon)
        self.img_panel = tk.Label(self.root, image=img)
        self.img_panel.pack()
        self.img_panel.bind("<ButtonPress-1>", self._start_move)
        self.img_panel.bind("<ButtonRelease-1>", self._stop_move)
        self.img_panel.bind("<B1-Motion>", self._on_motion)

        # Build tabs
        self.tabcontrol = ttk.Notebook(self.root)
        self.tab1 = MFRunTimer(self, parent=self.tabcontrol)
        self.tab2 = Drops(self.tab1, parent=self.tabcontrol)
        self.tab3 = Options(self, self.tab1, self.tab2, parent=self.tabcontrol)
        self.tab4 = Profile(self, parent=self.tabcontrol)
        self.tab5 = About(parent=self.tabcontrol)
        self.tabcontrol.add(self.tab1, text='Timer')
        self.tabcontrol.add(self.tab2, text='Drops')
        self.tabcontrol.add(self.tab3, text='Options')
        self.tabcontrol.add(self.tab4, text='Profile')
        self.tabcontrol.add(self.tab5, text='About')
        self.tabcontrol.pack(expand=1, fill='both')
        self.root.bind("<<NotebookTabChanged>>", lambda e: self.notebook_tab_change())

        # Add buttons to main widget
        lf = tk.LabelFrame(self.root, height=35)
        lf.propagate(False)  # dont allow buttons to modify label frame size
        lf.pack(expand=True, fill=tk.BOTH)
        tk.Button(lf, text='Start\nnew run', command=self.tab1.StopStart).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tk.Button(lf, text='End\nthis run', command=self.tab1.Stop).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tk.Button(lf, text='Add\ndrop', command=self.tab2.AddDrop).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tk.Button(lf, text='Reset\nlap', command=self.tab1.ResetLap).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tk.Button(lf, text='Archive\n& reset', command=self.ArchiveReset).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Register binds for changing tabs
        if self.tab_switch_keys_global:
            self.tab3.tab1.hk.register(['control', 'shift', 'next'], callback=lambda event: self._next_tab())
            self.tab3.tab1.hk.register(['control', 'shift', 'prior'], callback=lambda event: self._prev_tab())
        else:
            self.root.bind_all('<Control-Shift-Next>', lambda event: self._next_tab())
            self.root.bind_all('<Control-Shift-Prior>', lambda event: self._prev_tab())

        # Load save state and start autosave process
        self.LoadActiveState(active_state)
        self._autosave_state()

        # Start the program
        self.root.mainloop()

    def process_queue(self):
        """
        The system hotkeys are registered in child threads, and thus tkinter needs a queue to process hotkey calls to
        achieve a threadsafe system
        """
        try:
            self.queue.get(False)()
            self.root.after(50, lambda: self.process_queue())
        except queue.Empty:
            self.root.after(50, lambda: self.process_queue())

    def set_clickthrough(self):
        """
        Allow for making mouse clicks pass through the window, in case you want to use it as an overlay in your game
        Also makes the window transparent to visualize this effect.
        Calling the function again reverts the window to normal state.
        """
        hwnd = win32gui.FindWindow(None, "MF run counter")
        if not self.clickthrough:
            l_ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            l_ex_style |= win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, l_ex_style)
            win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 190, win32con.LWA_ALPHA)  # transparent
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, self.root.winfo_x(), self.root.winfo_y(), 0, 0, 0)
            self.clickthrough = True
        else:
            win32api.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 0)
            if not self.always_on_top:
                win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, self.root.winfo_x(), self.root.winfo_y(), 0, 0, 0)
            self.clickthrough = False

    def report_callback_exception(self, *args):
        """
        Handles occuring errors in the application, showing a messagebox with the occured error that user can send back
        for bug fixing
        """
        err = traceback.format_exception(*args)
        tk.messagebox.showerror('Exception occured', err)
        self.Quit()

    def notebook_tab_change(self):
        """
        When tab is switched to profile, the run counter is paused and descriptive statistics are updated. Perhaps it
        should also pause when going to the Options tab?
        """
        x = self.tabcontrol.select()
        if x.endswith('profile'):
            if not self.tab1._paused:
                self.tab1.Pause()
            self.tab4.update_descriptive_statistics()
        # A 'hack' to ensure that dropdown menus don't take focus immediate when you switch tabs by focusing the banner
        # image instead :)
        self.img_panel.focus_force()

    def load_state_file(self):
        """
        Loads the save file for the active profile.
        """
        if not os.path.isdir('Profiles'):
            os.makedirs('Profiles')
        file = 'Profiles/%s.json' % self.active_profile
        if not os.path.isfile(file):
            return dict()
        with open(file, 'r') as fo:
            state = json.load(fo)
        return state

    def _autosave_state(self):
        """
        Function to run the autosave loop that saves the profile every 30 seconds
        """
        self.SaveActiveState()
        self.root.after(30000, self._autosave_state)

    def ArchiveReset(self):
        """
        If any laps or drops have been recorded, this function saves the current session to the profile archive, and
        resets all info in the active session. In case no runs/drops are recorded, the session timer is simply reset
        """
        xc = self.root.winfo_rootx() - self.root.winfo_width()//12
        yc = self.root.winfo_rooty() + self.root.winfo_height()//3

        if not self.tab1.laps and not self.tab2.drops:
            self.ResetSession()
            return
        save_session = tk_utils.mbox('Would you like to save and reset session?', b1='Yes', b2='No', coords=[xc, yc])
        if save_session:
            self.ArchiveState()
            self.ResetSession()

    def ArchiveState(self):
        self.tab1.Stop()
        active = self.tab1.SaveState()
        active.update(dict(drops=self.tab2.save_state()))
        stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.tab4.available_archive.append(stamp)
        self.tab4.archive_dropdown['values'] = self.tab4.available_archive

        state = self.load_state_file()
        state['active_state'] = dict()
        state[stamp] = active
        file = 'Profiles/%s.json' % self.active_profile
        with open(file, 'w') as fo:
            json.dump(state, fo, indent=2)

    def LoadActiveState(self, state):
        active_state = state.get('active_state', dict())
        self.tab1.load_from_state(active_state)
        self.tab2.load_from_state(active_state)

    def SaveActiveState(self):
        cache = self.load_state_file()
        cache['active_state'] = self.tab1.SaveState()
        cache['active_state'].update(dict(drops=self.tab2.save_state()))
        file = 'Profiles/%s.json' % self.active_profile
        with open(file, 'w') as fo:
            json.dump(cache, fo, indent=2)
        self.tab4.update_descriptive_statistics()

    def ResetSession(self):
        """
        Resets session for the timer module and drops from the drops module
        """
        self.tab1.ResetSession()
        self.tab2.drops = dict()
        self.tab2.m.delete(0, tk.END)

    def Quit(self):
        """
        Stops the active run, updates config, saves current state to profile .json, and finally calls 'os._exit' which
        terminates all active threads
        """
        if self.tab1.is_running:
            self.tab1.Stop()
        self.update_config(self)
        self.SaveActiveState()
        os._exit(0)


MainFrame()
