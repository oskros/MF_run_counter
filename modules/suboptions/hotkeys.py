import sys
import tkinter as tk
import win32gui
from tkinter import messagebox, ttk
import system_hotkey
from utils import tk_dynamic as tkd, other_utils
# TODO: The usage of setattr/getattr in below class is inelegant, and could be refactored with a dictionary or similar


class Hotkeys(tkd.Frame):
    def __init__(self, main_frame, timer_frame, drop_frame, parent=None, **kw):
        tkd.Frame.__init__(self, parent, kw)
        self.main_frame = main_frame
        self.modifier_options = system_hotkey.modifier_options
        self.character_options = system_hotkey.character_options
        self.hk = system_hotkey.SystemHotkey()

        lf = tkd.Frame(self, height=20, width=179)
        lf.pack(expand=True, fill=tk.BOTH)
        lf.propagate(False)
        tkd.Label(lf, text='Action', font='Helvetica 11 bold', justify=tk.LEFT).pack(side=tk.LEFT)
        tkd.Label(lf, text='Key          ', font='Helvetica 11 bold', justify=tk.LEFT, width=9).pack(side=tk.RIGHT)
        tkd.Label(lf, text=' Modifier', font='Helvetica 11 bold', justify=tk.LEFT, width=7).pack(side=tk.RIGHT)

        default_binds = {k: other_utils.safe_eval(v) for k, v in dict(main_frame.cfg['KEYBINDS']).items()}
        self.add_hotkey(label_name='Start new run', keys=default_binds['start_key'], func=timer_frame.stop_start)
        self.add_hotkey(label_name='End run', keys=default_binds['end_key'], func=timer_frame.stop)
        self.add_hotkey(label_name='Delete prev', keys=default_binds['delete_prev_key'], func=timer_frame.delete_prev)
        self.add_hotkey(label_name='Pause', keys=default_binds['pause_key'], func=timer_frame.pause)
        self.add_hotkey(label_name='Add drop', keys=default_binds['drop_key'], func=drop_frame.add_drop)
        self.add_hotkey(label_name='Reset lap', keys=default_binds['reset_key'], func=timer_frame.reset_lap)
        self.add_hotkey(label_name='Make unclickable', keys=default_binds['make_unclickable'], func=main_frame.set_clickthrough)

    def add_hotkey(self, label_name, keys, func):
        # A check to ensure user has not tampered with mf_config.ini hotkeys, as that could cause unforeseen errors
        if keys[0] not in self.modifier_options or keys[1] not in self.character_options:
            messagebox.showerror('Invalid hotkey', 'One or several hotkeys are invalid. Please edit/delete mf_config.ini')
            sys.exit()

        # Build label frame for dropdown menus
        action = label_name.replace(' ', '_').lower()
        setattr(self, '_' + action, keys)
        lf = tkd.LabelFrame(self, height=30, width=179)
        lf.propagate(False)
        lf.pack(expand=True, fill=tk.BOTH)

        # Create label explaining what the hotkey controls
        lab = tkd.Label(lf, text=label_name)
        lab.pack(side=tk.LEFT)

        # Create dropdown for selecing the key (this needs to be packed first, as we pack from the right)
        setattr(self, action + '_e', tk.StringVar())
        key = getattr(self, action + '_e')
        key.set(keys[1])
        dropdown2 = ttk.Combobox(lf, textvariable=key, state='readonly', values=self.character_options)
        dropdown2.bind("<FocusOut>", lambda _: dropdown2.selection_clear())
        dropdown2.config(width=9)
        dropdown2.pack(side=tk.RIGHT, fill=tk.X, padx=2)

        # Create dropdown for selecting the modifier
        setattr(self, action + '_m', tk.StringVar())
        mod = getattr(self, action + '_m')
        mod.set(keys[0])
        dropdown1 = ttk.Combobox(lf, textvariable=mod, state='readonly', values=self.modifier_options)
        dropdown1.bind("<FocusOut>", lambda _: dropdown1.selection_clear())
        dropdown1.config(width=7)
        dropdown1.pack(side=tk.RIGHT)

        # Add a callback whenever something is written to the "mod" and "key" StringVars (so we can update the hotkey
        # register)
        mod.trace_add('write', lambda name, index, mode: self.re_register(action, getattr(self, '_' + action), func))
        key.trace_add('write', lambda name, index, mode: self.re_register(action, getattr(self, '_' + action), func))

        # If the "no_bind" option isn't seleced, we register the hotkey - notably the hotkey is disabled whenever the
        # "add drop" window is open, as this freezes the main window causing the user to potentially believe hotkeys
        # are not working and pressing them several times, causing a flood to the queue function.
        if keys[1].lower() != 'no_bind':
            reg_key = [k.lower() for k in keys if k != '']
            self.hk.register(reg_key, callback=lambda _: '' if win32gui.FindWindow(None, 'Add drop') else self.main_frame.queue.put(func))

    def re_register(self, event, old_hotkey, func):
        new_hotkey = [getattr(self, event + '_m').get(), getattr(self, event + '_e').get()]
        new_lower = [nh.lower() for nh in new_hotkey]
        if new_lower in [list(x) for x in list(self.hk.keybinds.keys())]:
            messagebox.showerror('Reserved bind', 'This keybind is already in use.')
            m = getattr(self, event + '_m')
            e = getattr(self, event + '_e')

            # Revert to previous value for dropdown
            for old, new, val in zip(old_hotkey, new_hotkey, [m, e]):
                if old != new:
                    val.set(old)
        else:
            if old_hotkey[1].lower() != 'no_bind':
                unreg = [oh.lower() for oh in old_hotkey if oh != '']
                self.hk.unregister(unreg)
            if new_hotkey[1].lower() != 'no_bind':
                reg = [nh.lower() for nh in new_hotkey if nh != '']
                self.hk.register(reg, callback=lambda _: '' if win32gui.FindWindow(None, 'Add drop') else self.main_frame.queue.put(func), overwrite=True)
            setattr(self, '_' + event, new_hotkey)
