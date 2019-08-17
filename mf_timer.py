from init import *
import tk_utils
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from mf_configparser import Config
from system_hotkey import SystemHotkey
import sound
import sys
import time
import os
import webbrowser
exec(blocks[1])


class MFRunTimer(tk.Frame):
    def __init__(self, config, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
        self.cfg = config
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
        time_str = self._build_time_str(elap)
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
            self.min_lap.set('Fastest time: %s' % self._build_time_str(min(self.laps)))
        else:
            self.min_lap.set('Fastest time: --:--:--.-')

    def _set_average(self):
        if self.laps:
            self.avg_lap.set('Average time: %s' % self._build_time_str(sum(self.laps)/len(self.laps)))
        else:
            self.avg_lap.set('Average time: --:--:--.-')

    @staticmethod
    def _build_time_str(elap):
        hours = int(elap / 3600)
        minutes = int(elap / 60 - hours * 60.0)
        seconds = int(elap - hours * 3600.0 - minutes * 60.0)
        hseconds = int((elap - hours * 3600.0 - minutes * 60.0 - seconds) * 10)
        return '%02d:%02d:%02d:%1d' % (hours, minutes, seconds, hseconds)

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
            delay = eval(self.cfg.get('DEFAULT', 'run_timer_delay_seconds'))
            if delay > 0:
                self.after(int(delay*1000), update_start)
            else:
                update_start()
            if play_sound and eval(self.cfg['FLAGS']['enable_sound_effects']):
                sound.queue_sound(self)

    def Stop(self, play_sound=True):
        if self._running:
            self.Lap()
            self.c1.itemconfigure(self.circ_id, fill='red')
            self._laptime = 0.0
            self._running = False
            self._set_time(0, for_session=False)
            self.after_cancel(self._timer)
            if play_sound and eval(self.cfg['FLAGS']['enable_sound_effects']):
                sound.queue_sound(self)

    def StopStart(self):
        self.Stop(play_sound=False)
        self.Start(play_sound=False)
        if eval(self.cfg['FLAGS']['enable_sound_effects']):
            sound.queue_sound(self)

    def Lap(self):
        if self._running:
            self.laps.append(self._laptime)
            str_n = ' ' * max(3 - len(str(len(self.laps))), 0) + str(len(self.laps))
            self.m.insert(tk.END, 'Run ' + str_n + ': ' + self._build_time_str(self.laps[-1]))
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
            self.c1.itemconfigure(self.circ_id, fill='red')
            self._set_time(self._laptime, for_session=False)
            self._set_time(self._sessiontime, for_session=True)
            if self._running:
                self.after_cancel(self._timer)
            self.after_cancel(self._sess_timer)
            exec(blocks[7])
            self._paused = True
        else:
            self._start = time.time() - self._laptime
            self._session_start = time.time() - self._sessiontime
            if self._running:
                self.c1.itemconfigure(self.circ_id, fill='green3')
                self._update_lap_time()
            self._update_session_time()
            exec(blocks[8])
            self._paused = False


class Hotkeys(tk.Frame):
    def __init__(self, main_frame, timer_frame, drop_frame, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
        self.modifier_options = ['Control', 'Alt', 'Shift', '']
        self.character_options = ['Escape', 'Space', 'Delete',
                                  'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',  'L', 'M',
                                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                                  'F10', 'F11', 'F12', 'NO_BIND']
        self.hk = SystemHotkey()

        lf = tk.Frame(self)
        lf.pack()

        lb = tk.Label(lf, text='Action           Modifier    Key         ', font='Helvetica 11 bold')
        lb.pack()

        self.add_hotkey(label_name='Start run', keys=eval(main_frame.cfg['KEYBINDS']['start_key']), func=timer_frame.Start)
        self.add_hotkey(label_name='End run', keys=eval(main_frame.cfg['KEYBINDS']['end_key']), func=timer_frame.Stop)
        self.add_hotkey(label_name='Stop start', keys=eval(main_frame.cfg['KEYBINDS']['stopstart_key']), func=timer_frame.StopStart)
        self.add_hotkey(label_name='Delete prev', keys=eval(main_frame.cfg['KEYBINDS']['delete_prev_key']), func=timer_frame.DeletePrev)
        self.add_hotkey(label_name='Pause', keys=eval(main_frame.cfg['KEYBINDS']['pause_key']), func=timer_frame.Pause)
        self.add_hotkey(label_name='Add drop', keys=eval(main_frame.cfg['KEYBINDS']['drop_key']), func=drop_frame.AddDrop)
        self.add_hotkey(label_name='Reset lap', keys=eval(main_frame.cfg['KEYBINDS']['reset_key']), func=main_frame.ResetLap)
        # self.add_hotkey('Quit', self._quit, tab0.SaveQuit)

    def add_hotkey(self, label_name, keys, func):
        if keys[0].lower() not in map(lambda x: x.lower(), self.modifier_options) or keys[1].lower() not in map(lambda x: x.lower(), self.character_options):
            messagebox.showerror('Invalid hotkey', 'One or several hotkeys are invalid. Please edit/delete mf_config.ini')
            sys.exit()
        default_modifier, default_key = keys
        action = label_name.replace(' ', '_').lower()
        setattr(self, '_' + action, keys)
        lf = tk.LabelFrame(self, height=35, width=179)
        lf.propagate(False)
        lf.pack(expand=True, fill=tk.BOTH)

        lab = tk.Label(lf, text=label_name)
        lab.pack(side=tk.LEFT)

        setattr(self, action + '_e', tk.StringVar())
        key = getattr(self, action + '_e')
        key.set(default_key)
        drop2 = ttk.Combobox(lf, textvariable=key, state='readonly', values=self.character_options)
        drop2.config(width=9)
        drop2.pack(side=tk.RIGHT, fill=tk.X, padx=2)

        setattr(self, action + '_m', tk.StringVar())
        mod = getattr(self, action + '_m')
        mod.set(default_modifier)
        drop1 = ttk.Combobox(lf, textvariable=mod, state='readonly', values=self.modifier_options)
        drop1.config(width=7)
        drop1.pack(side=tk.RIGHT)

        mod.trace_add('write', lambda name, index, mode: self.re_register(action, getattr(self, '_' + action), func))
        key.trace_add('write', lambda name, index, mode: self.re_register(action, getattr(self, '_' + action), func))
        if default_key.lower() != 'no_bind':
            reg_key = [keys[1].lower()] if keys[0] == '' else list(map(lambda x: x.lower(), keys))
            self.hk.register(reg_key, callback=lambda event: func())

    def re_register(self, event, old_hotkey, func):
        new_hotkey = [getattr(self, event + '_m').get(), getattr(self, event + '_e').get()]
        new_lower = list(map(lambda x: x.lower(), new_hotkey))
        if new_lower in [list(x) for x in list(self.hk.keybinds.keys())]:
            messagebox.showerror('Reserved bind', 'This keybind is already in use.')
            m = getattr(self, event + '_m')
            e = getattr(self, event + '_e')
            m.set(old_hotkey[0])
            e.set(old_hotkey[1])
        elif new_lower == ['control', 'escape']:
            messagebox.showerror('Reserved bind', 'Control+escape is reserved for windows. This setting is not allowed')
            m = getattr(self, event + '_m')
            e = getattr(self, event + '_e')
            m.set(old_hotkey[0])
            e.set(old_hotkey[1])
        else:
            if old_hotkey[1].lower() != 'no_bind':
                unreg = [old_hotkey[1].lower()] if old_hotkey[0] == '' else list(map(lambda x: x.lower(), old_hotkey))
                self.hk.unregister(unreg)
            if new_hotkey[1].lower() != 'no_bind':
                reg = [new_hotkey[1].lower()] if new_hotkey[0] == '' else new_lower
                self.hk.register(reg, callback=lambda event: func(), overwrite=True)
            setattr(self, '_' + event, new_hotkey)


class Drops(tk.Frame):
    def __init__(self, tab1, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
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
        drop = tk_utils.mbox('Input your drop', entry=True)
        if drop is False:
            return
        run_no = len(self.tab1.laps)
        if self.tab1._running:
            run_no += 1
        self.m.insert(tk.END, 'Run %s: %s' % (run_no, drop))
        self.m.yview_moveto(1)

    def delete(self):
        selection = self.m.curselection()
        if selection:
            self.m.delete(selection[0])


class Profile(tk.Frame):
    def __init__(self, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
        self.root = parent
        self.profiles = ['DEFAULT_PROFILE', 'TsssschSC - Mephisto']
        # Choose active profile
        profile_frame = tk.Frame(self, height=25, width=238, pady=2, padx=2)
        profile_frame.propagate(False)
        profile_frame.pack()

        self.active_profile = tk.StringVar()
        self.active_profile.set('DEFAULT_PROFILE')
        self.profile_dropdown = ttk.Combobox(profile_frame, textvariable=self.active_profile, state='readonly', values=self.profiles)
        # self.profile_dropdown.bind('<FocusOut>', lambda e: self.profile_dropdown.selection_clear())
        self.profile_dropdown.bind("<<ComboboxSelected>>", lambda e: print('New selection: %s' % self.active_profile.get()))
        self.profile_dropdown.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Add new profile
        new_profile = tk.Button(profile_frame, text='New profile..', command=self._add_new_profile, borderwidth=1, height=1)
        new_profile.pack(side=tk.LEFT)

    def _add_new_profile(self):
        xc = self.root.winfo_rootx() + self.root.winfo_width()//8
        yc = self.root.winfo_rooty() + self.root.winfo_height()//3
        profile = tk_utils.mbox('Add new profile', entry=True, coords=(xc,yc))
        if profile:
            if profile in self.profile_dropdown['values']:
                messagebox.showerror('Duplicate name', 'Profile name already in use - please choose another name.')
                return
            self.profile_dropdown['values'] = list(self.profile_dropdown['values']) + [profile]


class About(tk.Frame):
    def __init__(self, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
        label = tk.Label(self, text="""
        Please see the readme.md file available on 
        Github
         
        Run counter for Diablo 2 developed in July 
        2019 by *oskros on Path of Diablo.
        
        Current version: %s
        
        Visit the page below for new releases""" % version, justify=tk.LEFT)
        label.pack()
        label.place(x=-23, y=-15)

        link1 = tk.Label(self, text="Release Hyperlink", fg="blue", cursor="hand2")
        link1.pack(side=tk.BOTTOM)
        link1.bind("<Button-1>", lambda e: webbrowser.open_new(release_repo))


class Main(Config):
    def __init__(self):
        # Create root
        self.root = tk.Tk()

        # Build/load config file
        self.cfg = self.load_config_file()

        # Check for version
        if eval(self.cfg['FLAGS']['check_for_new_version']):
            self.check_newest_version()

        # Modify root window
        self.root.resizable(False, False)
        # self.root.attributes('-type', 'dock')
        # self.root.overrideredirect(True)
        self.root.config(borderwidth=3, relief='raised')
        self.root.geometry('+%d+%d' % eval(self.cfg['DEFAULT']['window_start_position']))
        self.root.wm_attributes("-topmost", eval(self.cfg['FLAGS']['always_on_top']))
        self.root.title('MF run counter')
        self.root.focus_get()
        self.root.protocol("WM_DELETE_WINDOW", self.SaveQuit)
        self.root.iconbitmap(os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), 'icon.ico'))

        # Build banner image
        d2icon = os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), 'd2icon.png')
        img = tk.PhotoImage(file=d2icon)
        img_panel = tk.Label(self.root, image=img)
        img_panel.pack()

        # Build tabs
        self.tabcontrol = ttk.Notebook(self.root)
        self.tab1 = MFRunTimer(self.cfg, self.tabcontrol)
        self.tab2 = Drops(self.tab1, parent=self.tabcontrol)
        self.tab3 = Hotkeys(self, self.tab1, self.tab2, parent=self.tabcontrol)
        self.tab4 = Profile(parent=self.root)
        self.tab5 = About(self.tabcontrol)
        self.tabcontrol.add(self.tab1, text='Timer')
        self.tabcontrol.add(self.tab2, text='Drops')
        self.tabcontrol.add(self.tab3, text='Hotkeys')
        self.tabcontrol.add(self.tab4, text='Profile')
        self.tabcontrol.add(self.tab5, text='About')
        self.tabcontrol.pack(expand=1, fill='both')

        # Add buttons to main widget
        lf = tk.LabelFrame(self.root, height=35)
        lf.propagate(False)
        lf.pack(expand=True, fill=tk.BOTH)
        tk.Button(lf, text='Start', command=self.tab1.Start).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tk.Button(lf, text='End', command=self.tab1.Stop).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tk.Button(lf, text='Add drop', command=self.tab2.AddDrop).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tk.Button(lf, text='Reset\nlap', command=self.ResetLap).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tk.Button(lf, text='Reset\nsession', command=self.ResetSession).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        # tk.Button(lf, text='Quit', command=self.SaveQuit).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # lfx = tk.LabelFrame(self.root)
        # lfx.pack(expand=True, fill=tk.BOTH)
        # tk.Button(lfx, text='Pause', command=self.tab1.Pause).pack(expand=True, fill=tk.BOTH)

        # Make window drag on the banner image
        img_panel.bind("<ButtonPress-1>", self._start_move)
        img_panel.bind("<ButtonRelease-1>", self._stop_move)
        img_panel.bind("<B1-Motion>", self._on_motion)

        # Register some hidden keybinds
        self.root.bind("<Delete>", lambda event: self._delete_selection())
        # self.root.bind("<Escape>", lambda event: self.SaveQuit())
        if eval(self.cfg['FLAGS']['tab_keys_global']):
            self.tab3.hk.register(['control', 'shift', 'next'], callback=lambda event: self._next_tab())
            self.tab3.hk.register(['control', 'shift', 'prior'], callback=lambda event: self._prev_tab())
        else:
            self.root.bind_all('<Control-Shift-Next>', lambda event: self._next_tab())
            self.root.bind_all('<Control-Shift-Prior>', lambda event: self._prev_tab())

        # Open the widget
        self.root.mainloop()

    def _delete_selection(self):
        tabs = self.tabcontrol.tabs()
        cur_tab = self.tabcontrol.select()
        idx = tabs.index(cur_tab)
        # if idx == 0:
        #     self.tab1.delete_prev()
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

    def ResetSession(self):
        xc = self.root.winfo_rootx() - self.root.winfo_width()//12
        yc = self.root.winfo_rooty() + self.root.winfo_height()//3
        save_session = tk_utils.mbox('Would you like to save session results?', b1='Yes', b2='No', coords=[xc, yc])
        if save_session is None:
            return
        if save_session is True:
            self.Save()

        if self.tab1._paused:
            self.tab1.Pause()
        self.tab1._start = time.time()
        self.tab1._laptime = 0.0
        self.tab1._session_start = time.time()
        self.tab1.laps = []
        self.tab1.m.delete(0, tk.END)
        self.tab1._set_time(self.tab1._laptime, for_session=False)
        self.tab1._set_time(self.tab1._sessiontime, for_session=True)
        self.tab1._set_laps(is_running=self.tab1._running)
        self.tab1._set_fastest()
        self.tab1._set_average()

        self.tab2.m.delete(0, tk.END)

    def ResetLap(self):
        if self.tab1._running:
            self.tab1._start = time.time()
            self.tab1._laptime = 0.0
            self.tab1._set_time(self.tab1._laptime, for_session=False)

    def Save(self):
        today = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())
        cfg_save_path = os.path.normpath(self.cfg.get('DEFAULT', 'logging_path'))
        if cfg_save_path in ['DEFAULT', '']:
            save_path = today
        else:
            save_path = os.path.join(cfg_save_path, today)
        with open(save_path + '.txt', 'wb') as savefile:
            to_write = [
                'Total session time: ' + str(self.tab1.session_time_str) + '\r\n',
                'Total run time:     ' + self.tab1._build_time_str(sum(self.tab1.laps)) + '\r\n'
                'Average run time:   ' + self.tab1._build_time_str(sum(self.tab1.laps) / len(self.tab1.laps)) + '\r\n',
                'Fastest run time:   ' + self.tab1._build_time_str(min(self.tab1.laps)) + '\r\n',
                'Percentage spent in runs: ' + str(
                    round(sum(self.tab1.laps) * 100 / self.tab1._sessiontime, 2)) + '%\r\n',
                '\r\n'
            ]
            for s in to_write:
                savefile.write(bytes(s, 'utf-8'))

            collected_drops = self.tab2.m.get(0, tk.END)
            dropdict = dict()
            for drop in collected_drops:
                split = drop.split(' ')
                dropdict.setdefault(split[1][:-1], []).append(' '.join(split[2:]))
            dropdict = {key: ', '.join(value) for key, value in dropdict.items()}

            for n, lap in enumerate(self.tab1.laps, 1):
                str_n = ' ' * max(len(str(len(self.tab1.laps))) - len(str(n)), 0) + str(n)
                run_str = 'Run ' + str_n + ': ' + self.tab1._build_time_str(lap)
                drops = dropdict.get(str(n), '')
                if drops:
                    run_str += ' --- ' + drops
                savefile.write(bytes(run_str + '\r\n', 'utf-8'))

    def UpdateConfig(self):
        cfg = self.cfg

        # Update position
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        cfg['DEFAULT']['window_start_position'] = str((x, y))

        # Update hotkeys
        cfg.remove_section('KEYBINDS')
        cfg.add_section('KEYBINDS')
        cfg.set('KEYBINDS', '# Please only edit keybinds from within the app')
        cfg['KEYBINDS']['start_key'] = str(self.tab3._start_run)
        cfg['KEYBINDS']['end_key'] = str(self.tab3._end_run)
        cfg['KEYBINDS']['stopstart_key'] = str(self.tab3._stop_start)
        cfg['KEYBINDS']['delete_prev_key'] = str(self.tab3._delete_prev)
        cfg['KEYBINDS']['pause_key'] = str(self.tab3._pause)
        cfg['KEYBINDS']['drop_key'] = str(self.tab3._add_drop)
        cfg['KEYBINDS']['reset_key'] = str(self.tab3._reset_lap)

        self.build_config_file(cfg)

    def SaveQuit(self):
        if self.tab1._running:
            self.tab1.Stop()
        if self.tab1.laps and messagebox.askyesno('Reset', 'Would you like to save results?'):
            self.Save()
        self.UpdateConfig()
        os._exit(0)

    @staticmethod
    def check_newest_version():
        try:
            import github_releases
            from packaging import version as pk_version
            latest = github_releases.get_releases('oskros/MF_counter_releases')[0]
            latest_ver = latest['tag_name']
            # webbrowser.open_new("https://github.com/oskros/MF_counter_releases/releases")
            if pk_version.parse(version) < pk_version.parse(latest_ver):
                tk.messagebox.showinfo('New version',
                                       'Your version is not up to date. Get the newest release from:'
                                       '\n%s' % release_repo)
        except:
            pass


Main()
