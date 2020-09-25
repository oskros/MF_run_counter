from utils import tk_dynamic as tkd, color_themes, other_utils
import tkinter as tk
import time


class StatsTracker(tkd.Frame):
    def __init__(self, main_frame, **kw):
        tkd.Frame.__init__(self, main_frame.root, **kw)
        self.main_frame = main_frame

        self.session_char_xp_start = 0
        self.session_char_xp = 0
        self.session_char_time_start = time.time()
        self.session_char_xp_missing = 0
        self.avg_run = 0
        self.session_xp_runs = set()

        # ==================================== WIDGETS ==================================== #
        tkd.Label(self, text='Advanced stats tracker', font='Helvetica 15').pack()

        lf1 = tkd.LabelFrame(self)
        lf1.pack(expand=False, fill=tk.X, padx=1)
        self.name_sv = self.create_row('Name', lf=lf1, default_val='-----')
        self.level_sv = self.create_row('Level', lf=lf1, default_val='-----')
        self.mf_sv = self.create_row('MF', lf=lf1, default_val='-----')
        self.players_x_sv = self.create_row('Players X', lf=lf1, default_val='-----')

        lf2 = tkd.LabelFrame(self)
        lf2.pack(expand=False, fill=tk.X, padx=1, pady=8)
        self.exp_sv = self.create_row('Exp %', lf=lf2)
        self.exp_session_sv = self.create_row('Exp (session)', lf=lf2)
        self.exp_run_sv = self.create_row('Exp (run)', lf=lf2)
        self.exp_hour_sv = self.create_row('Exp / hour', lf=lf2)

        lf3 = tkd.LabelFrame(self)
        lf3.pack(expand=False, fill=tk.X, padx=1)
        self.exp_level_sv = self.create_row('Exp to level', lf=lf3)
        self.hours_level_sv = self.create_row('Time to level', lf=lf3)
        self.runs_level_sv = self.create_row('Runs to level', lf=lf3)
        # ==================================== WIDGETS ==================================== #

        color_themes.Theme(main_frame.active_theme).update_colors()

    @staticmethod
    def create_row(var_name, lf, default_val='0'):
        fr = tkd.Frame(lf, height=22, width=236)
        fr.propagate(False)
        fr.pack(expand=False, fill=tk.X)

        sv = tk.StringVar(fr, value=default_val)
        tkd.Label(fr, text='%s:' % var_name, font='helvetica 10', anchor=tk.W, justify=tk.LEFT).pack(side=tk.LEFT)
        tkd.Label(fr, textvariable=sv, font='helvetica 12 bold', anchor=tk.E, justify=tk.RIGHT).pack(side=tk.RIGHT)

        return sv

    def update_loop(self):
        self._update_vars()
        self.after_updater = self.after(600, self.update_loop)

    def _update_vars(self):
        try:
            player_unit_stats = self.main_frame.d2_reader.player_unit_stats()
        except other_utils.pymem_err_list as e:

            # Update time dependent variables when outside a game instance (in menu for example)
            xp_hour_session = 3600 * (self.session_char_xp - self.session_char_xp_start) / (time.time() + 0.0001 - self.session_char_time_start)
            self.exp_hour_sv.set('{:,.0f}'.format(xp_hour_session))
            self.hours_level_sv.set(self.format_time(self.session_char_xp_missing / xp_hour_session) if xp_hour_session > 0 else '0')

            # My horrible way of determining whether a run has ended. Should be done in a better way for sure..
            if hasattr(self, 'curr_run_xp') and self.session_char_xp > self.curr_run_xp:
                self.session_xp_runs.add(self.session_char_xp - self.curr_run_xp)
                self.avg_run = sum(self.session_xp_runs) / len(self.session_xp_runs)
                self.runs_level_sv.set('{:.0f}'.format(-(-self.session_char_xp_missing/self.avg_run//1)))
            self.curr_run_xp = self.session_char_xp
            self.exp_run_sv.set('0')
            return

        # Game has not loaded PlayerUnitStats yet (new created characters don't have the XP stat, so need an exception)
        if player_unit_stats['Exp'] == -1 and player_unit_stats['Level'] != 1:
            return

        if not hasattr(self, 'curr_run_xp'):
            self.curr_run_xp = player_unit_stats['Exp']

        # Assign variables at first load of character
        if self.name_sv.get() == '-----' and self.session_char_xp_start == 0:
            self.session_char_xp_start = player_unit_stats['Exp']
            self.session_char_time_start = time.time()
            self.curr_run_xp = self.session_char_xp_start

        self.name_sv.set(player_unit_stats['Name'])
        self.level_sv.set(player_unit_stats['Level'])
        if player_unit_stats['MF'] >= 0:
            self.mf_sv.set(str(player_unit_stats['MF']) + '%')
        self.players_x_sv.set(player_unit_stats['Players X'])

        self.exp_sv.set('{0:.1f}%'.format(player_unit_stats['Exp %']*100))

        self.session_char_xp = player_unit_stats['Exp']
        self.exp_session_sv.set('{:,.0f}'.format(self.session_char_xp - self.session_char_xp_start))

        xp_hour_session = 3600 * (self.session_char_xp - self.session_char_xp_start) / (time.time() + 0.0001 - self.session_char_time_start)
        self.exp_hour_sv.set('{:,.0f}'.format(xp_hour_session))
        self.exp_run_sv.set('{:,.0f}'.format(self.session_char_xp - self.curr_run_xp))

        self.session_char_xp_missing = player_unit_stats['Exp missing']
        self.exp_level_sv.set('{:,.0f}'.format(self.session_char_xp_missing))
        self.hours_level_sv.set(self.format_time(self.session_char_xp_missing / xp_hour_session) if xp_hour_session > 0 else '0')
        if len(self.session_xp_runs) > 0:
            self.runs_level_sv.set('{:.0f}'.format(-(-self.session_char_xp_missing / self.avg_run // 1)))

    def reset_when_changes(self, player_unit_stats):
        if player_unit_stats['Name'] != self.name_sv.get() or str(player_unit_stats['Level']) != self.level_sv.get():
            self.session_char_xp_start = player_unit_stats['Exp']
            self.session_char_time_start = time.time()
            self.curr_run_xp = self.session_char_xp_start
            self.session_xp_runs = set()
            self.runs_level_sv.set('0')

    def reset_session(self):
        self.session_char_xp_start = 0
        self.session_char_xp = 0
        self.session_char_time_start = time.time()
        self.session_char_xp_missing = 0
        self.session_xp_runs = set()
        if hasattr(self, 'curr_run_xp'):
            delattr(self, 'curr_run_xp')

        self.name_sv.set('-----')
        self.level_sv.set('-----')
        self.mf_sv.set('-----')
        self.players_x_sv.set('-----')

        self.exp_sv.set('0')
        self.exp_session_sv.set('0')
        self.exp_run_sv.set('0')
        self.exp_hour_sv.set('0')

        self.exp_level_sv.set('0')
        self.hours_level_sv.set('0')
        self.runs_level_sv.set('0')

    def save_state(self):
        return dict(session_char_xp_start=self.session_char_xp_start,
                    session_char_xp=self.session_char_xp,
                    session_char_time_start=self.session_char_time_start,
                    session_char_xp_missing=self.session_char_xp_missing,
                    session_xp_runs=list(self.session_xp_runs))

    def load_from_state(self, active_state):
        self.session_char_xp_start = active_state.get('session_char_xp_start', 0)
        self.session_char_xp = active_state.get('session_char_xp', 0)
        self.session_char_time_start = active_state.get('session_char_time_start', time.time())
        self.session_char_xp_missing = active_state.get('session_char_xp_missing', 0)
        self.session_xp_runs = set(active_state.get('session_xp_runs', set()))

        if self.session_char_xp > 0:
            self.curr_run_xp = self.session_char_xp

        self.name_sv.set('-----')
        self.level_sv.set('-----')
        self.mf_sv.set('-----')
        self.players_x_sv.set('-----')

        self.exp_level_sv.set('{:,.0f}'.format(self.session_char_xp_missing))
        self.exp_session_sv.set('{:,.0f}'.format(self.session_char_xp - self.session_char_xp_start))
        if len(self.session_xp_runs) > 0:
            self.avg_run = sum(self.session_xp_runs) / len(self.session_xp_runs)
            self.runs_level_sv.set('{:.0f}'.format(-(-self.session_char_xp_missing / self.avg_run // 1)))
        else:
            self.runs_level_sv.set('0')

    @staticmethod
    def format_time(hours):
        h = hours // 1
        m = int(round((hours % 1)*60))
        return '%02dh:%02dm' % (h, m)

    def destroy(self):
        self.after_cancel(self.after_updater)
        tkd.Frame.destroy(self)
