from init import *
import sys
import time
import json
import queue
import base64
import logging
import ctypes
import traceback
import win32api
import win32gui
import win32con
from memory_reader import reader
from utils.config import Config
from tabs.options import Options
from tabs.profiles import Profile
from utils.color_themes import Theme, available_themes
from tkinter import messagebox
import tkinter as tk
from utils import tk_dynamic as tkd, tk_utils, github_releases, other_utils
from tabs.stats_tracker import StatsTracker
from tabs.about import About
from tabs.drops import Drops
from tabs.mf_timer import MFRunTimer
from tabs.grail import Grail

# FIXME: Show active profile on main tab somehow
# FIXME: Add option to export/upload to google sheets

# FIXME: Solve an issue with tooltips showing outside of the screen
# FIXME: Solve issue with bad synced sound effects (add sound effect when automode is active and starting new run)
# FIXME: Retain order of item table when adding new drops

# FIXME: Pause session and XP timer on pause call
# FIXME: Ability to select which run to archive drop on
# FIXME: Advanced automode and 2 diablo instances...?
# FIXME: Archive reset should always use last update time as stamp
# FIXME: Save relative XP gained in the XP tracker
# FIXME: Save all XP stuff under a character name, so multiple characters wont break it. Also save under individual levels
# FIXME: Build a proper logger

# FIXME: Add item by hovering over it in D2 and pressing hotkey (both for items picked up and on ground)


