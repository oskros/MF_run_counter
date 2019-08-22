import sys
import tkinter as tk
from tkinter import messagebox, ttk
from system_hotkey import SystemHotkey


class Options(tk.Frame):
    def __init__(self, main_frame, timer_frame, drop_frame, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)

        self.tabcontrol = ttk.Notebook(self)
        self.tab1 = Hotkeys(main_frame, timer_frame, drop_frame, parent=self.tabcontrol)
        self.tab2 = General(main_frame, parent=self.tabcontrol)
        self.tabcontrol.add(self.tab1, text='Hotkeys')
        self.tabcontrol.add(self.tab2, text='General')
        self.tabcontrol.pack(expand=1, fill='both')


class General(tk.Frame):
    def __init__(self, main_frame, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
        self.main_frame = main_frame
        self.add_flag(flag_name='Always on top')
        self.add_flag(flag_name='Tab switch keys global')
        self.add_flag(flag_name='Check for new version')
        self.add_flag(flag_name='Enable sound effects')
        self.add_delay_option()

        tk.Label(self, text="Toggling 'Tab switch keys global' requires\na restart of the application", pady=10).pack()

    def change_delay(self):
        new = self.run_delay.get()
        if new in ['', '-'] or float(new) < 0:
            return
        self.main_frame.run_timer_delay_seconds = float(self.run_delay.get())

    def add_delay_option(self):
        lf = tk.LabelFrame(self, height=30, width=179)
        lf.propagate(False)
        lf.pack(expand=False, fill=tk.X)

        lab = tk.Label(lf, text='Start run delay (seconds)')
        lab.pack(side=tk.LEFT)

        self.run_delay = tk.StringVar(lf)
        self.run_delay.set(eval(self.main_frame.cfg['DEFAULT']['run_timer_delay_seconds']))
        tk.Entry(lf, textvariable=self.run_delay).pack(side=tk.RIGHT)
        self.run_delay.trace_add('write', lambda name, index, mode: self.change_delay())

    def add_flag(self, flag_name):
        lf = tk.LabelFrame(self, height=30, width=179)
        lf.propagate(False)
        lf.pack(expand=False, fill=tk.X)

        lab = tk.Label(lf, text=flag_name)
        lab.pack(side=tk.LEFT)

        flag_attr = flag_name.lower().replace(' ', '_')
        setattr(self, flag_attr, tk.StringVar(lf))
        sv = getattr(self, flag_attr)
        off_button = tk.Radiobutton(lf, text='Off', variable=sv, indicatoron=False, value=False, width=5, command=lambda: self.toggle_button(flag_attr))
        on_button = tk.Radiobutton(lf, text='On', variable=sv, indicatoron=False, value=True, width=5, padx=3, command=lambda: self.toggle_button(flag_attr))

        if eval(self.main_frame.cfg['OPTIONS'][flag_attr]):
            on_button.invoke()
        else:
            off_button.invoke()
        on_button.pack(side=tk.RIGHT)
        off_button.pack(side=tk.RIGHT)

    def toggle_button(self, attr):
        val = eval(getattr(self, attr).get())
        setattr(self.main_frame, attr, val)
        if attr == 'always_on_top':
            self.main_frame.root.wm_attributes("-topmost", self.main_frame.always_on_top)


class Hotkeys(tk.Frame):
    def __init__(self, main_frame, timer_frame, drop_frame, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
        self.modifier_options = ['Control', 'Alt', 'Shift', '']
        self.character_options = ['Escape', 'Space', 'Delete',
                                  'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',  'L', 'M',
                                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                                  'F10', 'F11', 'F12', 'NO_BIND']
        self.hk = SystemHotkey()

        lf = tk.Frame(self, height=20, width=179)
        lf.pack(expand=True, fill=tk.BOTH)
        lf.propagate(False)

        l1 = tk.Label(lf, text='Action', font='Helvetica 11 bold', justify=tk.LEFT)
        l3 = tk.Label(lf, text='Key          ', font='Helvetica 11 bold', justify=tk.LEFT, width=9)
        l2 = tk.Label(lf, text=' Modifier', font='Helvetica 11 bold', justify=tk.LEFT, width=7)

        l1.pack(side=tk.LEFT)
        l3.pack(side=tk.RIGHT)
        l2.pack(side=tk.RIGHT)

        self.add_hotkey(label_name='Start new run', keys=eval(main_frame.cfg['KEYBINDS']['start_key']), func=lambda: main_frame.queue.put(timer_frame.StopStart))
        self.add_hotkey(label_name='End run', keys=eval(main_frame.cfg['KEYBINDS']['end_key']), func=lambda: main_frame.queue.put(timer_frame.Stop))
        self.add_hotkey(label_name='Delete prev', keys=eval(main_frame.cfg['KEYBINDS']['delete_prev_key']), func=lambda: main_frame.queue.put(timer_frame.DeletePrev))
        self.add_hotkey(label_name='Pause', keys=eval(main_frame.cfg['KEYBINDS']['pause_key']), func=lambda: main_frame.queue.put(timer_frame.Pause))
        self.add_hotkey(label_name='Add drop', keys=eval(main_frame.cfg['KEYBINDS']['drop_key']), func=lambda: main_frame.queue.put(drop_frame.AddDrop))
        self.add_hotkey(label_name='Reset lap', keys=eval(main_frame.cfg['KEYBINDS']['reset_key']), func=lambda: main_frame.queue.put(timer_frame.ResetLap))
        self.add_hotkey(label_name='Make unclickable', keys=eval(main_frame.cfg['KEYBINDS']['make_unclickable']), func=lambda: main_frame.queue.put(main_frame.set_clickthrough))

    def add_hotkey(self, label_name, keys, func):
        if keys[0].lower() not in map(lambda x: x.lower(), self.modifier_options) or keys[1].lower() not in map(lambda x: x.lower(), self.character_options):
            messagebox.showerror('Invalid hotkey', 'One or several hotkeys are invalid. Please edit/delete mf_config.ini')
            sys.exit()
        default_modifier, default_key = keys
        action = label_name.replace(' ', '_').lower()
        setattr(self, '_' + action, keys)
        lf = tk.LabelFrame(self, height=30, width=179)
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
        else:
            if old_hotkey[1].lower() != 'no_bind':
                unreg = [old_hotkey[1].lower()] if old_hotkey[0] == '' else list(map(lambda x: x.lower(), old_hotkey))
                self.hk.unregister(unreg)
            if new_hotkey[1].lower() != 'no_bind':
                reg = [new_hotkey[1].lower()] if new_hotkey[0] == '' else new_lower
                self.hk.register(reg, callback=lambda event: func(), overwrite=True)
            setattr(self, '_' + event, new_hotkey)
