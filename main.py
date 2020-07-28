from init import *
import sys
import time
import json
import queue
import traceback
import win32api
import win32gui
import win32con
import github_releases
from config import Config
from options import Options
from profiles import Profile
from color_themes import Theme, available_themes
from tkinter import ttk, messagebox
import tk_utils
import tkinter as tk
import tk_dynamic as tkd
from mf_timer import MFRunTimer, Drops, About


class MainFrame(Config, tk_utils.MovingFrame, tk_utils.TabSwitch):
    def __init__(self):
        # Create root
        self.root = tkd.Tk()

        # Ensure errors are handled with an exception pop-up if encountered
        self.root.report_callback_exception = self.report_callback_exception

        # Build/load config file
        self.cfg = self.load_config_file()
        self.AUTOMODE = eval(self.cfg['DEFAULT']['automode']) if 'automode' in self.cfg['DEFAULT'] else False
        self.always_on_top = eval(self.cfg['OPTIONS']['always_on_top'])
        self.tab_switch_keys_global = eval(self.cfg['OPTIONS']['tab_switch_keys_global'])
        self.check_for_new_version = eval(self.cfg['OPTIONS']['check_for_new_version'])
        self.enable_sound_effects = eval(self.cfg['OPTIONS']['enable_sound_effects'])
        self.run_timer_delay_seconds = eval(self.cfg['OPTIONS']['run_timer_delay_seconds'])
        self.pop_up_drop_window = eval(self.cfg['OPTIONS']['pop_up_drop_window'])
        self.active_theme = self.cfg['OPTIONS']['active_theme'].lower()

        # Load theme
        if self.active_theme not in available_themes:
            self.active_theme = 'vista'
        self.theme = Theme(used_theme=self.active_theme)
        self.drop_lab = tkd.Label(self.root, text='Drops', font='helvetica 14', bg=self.theme.label_color, fg=self.theme.text_color)

        # Create hotkey queue and initiate process for monitoring the queue
        self.queue = queue.Queue(maxsize=1)
        self.process_queue()

        # Check for version update
        if self.check_for_new_version:
            github_releases.check_newest_version(release_repo)

        # Load profile info
        self.make_profile_folder()
        self.profiles = [x[:-5] for x in os.listdir('Profiles') if x.endswith('.json')]
        self.active_profile = self.cfg['DEFAULT']['active_profile']
        if len(self.profiles) == 0:
            self.active_profile = ''
        elif len(self.profiles) > 0 and self.active_profile not in self.profiles:
            self.active_profile = self.profiles[0]
        self.profiles = sorted(self.profiles)  # FIXME: Sort by update time

        # Modify root window
        self.title = 'MF run counter'
        self.root.title(self.title)
        self.clickable = True
        self.root.resizable(False, False)
        self.root.geometry('+%d+%d' % eval(self.cfg['DEFAULT']['window_start_position']))
        # self.root.wm_attributes("-transparentcolor", "purple")
        self.root.wm_attributes("-topmost", self.always_on_top)
        self.root.focus_get()
        self.root.protocol("WM_DELETE_WINDOW", self.Quit)
        self.root.iconbitmap(os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), media_path + 'icon.ico'))
        self.root.pack_propagate(False)

        # Build banner image and make window draggable on the banner
        d2banner = os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), media_path + 'd2icon.png')
        img = tk.PhotoImage(file=d2banner)
        self.img_panel = tkd.Label(self.root, image=img)
        self.img_panel.pack()
        self.img_panel.bind("<ButtonPress-1>", self._start_move)
        self.img_panel.bind("<ButtonRelease-1>", self._stop_move)
        self.img_panel.bind("<B1-Motion>", self._on_motion)
        self.root.bind("<Left>", self._moveleft)
        self.root.bind("<Right>", self._moveright)
        self.root.bind("<Up>", self._moveup)
        self.root.bind("<Down>", self._movedown)
        if self.AUTOMODE:
            self.am_lab = tk.Label(self.root, text="Automode", fg="white", bg="black")
            self.am_lab.place(x=1, y=1)

        # Build tabs
        self.tabcontrol = ttk.Notebook(self.root)
        self.tab4 = Profile(self, parent=self.tabcontrol)
        self.tab1 = MFRunTimer(self, parent=self.tabcontrol)
        self.tabcontrol.add(self.tab1, text='Timer')
        self.tab2 = Drops(self.tab1, parent=self.root)
        self.toggle_drop_tab()
        self.tab3 = Options(self, self.tab1, self.tab2, parent=self.tabcontrol)
        self.tabcontrol.add(self.tab3, text='Options')
        self.tabcontrol.add(self.tab4, text='Profile')
        self.tab5 = About(parent=self.tabcontrol)
        self.tabcontrol.add(self.tab5, text='About')
        self.tabcontrol.pack(expand=1, fill='both')
        self.root.bind("<<NotebookTabChanged>>", lambda e: self.notebook_tab_change())
        self.tab4.update_descriptive_statistics()

        # Add buttons to main widget
        lf = tkd.LabelFrame(self.root, height=35)
        lf.propagate(False)  # dont allow buttons to modify label frame size
        lf.pack(expand=True, fill=tk.BOTH)
        tkd.Button(lf, text='Start\nnew run', command=self.tab1.StopStart).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tkd.Button(lf, text='End\nthis run', command=self.tab1.Stop).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tkd.Button(lf, text='Add\ndrop', command=self.tab2.AddDrop).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tkd.Button(lf, text='Reset\nlap', command=self.tab1.ResetLap).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tkd.Button(lf, text='Archive\n& reset', command=self.ArchiveReset).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Register binds for changing tabs
        if self.tab_switch_keys_global:
            self.tab3.tab2.hk.register(['control', 'shift', 'next'], callback=lambda event: self._next_tab())
            self.tab3.tab2.hk.register(['control', 'shift', 'prior'], callback=lambda event: self._prev_tab())
        else:
            self.root.bind_all('<Control-Shift-Next>', lambda event: self._next_tab())
            self.root.bind_all('<Control-Shift-Prior>', lambda event: self._prev_tab())

        # Load save state and start autosave process
        active_state = self.load_state_file()
        self.LoadActiveState(active_state)
        self._autosave_state()

        # Apply styling options
        self.theme.apply_theme_style()
        self.theme.update_colors()

        # Start the program
        self.root.mainloop()

    def toggle_drop_tab(self):
        if self.pop_up_drop_window:
            tab_name = next((x for x in self.tabcontrol.tabs() if x.endswith('drops')), '')
            if tab_name in self.tabcontrol.tabs():
                self.tabcontrol.forget(tab_name)
            self.root.config(borderwidth=2, relief='raised', height=622, width=240)
            self.tab2.pack(side=tk.BOTTOM)
            self.tab2.m.config(height=8)
            self.drop_lab.pack(side=tk.BOTTOM)
        else:
            if hasattr(self, 'drop_lab'):
                self.drop_lab.forget()
                self.tab2.forget()
            self.root.config(borderwidth=2, relief='raised', height=405, width=240)
            self.tabcontrol.add(self.tab2, text='Drops')
            self.tabcontrol.insert(1, self.tab2)
            self.tab2.m.config(height=12)

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
        hwnd = win32gui.FindWindow(None, self.title)
        if self.clickable:
            # Get window style and perform a 'bitwise or' operation to make the style layered and transparent, achieving
            # the clickthrough property
            l_ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            l_ex_style |= win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, l_ex_style)

            # Set the window to be transparent and appear always on top
            win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 190, win32con.LWA_ALPHA)  # transparent
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, self.root.winfo_x(), self.root.winfo_y(), 0, 0, 0)
            self.clickable = False
        else:
            # Calling the function again sets the extended style of the window to zero, reverting to a standard window
            win32api.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 0)
            if not self.always_on_top:
                # Remove the always on top property again, in case always on top was set to false in options
                win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, self.root.winfo_x(), self.root.winfo_y(), 0, 0, 0)
            self.clickable = True

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
            if not self.tab1.is_paused:
                self.tab1.Pause()
            self.tab4.update_descriptive_statistics()
        # A 'hack' to ensure that dropdown menus don't take focus immediate when you switch tabs by focusing the banner
        # image instead :)
        self.img_panel.focus_force()

    @staticmethod
    def make_profile_folder():
        if not os.path.isdir('Profiles'):
            os.makedirs('Profiles')

    def load_state_file(self):
        """
        Loads the save file for the active profile. Ensures directory exists, and if not it is created. Ensures the
        file exists, and if not an empty dictionary is returned.
        """
        self.make_profile_folder()
        file = 'Profiles/%s.json' % self.active_profile
        if not os.path.isfile(file):
            state = dict()
        else:
            with open(file, 'r') as fo:
                state = json.load(fo)
        return state

    def _autosave_state(self):
        """
        Function to run the autosave loop that saves the profile every 30 seconds
        """
        self.SaveActiveState()
        self.root.after(30000, self._autosave_state)

    def ResetSession(self):
        """
        Resets session for the timer module and drops from the drops module
        """
        self.tab1.ResetSession()
        self.tab2.drops = dict()
        self.tab2.m.delete(0, tk.END)

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
        user_confirm = tk_utils.mbox('Would you like to save and reset session?', b1='Yes', b2='No', coords=[xc, yc])
        if user_confirm:
            # Stop any active run and load current session info from timer and drop module.
            self.tab1.Stop()
            active = self.tab1.SaveState()
            active.update(dict(drops=self.tab2.save_state()))

            # Update session dropdown for the profile
            stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            self.tab4.available_archive.append(stamp)
            self.tab4.archive_dropdown['values'] = self.tab4.available_archive

            # Update profile .json with the session
            state = self.load_state_file()
            state['active_state'] = dict()
            state[stamp] = active
            file = 'Profiles/%s.json' % self.active_profile
            with open(file, 'w') as fo:
                json.dump(state, fo, indent=2)

            # When session has been successfully saved, the session is reset
            self.ResetSession()

    def LoadActiveState(self, state):
        """
        Loads the input state into the timer and drop modules. This is called at start-up when loading the profile .json
        and when you change the active profile in the profiles tab.
        """
        active_state = state.get('active_state', dict())
        self.tab1.load_from_state(active_state)
        self.tab2.load_from_state(active_state)

    def SaveActiveState(self):
        """
        Loads the .json for the profile, and replaces the 'active_state' key with the current active state, whereafter
        it is saved to file.
        """
        cache = self.load_state_file()
        cache['active_state'] = self.tab1.SaveState()
        cache['active_state'].update(dict(drops=self.tab2.save_state()))
        file = 'Profiles/%s.json' % self.active_profile
        with open(file, 'w') as fo:
            json.dump(cache, fo, indent=2)

    def Quit(self):
        """
        Stops the active run, updates config, saves current state to profile .json, and finally calls 'os._exit',
        terminating all active threads.
        """
        if self.tab1.is_running:
            self.tab1.Stop()
        self.update_config(self)
        self.SaveActiveState()
        os._exit(0)


MainFrame()