class MainFrame(Config):
    def __init__(self):
        # Create root
        self.root = tkd.Tk()

        # Create logger
        # logging.basicConfig(filename='mf_counter.log',
        #                     filemode='w',
        #                     format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        #                     datefmt='%H:%M:%S',
        #                     level=logging.DEBUG)

        # Check if application is already open
        self.title = 'MF run counter'
        if win32gui.FindWindow(None, self.title):
            tk.messagebox.showerror('Error', 'Application is already open. Cannot open another instance')
            sys.exit(0)

        # Ensure errors are handled with an exception pop-up if encountered
        self.root.report_callback_exception = self.report_callback_exception

        # Build/load config file
        self.cfg = self.load_config_file()
        self.SP_game_path = self.cfg['DEFAULT']['SP_game_path']
        self.MP_game_path = self.cfg['DEFAULT']['MP_game_path']
        self.herokuapp_username = self.cfg['DEFAULT']['herokuapp_username']
        self.herokuapp_password = base64.b64decode(self.cfg['DEFAULT']['herokuapp_password']).decode('utf-8')
        self.webproxies = other_utils.safe_eval(self.cfg['DEFAULT']['webproxies'])
        self.automode = other_utils.safe_eval(self.cfg['AUTOMODE']['automode'])
        self.stop_when_leaving = other_utils.safe_eval(self.cfg['AUTOMODE']['stop_when_leaving'])
        self.always_on_top = other_utils.safe_eval(self.cfg['OPTIONS']['always_on_top'])
        self.tab_switch_keys_global = other_utils.safe_eval(self.cfg['OPTIONS']['tab_switch_keys_global'])
        self.check_for_new_version = other_utils.safe_eval(self.cfg['OPTIONS']['check_for_new_version'])
        self.enable_sound_effects = other_utils.safe_eval(self.cfg['OPTIONS']['enable_sound_effects'])
        self.start_run_delay_seconds = other_utils.safe_eval(self.cfg['OPTIONS']['start_run_delay_seconds'])
        self.show_drops_tab_below = other_utils.safe_eval(self.cfg['OPTIONS']['show_drops_tab_below'])
        self.active_theme = self.cfg['OPTIONS']['active_theme'].lower()
        self.auto_upload_herokuapp = other_utils.safe_eval(self.cfg['OPTIONS']['auto_upload_herokuapp'])
        self.auto_archive_hours = other_utils.safe_eval(self.cfg['OPTIONS']['auto_archive_hours'])

        # Initiate d2loader for memory reading
        self.is_user_admin = reader.is_user_admin()
        self.d2_version_supported = True
        self.d2_reader = None
        self.cached_is_ingame = None

        # Load theme
        if self.active_theme not in available_themes:
            self.active_theme = 'vista'
        self.theme = Theme(used_theme=self.active_theme)

        # Create hotkey queue and initiate process for monitoring the queue
        self.queue = queue.Queue(maxsize=1)
        self.process_queue()

        # Check for version update
        if self.check_for_new_version:
            github_releases.check_newest_version(release_repo)

        # Load profile info
        self.make_profile_folder()
        self.profiles = [x[:-5] for x in os.listdir('Profiles') if x.endswith('.json') and not x == 'grail.json']
        self.active_profile = self.cfg['DEFAULT']['active_profile']
        if len(self.profiles) == 0:
            self.active_profile = ''
        elif len(self.profiles) > 0 and self.active_profile not in self.profiles:
            self.active_profile = self.profiles[0]

        self.profiles = self.sorted_profiles()

        # Modify root window
        self.root.title(self.title)
        self.clickable = True
        self.root.resizable(False, False)
        self.root.geometry('+%d+%d' % other_utils.safe_eval(self.cfg['DEFAULT']['window_start_position']))
        self.root.config(borderwidth=2, height=442, width=240, relief='raised')
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
        self.img_panel.bind("<ButtonPress-1>", self.root.start_move)
        self.img_panel.bind("<ButtonRelease-1>", self.root.stop_move)
        self.img_panel.bind("<B1-Motion>", self.root.on_motion)
        self.root.bind("<Delete>", self.delete_selection)
        self.root.bind("<Left>", self.root.moveleft)
        self.root.bind("<Right>", self.root.moveright)
        self.root.bind("<Up>", self.root.moveup)
        self.root.bind("<Down>", self.root.movedown)

        # Build tabs
        self.drops_frame = tkd.Frame(self.root)
        self.tabcontrol = tkd.Notebook(self.root)
        self.profile_tab = Profile(self, parent=self.tabcontrol)
        self.timer_tab = MFRunTimer(self, parent=self.tabcontrol)
        self.drops_tab = Drops(self, parent=self.drops_frame)
        self.options_tab = Options(self, self.timer_tab, self.drops_tab, parent=self.tabcontrol)
        self.grail_tab = Grail(self, parent=self.tabcontrol)
        self.about_tab = About(parent=self.tabcontrol)

        self.tabcontrol.add(self.timer_tab, text='Timer')
        self.tabcontrol.add(self.options_tab, text='Options')
        self.tabcontrol.add(self.profile_tab, text='Profile')
        self.tabcontrol.add(self.grail_tab, text='Grail')
        self.tabcontrol.add(self.about_tab, text='About')

        self.tabcontrol.pack(expand=False, fill=tk.BOTH)
        self.root.bind("<<NotebookTabChanged>>", lambda e: self.notebook_tab_change())
        self.profile_tab.update_descriptive_statistics()

        # Add buttons to main widget
        btn_frame = tkd.Frame(self.root)
        btn_frame.pack(expand=False, fill=tk.BOTH, side=tk.TOP)
        tkd.Button(btn_frame, text='Delete selection', command=self.delete_selection).pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=[2, 1], pady=1)
        tkd.Button(btn_frame, text='Archive session', command=self.ArchiveReset).pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=[0,1], pady=1)

        self.drops_frame.pack(fill=tk.BOTH, expand=True)
        self.toggle_drops_frame(show=self.show_drops_tab_below)
        self.drops_caret = tkd.CaretButton(self.drops_frame, active=self.show_drops_tab_below, command=self.toggle_drops_frame, text='Drops', compound=tk.RIGHT, height=13)
        self.drops_caret.propagate(False)
        self.drops_caret.pack(side=tk.BOTTOM, fill=tk.X, expand=True, padx=[2,1], pady=[0, 1])

        tracker_is_active = other_utils.safe_eval(self.cfg['AUTOMODE']['advanced_tracker_open']) and self.automode == 2 and self.is_user_admin
        self.advanced_stats_tracker = StatsTracker(self)
        self.advanced_stats_caret = tkd.CaretButton(self.root, active=tracker_is_active, text='Advanced stats', compound=tk.RIGHT, height=13, command=self.toggle_advanced_stats_frame)
        self.advanced_stats_caret.propagate(False)
        self.advanced_stats_caret.pack(side=tk.BOTTOM, fill=tk.X, expand=True, padx=[2, 1], pady=[0, 1])

        # Register binds for changing tabs
        if self.tab_switch_keys_global:
            self.options_tab.tab2.hk.register(['control', 'shift', 'next'], callback=lambda event: self.queue.put(self.tabcontrol.next_tab))
            self.options_tab.tab2.hk.register(['control', 'shift', 'prior'], callback=lambda event: self.queue.put(self.tabcontrol.prev_tab))
        else:
            self.root.bind_all('<Control-Shift-Next>', lambda event: self.tabcontrol.next_tab())
            self.root.bind_all('<Control-Shift-Prior>', lambda event: self.tabcontrol.prev_tab())

        # Load save state and start autosave process
        active_state = self.load_state_file()
        self.LoadActiveState(active_state)
        self.root.after(30000, self._autosave_state)

        # Apply styling options
        self.theme.apply_theme_style()
        self.theme.update_colors()

        # Automode and advanced stats loop
        self.toggle_automode()
        self.toggle_advanced_stats_frame(show=tracker_is_active)

        # A trick to disable windows DPI scaling - the app doesnt work well with scaling, unfortunately
        ctypes.windll.shcore.SetProcessDpiAwareness(2)

        # Used if "auto archive session" is activated
        self.profile_tab.auto_reset_session()

        # Start the program
        self.root.mainloop()

    def delete_selection(self, event=None):
        if self.timer_tab.m.curselection():
            self.timer_tab.delete_selected_run()
        elif self.drops_tab.focus_get()._name == 'droplist':
            self.drops_tab.delete_selected_drops()

    def load_memory_reader(self, show_err=True):
        try:
            assert self.automode == 2
            assert self.is_user_admin is True
            self.d2_reader = reader.D2Reader()
            self.cached_is_ingame = self.d2_reader.in_game()
        except other_utils.pymem_err_list as e:
            # logging.debug('D2memory read error: %s' % e)
            if e.__class__ is NotImplementedError:
                if self.d2_version_supported is True or show_err:
                    tk.messagebox.showerror('D2 version error', 'Advanced automode currently only supports D2 patch versions 1.13c, 1.13d and 1.14d, your version is "%s".\n\nDisabling automode.' % e)
                self.d2_version_supported = False
            else:
                self.d2_version_supported = True
            self.d2_reader = None
            self.cached_is_ingame = None
            if show_err and not self.is_user_admin:
                tk.messagebox.showerror('Elevated access rights',
                                        'You must run the app as ADMIN to initialize memory reader for advanced automode.\n\nDisabling automode. %s' % e)

    def sorted_profiles(self):
        def sort_key(x):
            file = 'Profiles/%s.json' % x
            if not os.path.isfile(file):
                return float('inf')
            else:
                with open(file, 'r') as fo:
                    state = json.load(fo)
                return state.get('extra_data', dict()).get('Last update', os.stat(file).st_mtime)
        return sorted(self.profiles, key=sort_key, reverse=True)

    def game_path(self):
        game_mode = self.profile_tab.game_mode.get()
        if game_mode == 'Single Player':
            return self.SP_game_path
        else:
            return self.MP_game_path

    def character_file_extension(self):
        game_mode = self.profile_tab.game_mode.get()
        if game_mode == 'Single Player':
            return '.d2s'
        else:
            return '.map'

    def toggle_automode(self, char_name=None):
        """
        Enables or disables automode. Shows a small label on top of the banner image with the text "Automode" when
        automode is activated. Takes an optional argument "char_name" which is used by the profile manager when changing
        between profiles, such that the automode loop listens to changes in the correct save file.
        """
        if hasattr(self, 'am_lab'):
            self.am_lab.destroy()
        if char_name is None:
            char_name = self.profile_tab.char_name.get()
        if self.automode:
            self.am_lab = tk.Label(self.root, text="Automode", fg="white", bg="black")
            self.am_lab.place(x=1, y=1)
        self.timer_tab.toggle_automode(char_name=char_name)

    def toggle_tab_keys_global(self):
        """
        Change whether tab switching keybind (ctrl-shift-pgup/pgdn) works only when the app has focus, or also when
        the app doesn't have focus. Added this feature, as some users might have this keybind natively bound to sth else
        """
        if self.tab_switch_keys_global:
            self.root.unbind_all('<Control-Shift-Next>')
            self.root.unbind_all('<Control-Shift-Prior>')
            self.options_tab.tab2.hk.register(['control', 'shift', 'next'], callback=lambda event: self.queue.put(self.tabcontrol.next_tab))
            self.options_tab.tab2.hk.register(['control', 'shift', 'prior'], callback=lambda event: self.queue.put(self.tabcontrol.prev_tab))
        else:
            self.options_tab.tab2.hk.unregister(['control', 'shift', 'next'])
            self.options_tab.tab2.hk.unregister(['control', 'shift', 'prior'])
            self.root.bind_all('<Control-Shift-Next>', lambda event: self.tabcontrol.next_tab())
            self.root.bind_all('<Control-Shift-Prior>', lambda event: self.tabcontrol.prev_tab())

    def toggle_drops_frame(self, show=None):
        if show is None:
            show = self.drops_caret.active
        if show:
            self.root.update()
            self.root.config(height=self.root.winfo_height()+174)
            self.drops_tab.pack(pady=[0, 2])
        else:
            if hasattr(self, 'drops_tab') and self.drops_tab.winfo_ismapped():
                self.drops_tab.forget()
                self.root.config(height=self.root.winfo_height()-174)
        self.show_drops_tab_below = show
        self.img_panel.focus_force()

    def toggle_advanced_stats_frame(self, show=None):
        if show is None:
            show = self.advanced_stats_caret.active
        if self.automode != 2:
            if show:
                messagebox.showerror('Error', 'You need to active "Advanced auto mode" in Options->Automode to see advanced stats')
            show = False
            self.advanced_stats_caret.toggle_image(active=False)
        tracker_height = 300
        if show:
            self.root.update()
            self.root.config(height=self.root.winfo_height()+tracker_height)
            self.advanced_stats_tracker.pack()
            self.advanced_stats_tracker.update_loop()
        else:
            if hasattr(self.advanced_stats_tracker, 'after_updater'):
                self.advanced_stats_tracker.forget()
                self.root.config(height=self.root.winfo_height()-tracker_height)
                self.advanced_stats_tracker.after_cancel(self.advanced_stats_tracker.after_updater)
                delattr(self.advanced_stats_tracker, 'after_updater')

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
        tk.messagebox.showerror('Exception occured', 'Data before last autosave is lost...\n\n' + ''.join(err))
        os._exit(0)

    def notebook_tab_change(self):
        """
        When tab is switched to profile, the descriptive statistics are updated.
        """
        x = self.tabcontrol.select()
        if x.endswith('profile'):
            self.SaveActiveState()
            self.profile_tab.profile_dropdown['values'] = self.sorted_profiles()
            self.profile_tab.update_descriptive_statistics()
        # A 'hack' to ensure that dropdown menus don't take focus immediately when you switch tabs by focusing the
        # banner image instead :)
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
        self.timer_tab.reset_session()
        self.drops_tab.reset_session()
        self.advanced_stats_tracker.reset_session()

    def ArchiveReset(self, skip_confirm=False, notify_msg=None, stamp_from_epoch=None):
        """
        If any laps or drops have been recorded, this function saves the current session to the profile archive, and
        resets all info in the active session. In case no runs/drops are recorded, the session timer is simply reset
        """
        if not self.timer_tab.laps and not self.drops_tab.drops:
            self.ResetSession()
            return

        xc = self.root.winfo_rootx() - self.root.winfo_width()//12
        yc = self.root.winfo_rooty() + self.root.winfo_height()//3
        if notify_msg is not None:
            tk.messagebox.showinfo(title='Archive', message=notify_msg)
        if skip_confirm or tk_utils.mbox('Would you like to save and reset session?', b1='Yes', b2='No', coords=[xc, yc], master_root=self.root):
            # Stop any active run and load current session info from timer and drop module.
            self.timer_tab.stop()
            active = self.timer_tab.save_state()
            self.profile_tab.tot_laps += len(active['laps'])
            active.update(self.drops_tab.save_state())
            active.update(self.advanced_stats_tracker.save_state())

            # Update session dropdown for the profile
            if stamp_from_epoch is None:
                stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            else:
                stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stamp_from_epoch))
            self.profile_tab.available_archive.append(stamp)
            self.profile_tab.archive_dropdown['values'] = self.profile_tab.available_archive
            # self.profile_tab.update_descriptive_statistics()

            # Update profile .json with the session
            state = self.load_state_file()
            state['active_state'] = dict()
            state[stamp] = active
            state.setdefault('extra_data', dict())['Last update'] = time.time()

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
        self.timer_tab.load_from_state(active_state)
        self.drops_tab.load_from_state(active_state)
        self.advanced_stats_tracker.load_from_state(active_state)

    def SaveActiveState(self):
        """
        Loads the .json for the profile, and replaces the 'active_state' key with the current active state, whereafter
        it is saved to file.
        """
        cache = self.load_state_file()
        timer_state = self.timer_tab.save_state()
        drops_state = self.drops_tab.save_state()
        advanced_stats_state = self.advanced_stats_tracker.save_state()
        if cache.get('active_state', dict()).get('laps', []) != timer_state.get('laps', []) or cache.get('active_state', dict()).get('drops', dict()) != drops_state.get('drops', dict()):
            is_updated = True
        else:
            is_updated = False
        cache['active_state'] = {**timer_state, **drops_state, **advanced_stats_state}
        cache.setdefault('extra_data', dict())['Game mode'] = self.profile_tab.game_mode.get()
        if is_updated or 'Last update' not in cache['extra_data']:
            cache['extra_data']['Last update'] = time.time()
        file = 'Profiles/%s.json' % self.active_profile
        with open(file, 'w') as fo:
            json.dump(cache, fo, indent=2)
        self.grail_tab.save_grail()

    def Quit(self):
        """
        Stops the active run, updates config, saves current state to profile .json, and finally exits the application
        """
        if self.timer_tab.is_running and not (self.profile_tab.game_mode.get() == 'Single Player' and self.timer_tab.automode_active and self.automode == 1):
            self.timer_tab.stop()
        self.SaveActiveState()
        self.update_config(self)
        sys.exit()


try:
    MainFrame()
except Exception as e:
    logging.basicConfig(filename='mf_timer.log',
                        filemode='w',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    logging.debug(e)
    raise e