from init import *
from options import Options
from config import Config
import github_releases
import tk_utils
import traceback
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import sound
import sys
import time
import os
import webbrowser
import json
exec(blocks[1])
frozen = '' if getattr(sys, 'frozen', False) else 'media\\'


class MFRunTimer(tk.Frame):
    def __init__(self, main_frame, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
        self.main_frame = main_frame
        self._start = 0.0
        self._session_start = time.time()
        self._sessiontime = 0.0
        self._laptime = 0.0
        self._running = False
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
        self._set_time(self._sessiontime, for_session=True)
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
        self._sessiontime = time.time() - self._session_start
        self._set_time(self._sessiontime, for_session=True)
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
        self._sessiontime = state.get('session_time', 0)
        self._session_start = time.time() - self._sessiontime
        for lap in state.get('laps', []):
            self.Lap(lap, force=True)

    def Start(self, play_sound=True):
        def update_start():
            if self._paused:
                self.Pause()
            self.c1.itemconfigure(self.circ_id, fill='green3')
            self._start = time.time() - self._laptime
            self._update_lap_time()
            self._set_laps(is_running=True)
            self._running = True

        if not self._running:
            if play_sound and self.main_frame.enable_sound_effects:
                sound.queue_sound(self)
            delay = eval(self.main_frame.cfg.get('DEFAULT', 'run_timer_delay_seconds'))
            if delay > 0:
                self.after(int(delay*1000), update_start)
            else:
                update_start()

    def Stop(self, play_sound=True):
        if self._running:
            self.Lap(self._laptime)
            self.c1.itemconfigure(self.circ_id, fill='red')
            self._laptime = 0.0
            self._running = False
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
        if self._running or force:
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
            self._set_laps(is_running=self._running)
            self._set_fastest()
            self._set_average()

    def Pause(self):
        if not self._paused:
            self.pause_lab = tk.Button(self, font='arial 24 bold', text='Resume', bg='deep sky blue', command=self.Pause)
            self.pause_lab.pack()
            self.pause_lab.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

            self.c1.itemconfigure(self.circ_id, fill='red')
            self._set_time(self._laptime, for_session=False)
            self._set_time(self._sessiontime, for_session=True)
            if self._running:
                self.after_cancel(self._timer)
            self.after_cancel(self._sess_timer)
            exec(blocks[7])
            self._paused = True
        else:
            self.pause_lab.destroy()
            self._start = time.time() - self._laptime
            self._session_start = time.time() - self._sessiontime
            if self._running:
                self.c1.itemconfigure(self.circ_id, fill='green3')
                self._update_lap_time()
            self._update_session_time()
            exec(blocks[8])
            self._paused = False

    def ResetLap(self):
        if self._running:
            self._start = time.time()
            self._laptime = 0.0
            self._set_time(self._laptime, for_session=False)

    def ResetSession(self):
        if self._running:
            self.Stop()
        self._start = time.time()
        self._laptime = 0.0
        self._sessiontime = 0.0
        self._session_start = time.time()
        self.laps = []
        self.m.delete(0, tk.END)
        self._set_time(self._laptime, for_session=False)
        self._set_time(self._sessiontime, for_session=True)
        self._set_laps(is_running=self._running)
        self._set_fastest()
        self._set_average()

    def SaveState(self):
        return dict(laps=self.laps, session_time=self._sessiontime)


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
        if drop is False:
            return
        run_no = len(self.tab1.laps)
        if self.tab1._running:
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

        sel_line = tk.Label(self, text='\nSelect an archived run for this profile', justify=tk.LEFT)
        sel_line.pack(anchor=tk.W)

        sel_frame = tk.Frame(self, height=28, width=238, pady=2, padx=2)
        sel_frame.propagate(False)
        sel_frame.pack()
        state = self.main_frame.load_state_file().get(self.main_frame.active_profile, dict())
        self.available_archive = ['Active session', 'Profile history'] + [x for x in state.keys() if x != 'active_state']
        self.selected_archive = tk.StringVar()
        self.selected_archive.set('Active session')
        self.archive_dropdown = ttk.Combobox(sel_frame, textvariable=self.selected_archive, state='readonly', values=self.available_archive)
        self.archive_dropdown.pack(side=tk.LEFT)

        open_archive = tk.Button(sel_frame, text='Open', command=self.open_archive_browser)
        open_archive.pack(side=tk.LEFT)

        delete_archive = tk.Button(sel_frame, text='Delete', command=self.delete_archived_session)
        delete_archive.pack(side=tk.LEFT)

        stat_line = tk.Label(self, text='\nDescriptive statistics for current profile', justify=tk.LEFT)
        stat_line.pack(anchor=tk.W)

        self.descr = tk.Listbox(self, selectmode=tk.EXTENDED, height=5, activestyle='none')
        self.descr.bind('<FocusOut>', lambda e: self.descr.selection_clear(0, tk.END))
        self.descr.config(font=('courier', 8))
        self.descr.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, pady=5)
        self.update_descriptive_statistics()

    def _add_new_profile(self):
        xc = self.root.winfo_rootx() + self.root.winfo_width()//8
        yc = self.root.winfo_rooty() + self.root.winfo_height()//3
        profile = tk_utils.mbox('Add new profile', entry=True, coords=(xc,yc))
        if profile:
            if profile in self.profile_dropdown['values']:
                messagebox.showerror('Duplicate name', 'Profile name already in use - please choose another name.')
                return
            self.main_frame.profiles.append(profile)
            self.profile_dropdown['values'] = self.main_frame.profiles

    def _change_active_profile(self):
        self.main_frame.SaveActiveState()
        act = self.active_profile.get()
        self.main_frame.active_profile = act

        cache_file = self.main_frame.load_state_file()
        profile_cache = cache_file.get(self.main_frame.active_profile, dict())
        self.available_archive = ['Active session', 'Profile history'] + [x for x in profile_cache.keys() if x != 'active_state']
        self.archive_dropdown['values'] = self.available_archive
        self.selected_archive.set('')

        self.main_frame.LoadActiveState(cache_file)
        self.update_descriptive_statistics()

    def _delete_profile(self):
        chosen = self.profile_dropdown.get()
        if chosen == '':
            return
        if len(self.profile_dropdown['values']) <= 1:
            tk.messagebox.showerror('Error', 'You need to have at least one profile, create a new profile before deleting this one.')
            return
        xc = self.root.winfo_rootx() + self.root.winfo_width()//8
        yc = self.root.winfo_rooty() + self.root.winfo_height()//3
        resp1 = tk_utils.mbox(msg='Are you sure you want to delete this profile? This will permanently delete all records stored for the profile.', coords=(xc, yc))
        if resp1 is True:
            resp2 = tk_utils.mbox(msg='Are you really really sure you want to delete the profile? Final warning!', b1='Cancel', b2='OK', coords=(xc,yc))
            if resp2 is False:
                cache = self.main_frame.load_state_file()
                cache.pop(chosen, None)
                with open('mf_cache.json', 'w') as fo:
                    json.dump(cache, fo, indent=2)
                self.main_frame.profiles.remove(chosen)
                self.main_frame.active_profile = self.main_frame.profiles[0]
                self.active_profile.set(self.main_frame.profiles[0])
                self.profile_dropdown['values'] = self.main_frame.profiles
                self._change_active_profile()

    def delete_archived_session(self):
        chosen = self.archive_dropdown.get()
        if chosen == '':
            return
        if chosen == 'Profile history':
            tk.messagebox.showerror('Error', 'You cannot delete profile history from here. Please delete all sessions manually, or delete the profile instead')
            return
        xc = self.root.winfo_rootx() + self.root.winfo_width()//8
        yc = self.root.winfo_rooty() + self.root.winfo_height()//3
        resp = tk_utils.mbox(msg='Do you really want to delete this session from archive?', coords=(xc, yc))
        if resp:
            if chosen == 'Active session':
                self.main_frame.ResetSession()
                self.main_frame.SaveActiveState()
                self.selected_archive.set('Active session')
                return
            cache = self.main_frame.load_state_file()
            if self.main_frame.active_profile in cache:
                cache[self.main_frame.active_profile].pop(chosen, None)
            with open('mf_cache.json', 'w') as fo:
                json.dump(cache, fo, indent=2)
            self.available_archive.remove(chosen)
            self.archive_dropdown['values'] = self.available_archive
            self.selected_archive.set('Active session')
            self.update_descriptive_statistics()

    def update_descriptive_statistics(self):
        active = self.main_frame.load_state_file().get(self.main_frame.active_profile, dict())
        laps = []
        session_time = 0
        dropcount = 0
        for key in active.keys():
            laps.extend(active[key].get('laps', []))
            session_time += active[key].get('session_time', 0)
            drops = active[key].get('drops', dict())
            for drop in drops.keys():
                dropcount += len(drop)
        avg_lap = sum(laps) / len(laps) if laps else 0
        pct = sum(laps) * 100 / session_time if session_time > 0 else 0

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
            return
        new_win = tk.Toplevel()
        new_win.title('Archive browser')
        new_win.wm_attributes('-topmost', 1)
        new_win.geometry('450x450')
        new_win.geometry('+%d+%d' % (self.main_frame.root.winfo_rootx(), self.main_frame.root.winfo_rooty()))
        new_win.focus_get()
        new_win.iconbitmap(os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), frozen + 'icon.ico'))

        l = tk.Label(new_win, text='Archive browser', font='Helvetica 14')
        l.pack()

        fr = tk.Frame(new_win)
        fr.pack(side=tk.BOTTOM)
        tk.Button(fr, text='Copy to clipboard', command=lambda: self.copy_to_clipboard(new_win, '\n'.join(m.get(0, tk.END)))).pack(side=tk.LEFT, fill=tk.X)
        tk.Button(fr, text='Save as .txt', command=lambda: self.save_to_txt('\n'.join(m.get(0, tk.END)))).pack(side=tk.LEFT, fill=tk.X)

        if chosen == 'Active session':
            session_time = self.main_frame.tab1._sessiontime
            laps = self.main_frame.tab1.laps
            drops = self.main_frame.tab2.drops
        elif chosen == 'Profile history':
            archive_state = self.main_frame.load_state_file()
            active = archive_state.get(self.main_frame.active_profile, dict())
            laps = []
            session_time = 0
            drops = dict()
            for key in active.keys():
                session_drops = active[key].get('drops', dict())
                for d in session_drops.keys():
                    drops[str(int(d)+len(laps))] = session_drops[d]
                laps.extend(active[key].get('laps', []))
                session_time += active[key].get('session_time', 0)
        else:
            archive_state = self.main_frame.load_state_file()
            active = archive_state.get(self.main_frame.active_profile, dict())
            chosen_archive = active.get(chosen, dict())
            session_time = chosen_archive.get('session_time', 0)
            laps = chosen_archive.get('laps', [])
            drops = chosen_archive.get('drops', dict())
        avg_lap = sum(laps) / len(laps) if laps else 0
        pct = sum(laps) * 100 / session_time if session_time > 0 else 0

        sbfr = tk.Frame(new_win)
        sbfr.pack(fill=tk.BOTH, expand=1)
        vscroll = tk.Scrollbar(sbfr, orient=tk.VERTICAL)
        hscroll = tk.Scrollbar(new_win, orient=tk.HORIZONTAL)
        m = tk.Listbox(sbfr, selectmode=tk.EXTENDED, yscrollcommand=vscroll.set, xscrollcommand=hscroll.set, activestyle='none')
        m.bind('<FocusOut>', lambda e: m.selection_clear(0, tk.END))
        m.config(font=('courier', 10))
        m.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        hscroll.config(command=m.xview)
        vscroll.config(command=m.yview)
        vscroll.pack(side=tk.LEFT, fill=tk.Y)
        hscroll.pack(side=tk.BOTTOM, fill=tk.X)

        m.insert(tk.END, 'Total session time:   ' + tk_utils.build_time_str(session_time))
        m.insert(tk.END, 'Total run time:       ' + tk_utils.build_time_str(sum(laps)))
        m.insert(tk.END, 'Average run time:     ' + tk_utils.build_time_str(avg_lap))
        m.insert(tk.END, 'Fastest run time:     ' + tk_utils.build_time_str(min(laps, default=0)))
        m.insert(tk.END, 'Time spent in runs: ' + str(round(pct, 2)) + '%')
        m.insert(tk.END, '')

        if '0' in drops.keys():
            m.insert(tk.END, 'Run 0: ' + ', '.join(drops['0']))
        for n, lap in enumerate(laps, 1):
            str_n = ' ' * max(len(str(len(laps))) - len(str(n)), 0) + str(n)
            run_str = 'Run ' + str_n + ': ' + tk_utils.build_time_str(lap)
            droplst = drops.get(str(n), '')
            if droplst:
                run_str += ' --- ' + ', '.join(droplst)
            m.insert(tk.END, run_str)

    @staticmethod
    def copy_to_clipboard(obj, string):
        obj.clipboard_clear()
        obj.clipboard_append(string)

    @staticmethod
    def save_to_txt(string):
        f = tk.filedialog.asksaveasfile(mode='w', defaultextension='.txt', filetypes=(('.txt', '*.txt'),('All Files', '*.*')))
        if not f:
            return
        f.write(string)
        f.close()


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

        # Build/load config file
        start_state = self.load_state_file()
        self.cfg = self.load_config_file()
        self.always_on_top = eval(self.cfg['FLAGS']['always_on_top'])
        self.tab_keys_global = eval(self.cfg['FLAGS']['tab_keys_global'])
        self.check_for_new_version = eval(self.cfg['FLAGS']['check_for_new_version'])
        self.enable_sound_effects = eval(self.cfg['FLAGS']['enable_sound_effects'])
        # Check for version
        if self.check_for_new_version:
            github_releases.check_newest_version()

        # Load profile info
        self.active_profile = self.cfg['PROFILE']['active_profile']
        self.profiles = set(eval(self.cfg['PROFILE']['profiles']))
        self.profiles.update(set(start_state.keys()))
        self.profiles = list(self.profiles)

        # Modify root window
        self.root.resizable(False, False)
        # self.root.attributes('-type', 'dock')
        # self.root.overrideredirect(True)
        self.root.config(borderwidth=3, relief='raised', height=405, width=240)
        self.root.geometry('+%d+%d' % eval(self.cfg['DEFAULT']['window_start_position']))
        self.root.wm_attributes("-topmost", self.always_on_top)
        self.root.title('MF run counter')
        self.root.focus_get()
        self.root.protocol("WM_DELETE_WINDOW", self.Quit)
        self.root.iconbitmap(os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), frozen + 'icon.ico'))
        self.root.pack_propagate(False)

        # Build banner image
        d2icon = os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), frozen + 'd2icon.png')
        img = tk.PhotoImage(file=d2icon)
        self.img_panel = tk.Label(self.root, image=img)
        self.img_panel.pack()

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
        lf.propagate(False)
        lf.pack(expand=True, fill=tk.BOTH)
        tk.Button(lf, text='Start\nnew run', command=self.tab1.StopStart).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tk.Button(lf, text='End\nthis run', command=self.tab1.Stop).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tk.Button(lf, text='Add\ndrop', command=self.tab2.AddDrop).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tk.Button(lf, text='Reset\nlap', command=self.tab1.ResetLap).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tk.Button(lf, text='Archive\n& reset', command=self.ArchiveReset).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Make window drag on the banner image
        self.img_panel.bind("<ButtonPress-1>", self._start_move)
        self.img_panel.bind("<ButtonRelease-1>", self._stop_move)
        self.img_panel.bind("<B1-Motion>", self._on_motion)

        # Register binds for changing tabs
        if self.tab_keys_global:
            self.tab3.tab1.hk.register(['control', 'shift', 'next'], callback=lambda event: self._next_tab())
            self.tab3.tab1.hk.register(['control', 'shift', 'prior'], callback=lambda event: self._prev_tab())
        else:
            self.root.bind_all('<Control-Shift-Next>', lambda event: self._next_tab())
            self.root.bind_all('<Control-Shift-Prior>', lambda event: self._prev_tab())

        # Load save state
        self.LoadActiveState(start_state)
        self._autosave_state()

        # Start the program
        self.root.mainloop()

    def report_callback_exception(self, *args):
        err = traceback.format_exception(*args)
        tk.messagebox.showerror('Exception occured', err)
        self.Quit()

    def notebook_tab_change(self):
        x = self.tabcontrol.select()
        if x.endswith('profile'):
            if not self.tab1._paused:
                self.tab1.Pause()
        self.img_panel.focus_force()

    @staticmethod
    def load_state_file():
        if not os.path.isfile('mf_cache.json'):
            return dict()
        with open('mf_cache.json', 'r') as fo:
            state = json.load(fo)
        return state

    def _autosave_state(self):
        self.SaveActiveState()
        self.root.after(30000, self._autosave_state)

    def ArchiveReset(self):
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
        if self.active_profile not in state:
            state[self.active_profile] = dict()
        state[self.active_profile]['active_state'] = dict()
        state[self.active_profile][stamp] = active
        with open('mf_cache.json', 'w') as fo:
            json.dump(state, fo, indent=2)

    def LoadActiveState(self, state):
        profile_state = state.get(self.active_profile, dict())
        active_state = profile_state.get('active_state', dict())
        self.tab1.load_from_state(active_state)
        self.tab2.load_from_state(active_state)

    def SaveActiveState(self):
        cache = self.load_state_file()
        if self.active_profile not in cache:
            cache[self.active_profile] = dict()
        cache[self.active_profile]['active_state'] = self.tab1.SaveState()
        cache[self.active_profile]['active_state'].update(dict(drops=self.tab2.save_state()))
        with open('mf_cache.json', 'w') as fo:
            json.dump(cache, fo, indent=2)
        self.tab4.update_descriptive_statistics()

    def ResetSession(self):
        self.tab1.ResetSession()
        self.tab2.drops = dict()
        self.tab2.m.delete(0, tk.END)

    def Quit(self):
        if self.tab1._running:
            self.tab1.Stop()
        self.UpdateConfig(self)
        self.SaveActiveState()
        os._exit(0)


MainFrame()
