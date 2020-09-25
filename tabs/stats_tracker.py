from utils import tk_dynamic as tkd, color_themes, other_utils
import tkinter as tk
import time


class StatsTracker(tkd.Frame):
    def __init__(self, main_frame, **kw):
        tkd.Frame.__init__(self, main_frame.root, **kw)
        self.main_frame = main_frame

        self.session_char_xp_start = 0
        self.session_char_xp = 0
        self.session_char_xp_diff = 0
        self.session_char_time_start = 0
        self.session_char_xp_missing = 0
        self.xp_hour_session = 0
        self.xp_runs = set()

        # ==================================== WIDGETS ==================================== #
        tkd.Label(self, text='Advanced stats tracker', font='Helvetica 15').pack()

        lf1 = tkd.LabelFrame(self)
        lf1.pack(expand=False, fill=tk.X, padx=1)
        self.name_sv = self.create_row('Name', lf=lf1)
        self.level_sv = self.create_row('Level', lf=lf1)
        self.mf_sv = self.create_row('MF', lf=lf1)
        self.players_x_sv = self.create_row('Players X', lf=lf1)

        lf2 = tkd.LabelFrame(self)
        lf2.pack(expand=False, fill=tk.X, padx=1, pady=8)
        self.exp_sv = self.create_row('Exp %', lf=lf2)
        self.exp_session_sv = self.create_row('Exp (session)', lf=lf2, default_val='0')
        self.exp_run_sv = self.create_row('Exp (run)', lf=lf2, default_val='0')
        self.exp_hour_sv = self.create_row('Exp / hour', lf=lf2, default_val='0')

        lf3 = tkd.LabelFrame(self)
        lf3.pack(expand=False, fill=tk.X, padx=1)
        self.exp_level_sv = self.create_row('Exp to level', lf=lf3)
        self.hours_level_sv = self.create_row('Time to level', lf=lf3)
        self.runs_level_sv = self.create_row('Runs to level', lf=lf3)
        # ==================================== WIDGETS ==================================== #

        color_themes.Theme(main_frame.active_theme).update_colors()

    @staticmethod
    def create_row(var_name, lf, default_val='-----'):
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
            self.xp_hour_session = 3600 * self.session_char_xp_diff / (time.time() + 0.0001 - self.session_char_time_start)
            self.exp_hour_sv.set('{:,.0f}'.format(self.xp_hour_session))
            self.hours_level_sv.set(self.format_time(self.session_char_xp_missing / self.xp_hour_session) if self.xp_hour_session > 0 else '-----')

            # My horrible way of determining whether a run has ended. Should be done in a better way for sure..
            if hasattr(self, 'curr_run_xp') and self.session_char_xp != self.curr_run_xp:
                self.xp_runs.add(self.session_char_xp - self.curr_run_xp)
                self.avg_run = sum(self.xp_runs)/len(self.xp_runs)
                self.runs_level_sv.set('{:.0f}'.format(-(-self.session_char_xp_missing/self.avg_run//1)))
            self.curr_run_xp = self.session_char_xp
            self.exp_run_sv.set('0')
            return

        # Game has not loaded PlayerUnitStats yet (new created characters don't have the XP stat, so need an exception)
        if player_unit_stats['Exp'] == -1 and player_unit_stats['Level'] != 1:
            return

        if not hasattr(self, 'curr_run_xp'):
            self.curr_run_xp = player_unit_stats['Exp']

        # Resets stats when changing character or levelling up - Needs to be changed if synced with profile
        if player_unit_stats['Name'] != self.name_sv.get() or str(player_unit_stats['Level']) != self.level_sv.get():
            self.session_char_xp_start = player_unit_stats['Exp']
            self.session_char_time_start = time.time()
            self.curr_run_xp = self.session_char_xp_start
            self.name_sv.set(player_unit_stats['Name'])
            self.xp_runs = set()
            self.runs_level_sv.set('-----')
        self.level_sv.set(player_unit_stats['Level'])
        if player_unit_stats['MF'] >= 0:
            self.mf_sv.set(str(player_unit_stats['MF']) + '%')
        self.players_x_sv.set(player_unit_stats['Players X'])

        self.exp_sv.set('{0:.1f}%'.format(player_unit_stats['Exp %']*100))

        self.session_char_xp = player_unit_stats['Exp']
        self.session_char_xp_diff = self.session_char_xp - self.session_char_xp_start
        self.exp_session_sv.set('{:,.0f}'.format(self.session_char_xp_diff))

        self.xp_hour_session = 3600 * self.session_char_xp_diff / (time.time() + 0.0001 - self.session_char_time_start)
        self.exp_hour_sv.set('{:,.0f}'.format(self.xp_hour_session))
        self.exp_run_sv.set('{:,.0f}'.format(self.session_char_xp - self.curr_run_xp))

        self.session_char_xp_missing = player_unit_stats['Exp missing']
        self.exp_level_sv.set('{:,.0f}'.format(self.session_char_xp_missing))
        self.hours_level_sv.set(self.format_time(self.session_char_xp_missing / self.xp_hour_session) if self.xp_hour_session > 0 else '-----')
        if hasattr(self, 'avg_run'):
            self.runs_level_sv.set('{:.0f}'.format(-(-self.session_char_xp_missing / self.avg_run // 1)))

    @staticmethod
    def format_time(hours):
        h = hours // 1
        m = int(round((hours % 1)*60))
        return '%02dh:%02dm' % (h, m)

    def destroy(self):
        self.after_cancel(self.after_updater)
        tkd.Frame.destroy(self)
