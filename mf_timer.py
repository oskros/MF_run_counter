from init import *
from options import Options
from config import Config
import github_releases
import tk_utils
import traceback
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sound
import sys
import time
import os
import webbrowser
import json
exec(blocks[1])


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
        if self._paused:
            self.Pause()
        self._start = time.time()
        self._laptime = 0.0
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

        tk.Button(self, text='Delete selection', command=self.delete).pack(side=tk.BOTTOM)

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
        # Choose active profile
        profile_frame = tk.Frame(self, height=25, width=238, pady=2, padx=2)
        profile_frame.propagate(False)
        profile_frame.pack()

        self.active_profile = tk.StringVar()
        self.active_profile.set(self.main_frame.active_profile)
        self.profile_dropdown = ttk.Combobox(profile_frame, textvariable=self.active_profile, state='readonly', values=self.main_frame.profiles)
        self.profile_dropdown.bind("<<ComboboxSelected>>", lambda e: self._set_active_profile())
        self.profile_dropdown.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        new_profile = tk.Button(profile_frame, text='New profile..', command=self._add_new_profile, borderwidth=1, height=1)
        new_profile.pack(side=tk.LEFT)

        temp_lab = tk.Label(self, text='\nView history for profile')
        temp_lab.pack()

        state = self.main_frame.load_state_file().get(self.main_frame.active_profile, dict())
        self.available_archive = [x for x in state.keys() if x != 'active_state']
        self.selected_archive = tk.StringVar()
        self.archive_dropdown = ttk.Combobox(self, textvariable=self.selected_archive, state='readonly', values=self.available_archive)
        self.archive_dropdown.pack()

        open_archive = tk.Button(self, text='Open archive', command=self.load_archived_state)
        open_archive.pack(expand=tk.NO)

    def load_archived_state(self):
        chosen = self.archive_dropdown.get()
        if chosen == '':
            return
        new_win = tk.Toplevel()
        new_win.title('Archive browser')
        new_win.wm_attributes('-topmost', 1)
        new_win.geometry('500x400')
        new_win.geometry('+%d+%d' % (self.main_frame.root.winfo_rootx(), self.main_frame.root.winfo_rooty()))
        new_win.focus_get()
        new_win.iconbitmap(os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), 'icon.ico'))

        l = tk.Label(new_win, text='Browser for archive', font='Helvetica 14')
        l.pack()

        archive_state = self.main_frame.load_state_file()
        active = archive_state.get(self.main_frame.active_profile, dict())
        chosen_archive = active.get(chosen, dict())
        session_time = chosen_archive.get('session_time', 0)
        laps = chosen_archive.get('laps', [])
        drops = chosen_archive.get('drops', dict())
        avg_lap = sum(laps) / len(laps) if laps else 0
        pct = sum(laps) * 100 / session_time if session_time > 0 else 0

        scrollbar = tk.Scrollbar(new_win, orient=tk.VERTICAL)
        self.m = tk.Listbox(new_win, selectmode=tk.EXTENDED, height=5, yscrollcommand=scrollbar.set, activestyle='none')
        self.m.bind('<FocusOut>', lambda e: self.m.selection_clear(0, tk.END))
        # self.m.bindtags((self.m, self, "all"))
        self.m.config(font=('courier', 12))
        self.m.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, pady=5)
        scrollbar.config(command=self.m.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.m.insert(tk.END, 'Total session time:   ' + tk_utils.build_time_str(session_time))
        self.m.insert(tk.END, 'Total run time:       ' + tk_utils.build_time_str(sum(laps)))
        self.m.insert(tk.END, 'Average run time:     ' + tk_utils.build_time_str(avg_lap))
        self.m.insert(tk.END, 'Fastest run time:     ' + tk_utils.build_time_str(min(laps, default=0)))
        self.m.insert(tk.END, 'Percentage spent in runs: ' + str(round(pct, 2)) + '%')
        self.m.insert(tk.END, '')

        if '0' in drops.keys():
            self.m.insert(tk.END, 'Run 0: ' + ', '.join(drops['0']))
        for n, lap in enumerate(laps, 1):
            str_n = ' ' * max(len(str(len(laps))) - len(str(n)), 0) + str(n)
            run_str = 'Run ' + str_n + ': ' + tk_utils.build_time_str(lap)
            droplst = drops.get(str(n), '')
            if droplst:
                run_str += ' --- ' + ', '.join(droplst)
            self.m.insert(tk.END, run_str)

    def _set_active_profile(self):
        self.main_frame.SaveActiveState()
        act = self.active_profile.get()
        self.main_frame.active_profile = act
        self.main_frame.LoadActiveState(self.main_frame.load_state_file())
        if not self.main_frame.tab1._paused:
            self.main_frame.tab1.Pause()

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


class About(tk.Frame):
    def __init__(self, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
        label0 = tk.Label(self, text="""Run counter for Diablo 2 developed in July 
2019 by *oskros on Path of Diablo. Please 
see the readme.md file available on Github""", justify=tk.LEFT)
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


class Main(Config):
    def __init__(self):
        # Create root
        self.root = tk.Tk()
        self.root.report_callback_exception = self.report_callback_exception

        # Build/load config file
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
        self.profiles = eval(self.cfg['PROFILE']['profiles'])

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
        self.root.iconbitmap(os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), 'icon.ico'))
        self.root.pack_propagate(False)

        # Build banner image
        d2icon = os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), 'd2icon.png')
        img = tk.PhotoImage(file=d2icon)
        img_panel = tk.Label(self.root, image=img)
        img_panel.pack()

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
        img_panel.bind("<ButtonPress-1>", self._start_move)
        img_panel.bind("<ButtonRelease-1>", self._stop_move)
        img_panel.bind("<B1-Motion>", self._on_motion)

        # Register some hidden keybinds
        self.root.bind("<Delete>", lambda event: self._delete_selection())

        # Load save state
        self.LoadActiveState(self.load_state_file())
        self._autosave_state()

        # Open the widget
        self.root.mainloop()

    def report_callback_exception(self, *args):
        err = traceback.format_exception(*args)
        tk.messagebox.showerror('Exception occured', err)
        self.Quit()

    def _delete_selection(self):
        tabs = self.tabcontrol.tabs()
        cur_tab = self.tabcontrol.select()
        idx = tabs.index(cur_tab)
        if idx == 1:
            self.tab2.delete()

    def _next_tab(self):
        tabs = self.tabcontrol.tabs()
        cur_tab = self.tabcontrol.select()

        nxt_idx = tabs.index(cur_tab) + 1
        if nxt_idx >= len(tabs):
            nxt_idx = 0
        self.tabcontrol.select(tabs[nxt_idx])

    def _prev_tab(self):
        tabs = self.tabcontrol.tabs()
        cur_tab = self.tabcontrol.select()

        prev_idx = tabs.index(cur_tab) - 1
        if prev_idx < 0:
            prev_idx = len(tabs) - 1
        self.tabcontrol.select(tabs[prev_idx])

    def _start_move(self, event):
        self.x = event.x
        self.y = event.y

    def _stop_move(self, event):
        self.x = None
        self.y = None

    def _on_motion(self, event):
        try:
            deltax = event.x - self.x
            deltay = event.y - self.y
        except (TypeError, AttributeError):
            return
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry("+%s+%s" % (x, y))

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
            json.dump(state, fo, indent=1)

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
            json.dump(cache, fo, indent=1)

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


Main()
