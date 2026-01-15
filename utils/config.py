from init import *
import os
import base64
import configparser
import system_hotkey
from tkinter import messagebox, filedialog
from utils import other_utils, color_themes
mf_config_path = 'mf_config.ini'


class Config:
    def __init__(self):
        self.cfg = self.load_config_file()

        # Build/load config file
        self.logging_level = self.cfg['DEFAULT']['logging_level']
        self.game_path = self.cfg['DEFAULT']['game_path']
        self.herokuapp_username = self.cfg['DEFAULT']['herokuapp_username']
        self.herokuapp_password = base64.b64decode(self.cfg['DEFAULT']['herokuapp_password']).decode('utf-8')
        self.webproxies = other_utils.safe_eval(self.cfg['DEFAULT']['webproxies'])
        self.automode = other_utils.safe_eval(self.cfg['AUTOMODE']['automode'])
        self.end_run_in_menu = other_utils.safe_eval(self.cfg['AUTOMODE']['end_run_in_menu'])
        self.pause_on_esc_menu = other_utils.safe_eval(self.cfg['AUTOMODE']['pause_on_esc_menu'])
        self.pause_in_town = other_utils.safe_eval(self.cfg['AUTOMODE']['pause_in_town'])
        self.always_on_top = other_utils.safe_eval(self.cfg['OPTIONS']['always_on_top'])
        self.tab_switch_keys_global = other_utils.safe_eval(self.cfg['OPTIONS']['tab_switch_keys_global'])
        self.check_for_new_version = other_utils.safe_eval(self.cfg['OPTIONS']['check_for_new_version'])
        self.enable_sound_effects = other_utils.safe_eval(self.cfg['OPTIONS']['enable_sound_effects'])
        self.start_run_delay_seconds = other_utils.safe_eval(self.cfg['OPTIONS']['start_run_delay_seconds'])
        self.show_drops_frame = other_utils.safe_eval(self.cfg['OPTIONS']['show_drops_tab_below'])
        self.active_theme = self.cfg['OPTIONS']['active_theme'].lower()
        self.auto_upload_herokuapp = other_utils.safe_eval(self.cfg['OPTIONS']['auto_upload_herokuapp'])
        self.auto_archive_hours = other_utils.safe_eval(self.cfg['OPTIONS']['auto_archive_hours'])
        self.autocompletion_unids = other_utils.safe_eval(self.cfg['OPTIONS']['autocompletion_unids'])
        self.pd2_mode = other_utils.safe_eval(self.cfg['OPTIONS']['pd2_mode'])
        self.add_to_last_run = other_utils.safe_eval(self.cfg['OPTIONS']['add_to_last_run'])
        self.disable_scaling = other_utils.safe_eval(self.cfg['OPTIONS']['disable_dpi_scaling'])
        self.advanced_tracker_open = other_utils.safe_eval(self.cfg['AUTOMODE']['advanced_tracker_open'])
        self.active_profile = self.cfg['DEFAULT']['active_profile']
        self.window_start_pos = other_utils.safe_eval(self.cfg['DEFAULT']['window_start_position'])

        # UI config
        self.show_buttons = other_utils.safe_eval(self.cfg['UI']['show_buttons'])
        self.show_drops_section = other_utils.safe_eval(self.cfg['UI']['show_drops_section'])
        self.show_advanced_tracker = other_utils.safe_eval(self.cfg['UI']['show_advanced_tracker'])
        self.show_xp_tracker = other_utils.safe_eval(self.cfg['UI']['show_xp_tracker'])
        self.track_kills_min = other_utils.safe_eval(self.cfg['UI']['track_kills_min'])

        if self.active_theme not in color_themes.available_themes:
            self.active_theme = color_themes.available_themes[0]
        self.theme = color_themes.Theme(used_theme=self.active_theme)

    @staticmethod
    def find_game_path(force_find=False):
        if force_find:
            path = filedialog.askdirectory(title='Please select directory')
        else:
            possible_paths = [
                f'C:/Users/{os.getenv("username")}/Saved Games/Diablo II Resurrected/',
                'C:/Program Files (x86)/Diablo II - 1.13c/Save/',
                'C:/Program Files (x86)/Diablo II Plugy/Save/',
                'C:/Program Files (x86)/Diablo II/Save/',
                'C:/Program Files (x86)/Diablo II 1/Save/',
                'C:/Program Files (x86)/Diablo II 2/Save/',
                'C:/Program Files/Diablo II PoD/Save/',
                'C:/Program Files/Diablo II/Save/',
                'C:/Program Files/Diablo II 1/Save/',
                'C:/Program Files/Diablo II 2/Save/',
                'C:/Diablo II PoD/Save/',
                'C:/Diablo II/Save/',
                'C:/Diablo II 1/Save/',
                'C:/Diablo II 2/Save/',
            ]
            path = next((path for path in possible_paths if os.path.exists(path)), '')
        return path

    def default_config(self):
        config = configparser.ConfigParser(comment_prefixes='# ', allow_no_value=True)
        config['DEFAULT']['game_path'] = self.find_game_path()
        config['DEFAULT']['window_start_position'] = str((100, 100))
        config['DEFAULT']['active_profile'] = ''
        config['DEFAULT']['herokuapp_username'] = ''
        config['DEFAULT']['herokuapp_password'] = ''
        config['DEFAULT']['webproxies'] = ''
        config['DEFAULT']['logging_level'] = 'WARNING'

        config.add_section('OPTIONS')
        config['OPTIONS']['always_on_top'] = '1'
        config['OPTIONS']['tab_switch_keys_global'] = '0'
        config['OPTIONS']['check_for_new_version'] = '1'
        config['OPTIONS']['enable_sound_effects'] = '0'
        config['OPTIONS']['show_drops_tab_below'] = '1'
        config['OPTIONS']['active_theme'] = 'dark'
        config['OPTIONS']['start_run_delay_seconds'] = '0.0'
        config['OPTIONS']['auto_upload_herokuapp'] = '0'
        config['OPTIONS']['auto_archive_hours'] = '0.0'
        config['OPTIONS']['autocompletion_unids'] = '0'
        config['OPTIONS']['add_to_last_run'] = '0'
        config['OPTIONS']['disable_dpi_scaling'] = '1'
        config['OPTIONS']['pd2_mode'] = '0'

        config.add_section('AUTOMODE')
        config['AUTOMODE']['automode'] = '0'
        config['AUTOMODE']['advanced_tracker_open'] = '0'
        config['AUTOMODE']['end_run_in_menu'] = '1'
        config['AUTOMODE']['pause_on_esc_menu'] = '0'
        config['AUTOMODE']['pause_in_town'] = '0'

        config.add_section('UI')
        config['UI']['show_buttons'] = '1'
        config['UI']['show_drops_section'] = '1'
        config['UI']['show_advanced_tracker'] = '1'
        config['UI']['show_xp_tracker'] = '1'
        config['UI']['track_kills_min'] = '0'

        config.add_section('VERSION')
        config['VERSION']['version'] = version

        config.add_section('KEYBINDS')
        config.set('KEYBINDS', '# Please only edit keybinds from within the app')
        config['KEYBINDS']['start_key'] = str(['Alt', 'Q'])
        config['KEYBINDS']['end_key'] = str(['Alt', 'W'])
        config['KEYBINDS']['delete_prev_key'] = str(['Control', 'NO_BIND'])
        config['KEYBINDS']['pause_key'] = str(['Control', 'Space'])
        config['KEYBINDS']['drop_key'] = str(['Alt', 'A'])
        config['KEYBINDS']['reset_key'] = str(['Alt', 'R'])
        config['KEYBINDS']['make_unclickable'] = str(['Alt', 'NO_BIND'])

        return config

    @staticmethod
    def delete_config_file():
        if os.path.isfile(mf_config_path):
            os.remove(mf_config_path)

    @staticmethod
    def build_config_file(config):
        try:
            with open(mf_config_path, 'w') as fo:
                config.write(fo)
        except PermissionError as e:
            messagebox.showerror('Permission error', 'You have placed "mf_timer.exe" in a restricted folder - Move "mf_timer.exe" to a non-restricted folder, or open it as admin.\n\n%s' % e)
            raise e

    def load_config_file(self):
        if not os.path.isfile(mf_config_path):
            self.build_config_file(self.default_config())
        parser = configparser.ConfigParser(comment_prefixes='# ', allow_no_value=True)
        with open(mf_config_path) as fi:
            parser.read_file(fi)

        self.merge_config_default(parser)

        # Check if any binds in config file is already used by the system, and remove them in case
        used = system_hotkey.check_used_hotkeys()
        for key, bind in parser['KEYBINDS'].items():
            valid_entry = bind is not None and len(bind) > 0 and bind[0] in ["[", "("]
            if valid_entry and tuple(str(x).lower() for x in other_utils.safe_eval(bind)) in used:
                parser['KEYBINDS'][key] = str([other_utils.safe_eval(bind)[0], 'NO_BIND'])
                messagebox.showerror('Used keybind', f'Configured keybind for {key} ({bind}) is already in use by the system.\nUnbinding "{key}" - please set a new bind in options.')

        return parser

    def merge_config_default(self, cfg):
        def_cfg = self.default_config()

        cfg_sections = cfg.sections()
        for sec in def_cfg.sections():
            if sec not in cfg_sections:
                cfg.add_section(sec)

        def_dict = {**def_cfg._sections, 'DEFAULT': dict(def_cfg['DEFAULT'])}
        cfg_dict = {**cfg._sections, 'DEFAULT': dict(cfg['DEFAULT'])}

        for sec in def_dict:
            for param in def_dict[sec]:
                if param not in cfg_dict[sec]:
                    cfg[sec][param] = def_cfg[sec][param]

    def update_config(self, parent):
        cfg = parent.cfg

        # Update position
        x = parent.root.winfo_x()
        y = parent.root.winfo_y()
        cfg['DEFAULT']['game_path'] = str(parent.game_path)
        cfg['DEFAULT']['window_start_position'] = str((x, y))
        cfg['DEFAULT']['active_profile'] = str(parent.active_profile)
        cfg['DEFAULT']['herokuapp_username'] = str(parent.herokuapp_username)
        cfg['DEFAULT']['herokuapp_password'] = str(base64.b64encode(parent.herokuapp_password.encode('utf-8')).decode('utf-8'))

        # Update flags
        cfg['OPTIONS']['always_on_top'] = str(parent.always_on_top)
        cfg['OPTIONS']['tab_switch_keys_global'] = str(parent.tab_switch_keys_global)
        cfg['OPTIONS']['check_for_new_version'] = str(parent.check_for_new_version)
        cfg['OPTIONS']['enable_sound_effects'] = str(parent.enable_sound_effects)
        cfg['OPTIONS']['show_drops_tab_below'] = str(int(parent.show_drops_frame))
        cfg['OPTIONS']['active_theme'] = str(parent.active_theme)
        cfg['OPTIONS']['start_run_delay_seconds'] = str(parent.start_run_delay_seconds)
        cfg['OPTIONS']['auto_upload_herokuapp'] = str(parent.auto_upload_herokuapp)
        cfg['OPTIONS']['auto_archive_hours'] = str(parent.auto_archive_hours)
        cfg['OPTIONS']['autocompletion_unids'] = str(parent.autocompletion_unids)
        cfg['OPTIONS']['add_to_last_run'] = str(parent.add_to_last_run)
        cfg['OPTIONS']['pd2_mode'] = str(parent.pd2_mode)

        # Update automodes
        cfg['AUTOMODE']['automode'] = str(parent.automode)
        cfg['AUTOMODE']['advanced_tracker_open'] = str(int(parent.advanced_stats_caret.active)) if parent.automode == 2 else '0'
        cfg['AUTOMODE']['end_run_in_menu'] = str(parent.end_run_in_menu)
        cfg['AUTOMODE']['pause_on_esc_menu'] = str(parent.pause_on_esc_menu)
        cfg['AUTOMODE']['pause_in_town'] = str(parent.pause_in_town)

        cfg['UI']['show_buttons'] = str(parent.show_buttons)
        cfg['UI']['show_drops_section'] = str(parent.show_drops_section)
        cfg['UI']['show_advanced_tracker'] = str(parent.show_advanced_tracker)
        cfg['UI']['show_xp_tracker'] = str(parent.show_xp_tracker)
        cfg['UI']['track_kills_min'] = str(parent.track_kills_min)

        # Update hotkeys
        cfg.remove_section('KEYBINDS')
        cfg.add_section('KEYBINDS')
        cfg.set('KEYBINDS', '# Please only edit keybinds from within the app')
        cfg['KEYBINDS']['start_key'] = str(parent.options_tab.tab3._start_new_run)
        cfg['KEYBINDS']['end_key'] = str(parent.options_tab.tab3._end_run)
        cfg['KEYBINDS']['delete_prev_key'] = str(parent.options_tab.tab3._delete_prev)
        cfg['KEYBINDS']['pause_key'] = str(parent.options_tab.tab3._pause)
        cfg['KEYBINDS']['drop_key'] = str(parent.options_tab.tab3._add_drop)
        cfg['KEYBINDS']['reset_key'] = str(parent.options_tab.tab3._reset_lap)
        cfg['KEYBINDS']['make_unclickable'] = str(parent.options_tab.tab3._make_unclickable)

        self.build_config_file(cfg)
