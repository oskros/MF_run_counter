from init import *
import os
import configparser
import tk_utils
from tkinter import messagebox


class Config:
    exec(blocks[2])

    def default_config(self):
        config = configparser.ConfigParser(comment_prefixes='# ', allow_no_value=True)
        exec(blocks[3])
        config['DEFAULT']['window_start_position'] = str((100, 100))
        config['DEFAULT']['run_timer_delay_seconds'] = '0.0'
        config['DEFAULT']['active_profile'] = 'DEFAULT_PROFILE'

        config.add_section('OPTIONS')
        config['OPTIONS']['always_on_top'] = '1'
        config['OPTIONS']['tab_switch_keys_global'] = '1'
        config['OPTIONS']['check_for_new_version'] = '1'
        config['OPTIONS']['enable_sound_effects'] = '0'

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

        exec(blocks[4])

        try:
            ver = parser.get('VERSION', 'version')
        except:
            ver = 0
        if ver != version:
            self.delete_config_file()
            parser = self.load_config_file()
            messagebox.showinfo('Config file recreated', 'You downloaded a new version. To ensure compatibility, config file has been recreated.')
        return parser

    @staticmethod
    def UpdateConfig(parent):
        cfg = parent.cfg

        # Update position
        x = parent.root.winfo_x()
        y = parent.root.winfo_y()
        cfg['DEFAULT']['window_start_position'] = str((x, y))
        cfg['DEFAULT']['run_timer_delay_seconds'] = str(parent.run_timer_delay_seconds)
        cfg['DEFAULT']['active_profile'] = str(parent.active_profile)

        # Update flags
        cfg['OPTIONS']['always_on_top'] = str(parent.always_on_top)
        cfg['OPTIONS']['tab_switch_keys_global'] = str(parent.tab_switch_keys_global)
        cfg['OPTIONS']['check_for_new_version'] = str(parent.check_for_new_version)
        cfg['OPTIONS']['enable_sound_effects'] = str(parent.enable_sound_effects)

        # Update hotkeys
        cfg.remove_section('KEYBINDS')
        cfg.add_section('KEYBINDS')
        cfg.set('KEYBINDS', '# Please only edit keybinds from within the app')
        cfg['KEYBINDS']['start_key'] = str(parent.tab3.tab1._start_new_run)
        cfg['KEYBINDS']['end_key'] = str(parent.tab3.tab1._end_run)
        cfg['KEYBINDS']['delete_prev_key'] = str(parent.tab3.tab1._delete_prev)
        cfg['KEYBINDS']['pause_key'] = str(parent.tab3.tab1._pause)
        cfg['KEYBINDS']['drop_key'] = str(parent.tab3.tab1._add_drop)
        cfg['KEYBINDS']['reset_key'] = str(parent.tab3.tab1._reset_lap)
        cfg['KEYBINDS']['make_unclickable'] = str(parent.tab3.tab1._make_unclickable)

        parent.build_config_file(cfg)
