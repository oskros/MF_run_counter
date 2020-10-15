from utils import tk_dynamic as tkd, color_themes, other_utils
from collections import defaultdict
import tkinter as tk
import time
import logging


class StatsTracker(tkd.Frame):
    def __init__(self, main_frame, parent, **kw):
        tkd.Frame.__init__(self, parent, **kw)
        self.main_frame = main_frame

        self.session_char_xp_start = 0
        self.char_xp = 0
        self.char_xp_missing = 0
        self.run_char_xp_start = 0
        self.run_char_xp = 0

        self.session_time_start = time.time()
        self.session_time = 0.0
        self.session_xp_runs = set()

        # StringVars
        self.tot_kills_sv = tk.StringVar(value='0')
        self.unique_kills_sv = tk.StringVar(value='0')
        self.champ_kills_sv = tk.StringVar(value='0')
        self.name_sv = tk.StringVar(value='-----')

        self.level_sv = tk.StringVar(value='-----')
        self.mf_sv = tk.StringVar(value='-----')
        self.players_x_sv = tk.StringVar(value='-----')
        self.mon_kills_sv = tk.StringVar(value='0 / 0')

        self.exp_perc_sv = tk.StringVar(value='0')
        self.exp_session_sv = tk.StringVar(value='0')
        self.exp_run_sv = tk.StringVar(value='0')
        self.exp_hour_sv = tk.StringVar(value='0')

        self.exp_level_sv = tk.StringVar(value='0')
        self.hours_level_sv = tk.StringVar(value='0')
        self.runs_level_sv = tk.StringVar(value='0')

        self.make_widgets()
        color_themes.Theme(main_frame.active_theme).update_colors()

    def make_widgets(self):
        tkd.Label(self, text='Advanced stats tracker', font='Helvetica 15').pack()

        lf1 = tkd.LabelFrame(self)
        lf1.pack(expand=False, fill=tk.X, padx=1)
        self.create_row(self.level_sv, label_name='Level', lf=lf1)
        self.create_row(self.mf_sv, label_name='MF', lf=lf1)
        self.create_row(self.players_x_sv, label_name='Players X', lf=lf1)
        self.create_row(self.mon_kills_sv, label_name='Boss / champ kills', lf=lf1)

        lf2 = tkd.LabelFrame(self)
        lf2.pack(expand=False, fill=tk.X, padx=1, pady=8)
        self.create_row(self.exp_perc_sv, label_name='Exp %', lf=lf2)
        self.create_row(self.exp_session_sv, label_name='Exp (session)', lf=lf2)
        self.create_row(self.exp_run_sv, label_name='Exp (run)', lf=lf2)
        self.create_row(self.exp_hour_sv, label_name='Exp / hour', lf=lf2)

        lf3 = tkd.LabelFrame(self)
        lf3.pack(expand=False, fill=tk.X, padx=1)
        self.create_row(self.exp_level_sv, label_name='Exp to level', lf=lf3)
        self.create_row(self.hours_level_sv, label_name='Time to level', lf=lf3)
        self.create_row(self.runs_level_sv, label_name='Runs to level', lf=lf3)

    @staticmethod
    def create_row(svar, label_name, lf):
        fr = tkd.Frame(lf, height=22, width=236)
        fr.propagate(False)
        fr.pack(expand=False, fill=tk.X)

        tkd.Label(fr, text='%s:' % label_name, font='helvetica 10', anchor=tk.W, justify=tk.LEFT).pack(side=tk.LEFT)
        tkd.Label(fr, textvariable=svar, font='helvetica 12 bold', anchor=tk.E, justify=tk.RIGHT).pack(side=tk.RIGHT)

    def update_killcount(self):
        try:
            self.main_frame.d2_reader.update_dead_guids()
            self.tot_kills_sv.set(self.main_frame.d2_reader.kill_counts.get('Total', 0))
            self.unique_kills_sv.set(self.main_frame.d2_reader.kill_counts.get('Unique', 0))
            self.champ_kills_sv.set(self.main_frame.d2_reader.kill_counts.get('Champion', 0))
            self.mon_kills_sv.set('%s / %s' % (self.unique_kills_sv.get(), self.champ_kills_sv.get()))
        except other_utils.pymem_err_list as e:
            logging.debug(e)

    def update_loop(self):
        self._update_vars()
        self._update_svars()
        self.after_updater = self.after(200, self.update_loop)

    def _update_vars(self):
        # Pause session time when run is paused
        if not self.main_frame.timer_tab.session_running:
            self.session_time_start = time.time() - self.session_time
        self.session_time = time.time() - self.session_time_start

        # Return when not ingame
        if self.main_frame.d2_reader is None or not self.main_frame.timer_tab.cached_is_ingame:
            return

        self.update_killcount()

        # Catch any erors with loading player stats
        try:
            player_unit_stats = self.main_frame.d2_reader.player_unit_stats()
        except other_utils.pymem_err_list as e:
            logging.debug(e)
            return

        # Game has not loaded PlayerUnitStats yet (new created characters don't have the XP stat, so need an exception)
        if player_unit_stats['Exp'] == -1 and player_unit_stats['Level'] != 1:
            logging.debug('Failed to find XP and level, assuming stats are not loaded yet')
            return

        # Assign variables at first load of character
        if self.name_sv.get() == '-----' and self.session_char_xp_start == 0:
            self.session_char_xp_start = player_unit_stats['Exp']
            self.run_char_xp_start = self.session_char_xp_start

        # Reset when changing character (used to reset at level up, but removed this)
        self.reset_when_changes(player_unit_stats=player_unit_stats)

        self.name_sv.set(player_unit_stats['Name'])
        self.level_sv.set(player_unit_stats['Level'])
        if player_unit_stats['MF'] >= 0:
            self.mf_sv.set('%s%%' % player_unit_stats['MF'])
        self.players_x_sv.set(player_unit_stats['Players X'])
        self.exp_perc_sv.set('{0:.1f}%'.format(player_unit_stats['Exp %']*100))

        self.char_xp = player_unit_stats['Exp']
        self.char_xp_missing = player_unit_stats['Exp missing']
        self.run_char_xp = self.char_xp - self.run_char_xp_start

    def _update_svars(self):
        self.exp_session_sv.set('{:,.0f}'.format(self.char_xp - self.session_char_xp_start))
        xp_hour_session = 3600 * (self.char_xp - self.session_char_xp_start) / (self.session_time + 0.0001)
        self.exp_hour_sv.set('{:,.0f}'.format(xp_hour_session))
        self.exp_run_sv.set('{:,.0f}'.format(self.run_char_xp))

        self.exp_level_sv.set('{:,.0f}'.format(self.char_xp_missing))
        self.hours_level_sv.set(self.format_time(self.char_xp_missing / xp_hour_session) if xp_hour_session > 0 else '0')
        if len(self.session_xp_runs) > 0:
            avg_run = sum(self.session_xp_runs) / len(self.session_xp_runs)
            self.runs_level_sv.set('{:.0f}'.format(-(-self.char_xp_missing / avg_run // 1)))

    def reset_at_new_run(self):
        if self.run_char_xp > 0:
            self.session_xp_runs.add(self.run_char_xp)
        self.run_char_xp_start = self.char_xp
        self.run_char_xp = 0

        if self.main_frame.d2_reader is not None:
            self.main_frame.d2_reader.dead_guids = []
            self.main_frame.d2_reader.observed_guids = set()
            self.main_frame.d2_reader.kill_counts = defaultdict(lambda: 0)

        self.tot_kills_sv.set('0')
        self.unique_kills_sv.set('0')
        self.champ_kills_sv.set('0')
        self.mon_kills_sv.set('0 / 0')

    def reset_when_changes(self, player_unit_stats):
        if self.name_sv.get() != '-----' and player_unit_stats['Name'] != self.name_sv.get(): #  or str(player_unit_stats['Level']) != self.level_sv.get()):
            self.session_char_xp_start = player_unit_stats['Exp']
            self.session_time_start = time.time()
            self.session_time = 0.0
            self.run_char_xp_start = self.session_char_xp_start
            self.session_xp_runs = set()
            self.runs_level_sv.set('0')

    def reset_session(self):
        self.session_char_xp_start = 0
        self.char_xp = 0
        self.session_time_start = time.time()
        self.session_time = 0.0
        self.char_xp_missing = 0
        self.session_xp_runs = set()
        if hasattr(self, 'curr_run_xp'):
            delattr(self, 'curr_run_xp')

        self.name_sv.set('-----')
        self.level_sv.set('-----')
        self.mf_sv.set('-----')
        self.players_x_sv.set('-----')

        self.exp_perc_sv.set('0')
        self.exp_session_sv.set('0')
        self.exp_run_sv.set('0')
        self.exp_hour_sv.set('0')

        self.exp_level_sv.set('0')
        self.hours_level_sv.set('0')
        self.runs_level_sv.set('0')

    def save_state(self):
        return dict()#session_char_xp_start=self.session_char_xp_start,
                    # session_char_xp=self.session_char_xp,
                    # session_char_time_start=time.time() - self.session_char_time_start,
                    # session_char_xp_missing=self.session_char_xp_missing,
                    # session_xp_runs=list(self.session_xp_runs))

    def load_from_state(self, active_state):
        return

        # self.session_char_xp_start = active_state.get('session_char_xp_start', 0)
        # self.session_char_xp = active_state.get('session_char_xp', 0)
        # self.session_char_time_start = time.time() - active_state.get('session_char_time_start', 0)
        # self.session_char_xp_missing = active_state.get('session_char_xp_missing', 0)
        # self.session_xp_runs = set(active_state.get('session_xp_runs', set()))
        #
        # if self.session_char_xp > 0:
        #     self.curr_run_xp = self.session_char_xp
        #
        # self.name_sv.set('-----')
        # self.level_sv.set('-----')
        # self.mf_sv.set('-----')
        # self.players_x_sv.set('-----')
        #
        # self.exp_sv.set('0')
        # self.exp_level_sv.set('{:,.0f}'.format(self.session_char_xp_missing))
        # self.exp_session_sv.set('{:,.0f}'.format(self.session_char_xp - self.session_char_xp_start))
        # if len(self.session_xp_runs) > 0:
        #     self.avg_run = sum(self.session_xp_runs) / len(self.session_xp_runs)
        #     self.runs_level_sv.set('{:.0f}'.format(-(-self.session_char_xp_missing / self.avg_run // 1)))
        # else:
        #     self.runs_level_sv.set('0')

    @staticmethod
    def format_time(hours):
        h = hours // 1
        m = int(round((hours % 1)*60))
        return '%02dh:%02dm' % (h, m)

    def destroy(self):
        self.after_cancel(self.after_updater)
        tkd.Frame.destroy(self)
