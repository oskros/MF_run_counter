from init import *
import os
import configparser
import system_hotkey
from tkinter import messagebox


class Config:
    @staticmethod
    def find_SP_game_path():
        possible_paths = [
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
        return next((path for path in possible_paths if os.path.exists(path)), '')

    @staticmethod
    def find_MP_game_path():
        possible_paths = [
            'C:/Diablo 2/Diablo II/Path of Diablo/Save/Path of Diablo',
            'C:/Program Files (x86)/Diablo II PoD/Path of Diablo/Save/Path of Diablo/',
            'C:/Program Files (x86)/Diablo II/Path of Diablo/Save/Path of Diablo/',
            'C:/Program Files (x86)/Diablo II 1/Path of Diablo/Save/Path of Diablo/',
            'C:/Program Files (x86)/Diablo II 2/Path of Diablo/Save/Path of Diablo/',
            'C:/Program Files/Diablo II PoD/Path of Diablo/Save/Path of Diablo/',
            'C:/Program Files/Diablo II/Path of Diablo/Save/Path of Diablo/',
            'C:/Program Files/Diablo II 1/Path of Diablo/Save/Path of Diablo/',
            'C:/Program Files/Diablo II 2/Path of Diablo/Save/Path of Diablo/',
            'C:/Diablo II PoD/Path of Diablo/Save/Path of Diablo/',
            'C:/Diablo II/Path of Diablo/Save/Path of Diablo/',
            'C:/Diablo II 1/Path of Diablo/Save/Path of Diablo/',
            'C:/Diablo II 2/Path of Diablo/Save/Path of Diablo/',
        ]
        return next((path for path in possible_paths if os.path.exists(path)), '')

    def default_config(self):
        config = configparser.ConfigParser(comment_prefixes='# ', allow_no_value=True)
        config['DEFAULT']['SP_game_path'] = self.find_SP_game_path()
        config['DEFAULT']['MP_game_path'] = self.find_MP_game_path()
        config['DEFAULT']['window_start_position'] = str((100, 100))
        config['DEFAULT']['active_profile'] = ''

        config.add_section('OPTIONS')
        config['OPTIONS']['automode'] = '0'
        config['OPTIONS']['always_on_top'] = '1'
        config['OPTIONS']['tab_switch_keys_global'] = '0'
        config['OPTIONS']['check_for_new_version'] = '1'
        config['OPTIONS']['enable_sound_effects'] = '0'
        config['OPTIONS']['pop_up_drop_window'] = '0'
        config['OPTIONS']['active_theme'] = 'default'
        config['OPTIONS']['run_timer_delay_seconds'] = '0.0'
        config['OPTIONS']['autocomplete'] = '1'
        config['OPTIONS']['item_shortnames'] = '0'

        config.add_section('VERSION')
        config['VERSION']['version'] = version

        config.add_section('KEYBINDS')
        config.set('KEYBINDS', '# Please only edit keybinds from within the app')
        config['KEYBINDS']['start_key'] = str(['Alt', 'Q'])
        config['KEYBINDS']['end_key'] = str(['Alt', 'W'])
        config['KEYBINDS']['delete_prev_key'] = str(['Control', 'Delete'])
        config['KEYBINDS']['pause_key'] = str(['Control', 'Space'])
        config['KEYBINDS']['drop_key'] = str(['Alt', 'A'])
        config['KEYBINDS']['reset_key'] = str(['Alt', 'R'])
        config['KEYBINDS']['make_unclickable'] = str(['Alt', 'NO_BIND'])

        return config

    @staticmethod
    def delete_config_file():
        if os.path.isfile('mf_config.ini'):
            os.remove('mf_config.ini')

    @staticmethod
    def build_config_file(config):
        with open('mf_config.ini', 'w') as fo:
            config.write(fo)

    def load_config_file(self):
        if not os.path.isfile('mf_config.ini'):
            self.build_config_file(self.default_config())
        parser = configparser.ConfigParser(comment_prefixes='# ', allow_no_value=True)
        with open('mf_config.ini') as fi:
            parser.read_file(fi)

        if 'automode' in parser['DEFAULT'] and eval(parser['DEFAULT']['automode']) is True and 'game_path' not in parser['DEFAULT']:
            parser['DEFAULT']['game_path'] = self.find_SP_game_path()

        try:
            ver = parser.get('VERSION', 'version')
        except:
            ver = 0
        if ver != version:
            self.delete_config_file()
            parser = self.load_config_file()
            messagebox.showinfo('Config file recreated', 'You downloaded a new version. To ensure compatibility, config file has been recreated with default options.')

        # Check if any binds in config file is already used by the system, and remove them in case
        used = system_hotkey.check_used_hotkeys()
        for key, bind in parser['KEYBINDS'].items():
            if len(bind) > 0 and bind[0] in ["[", "("] and tuple(str(x).lower() for x in eval(bind)) in used:
                parser['KEYBINDS'][key] = str([eval(bind)[0], 'NO_BIND'])
                messagebox.showerror('Used keybind', 'Configured keybind for %s (%s) is already in use by the system.\nUnbinding "%s" - please set a new bind in options.' % (key, bind, key))

        return parser

    def update_config(self, parent):
        cfg = parent.cfg

        # Update position
        x = parent.root.winfo_x()
        y = parent.root.winfo_y()
        cfg['DEFAULT']['SP_game_path'] = str(parent.SP_game_path)
        cfg['DEFAULT']['MP_game_path'] = str(parent.MP_game_path)
        cfg['DEFAULT']['window_start_position'] = str((x, y))
        cfg['DEFAULT']['active_profile'] = str(parent.active_profile)

        # Update flags
        cfg['OPTIONS']['automode'] = str(parent.automode)
        cfg['OPTIONS']['always_on_top'] = str(parent.always_on_top)
        cfg['OPTIONS']['tab_switch_keys_global'] = str(parent.tab_switch_keys_global)
        cfg['OPTIONS']['check_for_new_version'] = str(parent.check_for_new_version)
        cfg['OPTIONS']['enable_sound_effects'] = str(parent.enable_sound_effects)
        cfg['OPTIONS']['pop_up_drop_window'] = str(parent.pop_up_drop_window)
        cfg['OPTIONS']['active_theme'] = str(parent.active_theme)
        cfg['OPTIONS']['run_timer_delay_seconds'] = str(parent.run_timer_delay_seconds)
        cfg['OPTIONS']['autocomplete'] = str(parent.autocomplete)
        cfg['OPTIONS']['item_shortnames'] = str(parent.item_shortnames)

        # Update hotkeys
        cfg.remove_section('KEYBINDS')
        cfg.add_section('KEYBINDS')
        cfg.set('KEYBINDS', '# Please only edit keybinds from within the app')
        cfg['KEYBINDS']['start_key'] = str(parent.tab3.tab2._start_new_run)
        cfg['KEYBINDS']['end_key'] = str(parent.tab3.tab2._end_run)
        cfg['KEYBINDS']['delete_prev_key'] = str(parent.tab3.tab2._delete_prev)
        cfg['KEYBINDS']['pause_key'] = str(parent.tab3.tab2._pause)
        cfg['KEYBINDS']['drop_key'] = str(parent.tab3.tab2._add_drop)
        cfg['KEYBINDS']['reset_key'] = str(parent.tab3.tab2._reset_lap)
        cfg['KEYBINDS']['make_unclickable'] = str(parent.tab3.tab2._make_unclickable)

        self.build_config_file(cfg)
